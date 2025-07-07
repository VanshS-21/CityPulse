"""
End-to-end tests for CityPulse data pipeline.

This module tests the complete data flow from Pub/Sub ingestion
through Dataflow processing to BigQuery storage.
"""

import pytest
import time
import json
from typing import Dict, Any, List

from ..config.test_config import get_all_configs
from ..utils.gcp_helpers import (
    PubSubHelper, BigQueryHelper, DataflowHelper,
    generate_unique_resource_name, cleanup_all_test_resources
)
from ..utils.data_generators import (
    generate_citizen_report, generate_iot_data, 
    generate_batch_citizen_reports
)
from ..utils.test_helpers import (
    TestTimer, wait_for_condition, test_resource_cleanup,
    format_test_results
)


@pytest.fixture(scope="module")
def configs():
    """Get test configurations."""
    return get_all_configs()


@pytest.fixture(scope="function")
def test_helpers(configs):
    """Create test helper instances with automatic cleanup."""
    pubsub_helper = PubSubHelper(configs["gcp"].project_id)
    bigquery_helper = BigQueryHelper(
        configs["gcp"].project_id,
        configs["bigquery"].dataset_id
    )
    dataflow_helper = DataflowHelper(
        configs["gcp"].project_id,
        configs["gcp"].region
    )
    
    with test_resource_cleanup(pubsub_helper, bigquery_helper, dataflow_helper):
        yield {
            "pubsub": pubsub_helper,
            "bigquery": bigquery_helper,
            "dataflow": dataflow_helper
        }


class TestCompleteDataFlow:
    """Test complete data flow from source to destination."""
    
    def test_citizen_reports_end_to_end(self, test_helpers, configs):
        """Test complete citizen reports data flow."""
        results = {}
        
        # Step 1: Publish test data to production topic
        with TestTimer("publish test data") as timer:
            test_data = generate_batch_citizen_reports(5, valid_ratio=0.8)
            
            # Use production topic
            topic_name = configs["pubsub"].citizen_reports_topic
            publisher = test_helpers["pubsub"].publisher
            topic_path = publisher.topic_path(configs["gcp"].project_id, topic_name)
            
            message_ids = test_helpers["pubsub"].publish_messages(topic_path, test_data)
            
        results["publish_data"] = {
            "success": len(message_ids) == len(test_data),
            "duration": timer.duration,
            "message_count": len(message_ids)
        }
        
        # Step 2: Wait for pipeline processing
        with TestTimer("pipeline processing") as timer:
            # Wait for data to appear in BigQuery
            main_table_id = f"{configs['gcp'].project_id}.{configs['bigquery'].dataset_id}.{configs['bigquery'].events_table}"
            
            def check_data_processed():
                try:
                    # Check if our test data made it to BigQuery
                    query = f"""
                    SELECT COUNT(*) as count 
                    FROM `{main_table_id}` 
                    WHERE DATE(created_at) = CURRENT_DATE()
                    AND source = 'citizen_app'
                    """
                    result = list(test_helpers["bigquery"].client.query(query).result())
                    return result[0].count >= 4  # Expect at least 4 valid records
                except Exception:
                    return False
            
            data_processed = wait_for_condition(
                check_data_processed,
                timeout=300,  # 5 minutes
                check_interval=30,
                description="data processing in pipeline"
            )
            
        results["pipeline_processing"] = {
            "success": data_processed,
            "duration": timer.duration
        }
        
        # Step 3: Validate data in BigQuery
        with TestTimer("data validation") as timer:
            if data_processed:
                # Get processed data
                query = f"""
                SELECT event_id, title, description, category, severity, created_at
                FROM `{main_table_id}` 
                WHERE DATE(created_at) = CURRENT_DATE()
                AND source = 'citizen_app'
                ORDER BY created_at DESC
                LIMIT 10
                """
                
                processed_data = list(test_helpers["bigquery"].client.query(query).result())
                
                # Validate data structure
                validation_success = True
                for row in processed_data:
                    if not all([row.event_id, row.title, row.description, row.category]):
                        validation_success = False
                        break
                
                results["data_validation"] = {
                    "success": validation_success,
                    "duration": timer.duration,
                    "records_found": len(processed_data)
                }
            else:
                results["data_validation"] = {
                    "success": False,
                    "duration": timer.duration,
                    "error": "No data to validate"
                }
        
        # Step 4: Check error handling
        with TestTimer("error handling validation") as timer:
            dead_letter_table_id = f"{configs['gcp'].project_id}.{configs['bigquery'].dataset_id}.{configs['bigquery'].dead_letter_events_table}"
            
            try:
                query = f"""
                SELECT COUNT(*) as error_count 
                FROM `{dead_letter_table_id}` 
                WHERE DATE(timestamp) = CURRENT_DATE()
                """
                result = list(test_helpers["bigquery"].client.query(query).result())
                error_count = result[0].error_count
                
                # Should have some errors from invalid data
                error_handling_success = error_count >= 1
                
                results["error_handling"] = {
                    "success": error_handling_success,
                    "duration": timer.duration,
                    "error_count": error_count
                }
            except Exception as e:
                results["error_handling"] = {
                    "success": False,
                    "duration": timer.duration,
                    "error": str(e)
                }
        
        # Print results summary
        print("\n" + format_test_results(results))
        
        # Overall test success
        overall_success = all(result.get("success", False) for result in results.values())
        assert overall_success, f"E2E test failed. Results: {results}"
    
    def test_data_pipeline_performance(self, test_helpers, configs):
        """Test pipeline performance with larger dataset."""
        # Generate larger test dataset
        test_data = generate_batch_citizen_reports(50, valid_ratio=0.9)
        
        with TestTimer("large dataset processing") as timer:
            # Publish data
            topic_name = configs["pubsub"].citizen_reports_topic
            publisher = test_helpers["pubsub"].publisher
            topic_path = publisher.topic_path(configs["gcp"].project_id, topic_name)
            
            message_ids = test_helpers["pubsub"].publish_messages(topic_path, test_data)
            
            # Wait for processing
            main_table_id = f"{configs['gcp'].project_id}.{configs['bigquery'].dataset_id}.{configs['bigquery'].events_table}"
            
            def check_batch_processed():
                try:
                    query = f"""
                    SELECT COUNT(*) as count 
                    FROM `{main_table_id}` 
                    WHERE DATE(created_at) = CURRENT_DATE()
                    AND source = 'citizen_app'
                    """
                    result = list(test_helpers["bigquery"].client.query(query).result())
                    return result[0].count >= 45  # Expect at least 45 valid records
                except Exception:
                    return False
            
            batch_processed = wait_for_condition(
                check_batch_processed,
                timeout=600,  # 10 minutes for larger dataset
                check_interval=30,
                description="batch data processing"
            )
        
        # Performance assertions
        assert batch_processed, "Large dataset was not processed within timeout"
        assert timer.duration < 600, f"Processing took too long: {timer.duration}s"
        
        # Calculate throughput
        throughput = len(test_data) / timer.duration
        print(f"Processing throughput: {throughput:.2f} messages/second")
        
        # Reasonable throughput expectation
        assert throughput > 0.1, f"Throughput too low: {throughput} messages/second"


