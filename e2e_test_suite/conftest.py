import os
import uuid
import pytest
from google.cloud import pubsub_v1, bigquery
from google.api_core import exceptions
from dotenv import load_dotenv

load_dotenv()


# --- Configuration ---
try:
    GCP_PROJECT_ID = os.environ["GCP_PROJECT_ID"]
    GCP_REGION = os.environ["GCP_REGION"]
except KeyError:
    pytest.fail("GCP_PROJECT_ID and GCP_REGION environment variables must be set for integration tests.")

# --- Helper Fixture for Unique Naming ---

@pytest.fixture(scope="session")
def unique_id() -> str:
    """Generates a unique ID suffix for a test session."""
    return str(uuid.uuid4()).replace("-", "")

# --- Pub/Sub Fixture ---

@pytest.fixture(scope="session")
def pubsub_resources(unique_id: str):
    """
    Provisions a temporary Pub/Sub topic and subscription for a test session.

    Yields:
        tuple: A tuple containing the fully-qualified topic name and subscription name.
    """
    publisher_client = pubsub_v1.PublisherClient()
    subscriber_client = pubsub_v1.SubscriberClient()

    topic_id = f"e2e-test-topic-{unique_id}"
    subscription_id = f"e2e-test-sub-{unique_id}"

    topic_path = publisher_client.topic_path(GCP_PROJECT_ID, topic_id)
    subscription_path = subscriber_client.subscription_path(GCP_PROJECT_ID, subscription_id)

    print(f"Creating Pub/Sub topic: {topic_path}")
    try:
        publisher_client.create_topic(name=topic_path)
    except exceptions.AlreadyExists:
        print(f"Topic {topic_path} already exists.")


    print(f"Creating Pub/Sub subscription: {subscription_path}")
    try:
        subscriber_client.create_subscription(name=subscription_path, topic=topic_path)
    except exceptions.AlreadyExists:
        print(f"Subscription {subscription_path} already exists.")

    yield topic_path, subscription_path

    # --- Teardown ---
    print(f"Deleting Pub/Sub subscription: {subscription_path}")
    try:
        subscriber_client.delete_subscription(subscription=subscription_path)
    except exceptions.NotFound:
        print(f"Subscription {subscription_path} not found, skipping deletion.")
    except Exception as e:
        print(f"Error deleting subscription {subscription_path}: {e}")

    print(f"Deleting Pub/Sub topic: {topic_path}")
    try:
        publisher_client.delete_topic(topic=topic_path)
    except exceptions.NotFound:
        print(f"Topic {topic_path} not found, skipping deletion.")
    except Exception as e:
        print(f"Error deleting topic {topic_path}: {e}")


# --- BigQuery Fixture ---

@pytest.fixture(scope="session")
def bigquery_resources(unique_id: str):
    """
    Provisions a temporary BigQuery dataset with main and dead-letter tables.

    Yields:
        tuple: A tuple containing the fully-qualified table IDs for the main
               and dead-letter tables.
    """
    bigquery_client = bigquery.Client(project=GCP_PROJECT_ID)

    dataset_id = f"e2e_test_dataset_{unique_id}"
    dataset_path = f"{GCP_PROJECT_ID}.{dataset_id}"
    main_table_id = f"{dataset_path}.main_events"
    dead_letter_table_id = f"{dataset_path}.dead_letter"

    print(f"Creating BigQuery dataset: {dataset_path}")
    dataset = bigquery.Dataset(dataset_path)
    dataset.location = GCP_REGION
    try:
        bigquery_client.create_dataset(dataset, timeout=30)
    except exceptions.Conflict:
        print(f"Dataset {dataset_path} already exists.")


    # Define schemas
    main_table_schema = [
        bigquery.SchemaField("event_id", "STRING"),
        bigquery.SchemaField("user_id", "INTEGER"),
        bigquery.SchemaField("event_timestamp", "DATETIME"),
        bigquery.SchemaField("processing_timestamp", "DATETIME"),
    ]
    dead_letter_schema = [
        bigquery.SchemaField("raw_payload", "STRING"),
        bigquery.SchemaField("error_message", "STRING"),
        bigquery.SchemaField("timestamp", "TIMESTAMP"),
    ]

    # Create tables
    print(f"Creating BigQuery main table: {main_table_id}")
    main_table = bigquery.Table(main_table_id, schema=main_table_schema)
    try:
        bigquery_client.create_table(main_table)
    except exceptions.Conflict:
        print(f"Table {main_table_id} already exists.")


    print(f"Creating BigQuery dead-letter table: {dead_letter_table_id}")
    dead_letter_table = bigquery.Table(dead_letter_table_id, schema=dead_letter_schema)
    try:
        bigquery_client.create_table(dead_letter_table)
    except exceptions.Conflict:
        print(f"Table {dead_letter_table_id} already exists.")


    yield main_table_id, dead_letter_table_id

    # --- Teardown ---
    print(f"Deleting BigQuery dataset: {dataset_path}")
    try:
        bigquery_client.delete_dataset(
            dataset_path, delete_contents=True, not_found_ok=True
        )
    except Exception as e:
        print(f"Error deleting dataset {dataset_path}: {e}")