class TestDataConsistency:
    """Test data consistency across the pipeline."""
    
    def test_data_integrity_validation(self, test_helpers, configs):
        """Test that data maintains integrity through the pipeline."""
        # Generate test data with known values
        test_event = generate_citizen_report(
            event_id="e2e-test-integrity-123",
            title="E2E Test Event",
            description="This is a test event for data integrity validation",
            category="Infrastructure",
            severity="medium"
        )
        
        # Publish single test event
        topic_name = configs["pubsub"].citizen_reports_topic
        publisher = test_helpers["pubsub"].publisher
        topic_path = publisher.topic_path(configs["gcp"].project_id, topic_name)
        
        message_ids = test_helpers["pubsub"].publish_messages(topic_path, [test_event])
        assert len(message_ids) == 1
        
        # Wait for processing and retrieve data
        main_table_id = f"{configs['gcp'].project_id}.{configs['bigquery'].dataset_id}.{configs['bigquery'].events_table}"
        
        def check_specific_event():
            try:
                query = f"""
                SELECT * FROM `{main_table_id}` 
                WHERE event_id = 'e2e-test-integrity-123'
                """
                result = list(test_helpers["bigquery"].client.query(query).result())
                return len(result) > 0
            except Exception:
                return False
        
        event_processed = wait_for_condition(
            check_specific_event,
            timeout=300,
            check_interval=15,
            description="specific test event processing"
        )
        
        assert event_processed, "Test event was not processed"
        
        # Retrieve and validate the processed event
        query = f"""
        SELECT event_id, title, description, category, severity
        FROM `{main_table_id}` 
        WHERE event_id = 'e2e-test-integrity-123'
        """
        
        result = list(test_helpers["bigquery"].client.query(query).result())
        assert len(result) == 1
        
        processed_event = result[0]
        
        # Validate data integrity
        assert processed_event.event_id == test_event["event_id"]
        assert processed_event.title == test_event["title"]
        assert processed_event.description == test_event["description"]
        assert processed_event.category == test_event["category"]
        assert processed_event.severity == test_event["severity"]
    
    def test_duplicate_handling(self, test_helpers, configs):
        """Test handling of duplicate events."""
        # Generate duplicate events
        base_event = generate_citizen_report(
            event_id="e2e-test-duplicate-456",
            title="Duplicate Test Event"
        )
        
        duplicate_events = [base_event.copy() for _ in range(3)]
        
        # Publish duplicates
        topic_name = configs["pubsub"].citizen_reports_topic
        publisher = test_helpers["pubsub"].publisher
        topic_path = publisher.topic_path(configs["gcp"].project_id, topic_name)
        
        message_ids = test_helpers["pubsub"].publish_messages(topic_path, duplicate_events)
        assert len(message_ids) == 3
        
        # Wait for processing
        time.sleep(120)  # Wait 2 minutes for processing
        
        # Check how many records were created
        main_table_id = f"{configs['gcp'].project_id}.{configs['bigquery'].dataset_id}.{configs['bigquery'].events_table}"
        
        query = f"""
        SELECT COUNT(*) as count
        FROM `{main_table_id}` 
        WHERE event_id = 'e2e-test-duplicate-456'
        """
        
        result = list(test_helpers["bigquery"].client.query(query).result())
        duplicate_count = result[0].count
        
        print(f"Duplicate events processed: {duplicate_count}")
        
        # The pipeline might handle duplicates differently
        # This test documents the current behavior
        assert duplicate_count >= 1, "At least one duplicate should be processed"
