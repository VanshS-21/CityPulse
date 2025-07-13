"""
Comprehensive tests for the enhanced CityPulse configuration system.
Tests the new Pydantic-based configuration with validation and type safety.
"""

import os
import pytest
from unittest.mock import patch, MagicMock
from pathlib import Path
from pydantic import ValidationError

# Import the enhanced configuration classes
import sys
sys.path.append('server')

from shared_config import (
    Environment,
    DatabaseConfig,
    FirestoreCollections,
    PubSubConfig,
    StorageConfig,
    APIConfig,
    DataPipelineConfig,
    AIConfig,
    CityPulseConfig,
    get_config,
    reset_config,
    validate_environment_config,
    get_config_summary
)


class TestEnvironmentEnum:
    """Test the Environment enumeration."""
    
    def test_environment_values(self):
        """Test that all environment values are correct."""
        assert Environment.DEVELOPMENT == "development"
        assert Environment.STAGING == "staging"
        assert Environment.PRODUCTION == "production"
    
    def test_environment_from_string(self):
        """Test creating Environment from string."""
        assert Environment("development") == Environment.DEVELOPMENT
        assert Environment("staging") == Environment.STAGING
        assert Environment("production") == Environment.PRODUCTION
    
    def test_invalid_environment(self):
        """Test that invalid environment raises ValueError."""
        with pytest.raises(ValueError):
            Environment("invalid")


class TestDatabaseConfig:
    """Test the DatabaseConfig class."""
    
    def test_valid_database_config(self):
        """Test creating a valid database configuration."""
        config = DatabaseConfig(project_id="test-project-123")
        assert config.project_id == "test-project-123"
        assert config.firestore_database == "(default)"
        assert config.bigquery_dataset == "citypulse_analytics"
        assert config.credentials_path is None
    
    def test_database_config_with_custom_values(self):
        """Test database configuration with custom values."""
        config = DatabaseConfig(
            project_id="custom-project",
            firestore_database="custom-db",
            bigquery_dataset="custom_dataset",
            credentials_path="/path/to/creds.json"
        )
        assert config.project_id == "custom-project"
        assert config.firestore_database == "custom-db"
        assert config.bigquery_dataset == "custom_dataset"
        assert config.credentials_path == "/path/to/creds.json"
    
    def test_invalid_project_id(self):
        """Test that invalid project IDs raise ValidationError."""
        with pytest.raises(ValidationError):
            DatabaseConfig(project_id="")
        
        with pytest.raises(ValidationError):
            DatabaseConfig(project_id="ab")  # Too short
        
        with pytest.raises(ValidationError):
            DatabaseConfig(project_id="invalid@project")  # Invalid characters
    
    def test_invalid_bigquery_dataset(self):
        """Test that invalid BigQuery dataset names raise ValidationError."""
        with pytest.raises(ValidationError):
            DatabaseConfig(
                project_id="test-project",
                bigquery_dataset="invalid-dataset"  # Hyphens not allowed
            )
    
    def test_bigquery_table_properties(self):
        """Test BigQuery table name properties."""
        config = DatabaseConfig(project_id="test-project")
        assert config.bigquery_events_table == "citypulse_analytics.events"
        assert config.bigquery_users_table == "citypulse_analytics.users"
        assert config.bigquery_feedback_table == "citypulse_analytics.feedback"
    
    def test_environment_variables(self):
        """Test that environment variables are properly loaded."""
        with patch.dict(os.environ, {
            'DB_PROJECT_ID': 'env-project',
            'DB_FIRESTORE_DATABASE': 'env-db',
            'DB_BIGQUERY_DATASET': 'env_dataset'
        }):
            config = DatabaseConfig()
            assert config.project_id == 'env-project'
            assert config.firestore_database == 'env-db'
            assert config.bigquery_dataset == 'env_dataset'


class TestFirestoreCollections:
    """Test the FirestoreCollections class."""
    
    def test_default_collections(self):
        """Test default collection names."""
        collections = FirestoreCollections()
        assert collections.events == "events"
        assert collections.users == "users"
        assert collections.feedback == "feedback"
        assert collections.user_profiles == "user_profiles"
    
    def test_custom_collections(self):
        """Test custom collection names."""
        collections = FirestoreCollections(
            events="custom_events",
            users="custom_users",
            feedback="custom_feedback",
            user_profiles="custom_profiles"
        )
        assert collections.events == "custom_events"
        assert collections.users == "custom_users"
        assert collections.feedback == "custom_feedback"
        assert collections.user_profiles == "custom_profiles"
    
    def test_invalid_collection_names(self):
        """Test that invalid collection names raise ValidationError."""
        with pytest.raises(ValidationError):
            FirestoreCollections(events="")  # Empty string
        
        with pytest.raises(ValidationError):
            FirestoreCollections(events="invalid-collection")  # Hyphens not allowed
    
    def test_environment_variables(self):
        """Test that environment variables are properly loaded."""
        with patch.dict(os.environ, {
            'COLLECTION_EVENTS': 'env_events',
            'COLLECTION_USERS': 'env_users'
        }):
            collections = FirestoreCollections()
            assert collections.events == 'env_events'
            assert collections.users == 'env_users'


class TestAPIConfig:
    """Test the APIConfig class."""
    
    def test_default_api_config(self):
        """Test default API configuration."""
        config = APIConfig()
        assert config.host == "0.0.0.0"
        assert config.port == 8000
        assert config.debug is False
        assert "http://localhost:3000" in config.cors_origins
        assert config.max_request_size == 10 * 1024 * 1024
        assert config.rate_limit_per_minute == 100
    
    def test_custom_api_config(self):
        """Test custom API configuration."""
        config = APIConfig(
            host="127.0.0.1",
            port=9000,
            debug=True,
            cors_origins=["https://example.com"],
            max_request_size=5 * 1024 * 1024,
            rate_limit_per_minute=200
        )
        assert config.host == "127.0.0.1"
        assert config.port == 9000
        assert config.debug is True
        assert config.cors_origins == ["https://example.com"]
        assert config.max_request_size == 5 * 1024 * 1024
        assert config.rate_limit_per_minute == 200
    
    def test_invalid_port(self):
        """Test that invalid ports raise ValidationError."""
        with pytest.raises(ValidationError):
            APIConfig(port=0)  # Too low
        
        with pytest.raises(ValidationError):
            APIConfig(port=70000)  # Too high
    
    def test_invalid_cors_origins(self):
        """Test that invalid CORS origins raise ValidationError."""
        with pytest.raises(ValidationError):
            APIConfig(cors_origins="not a list")
        
        with pytest.raises(ValidationError):
            APIConfig(cors_origins=["", "valid.com"])  # Empty string in list


class TestCityPulseConfig:
    """Test the main CityPulseConfig class."""
    
    def setup_method(self):
        """Reset configuration before each test."""
        reset_config()
    
    def test_default_config(self):
        """Test default configuration creation."""
        config = CityPulseConfig(project_id="test-project")
        assert config.environment == Environment.DEVELOPMENT
        assert config.project_id == "test-project"
        assert config.region == "us-central1"
        assert isinstance(config.database, DatabaseConfig)
        assert isinstance(config.api, APIConfig)
        assert isinstance(config.collections, FirestoreCollections)
    
    def test_production_config(self):
        """Test production configuration."""
        config = CityPulseConfig(
            environment=Environment.PRODUCTION,
            project_id="prod-project"
        )
        assert config.environment == Environment.PRODUCTION
        assert config.project_id == "prod-project"
    
    def test_environment_from_env_var(self):
        """Test environment loading from environment variable."""
        with patch.dict(os.environ, {'CITYPULSE_ENV': 'staging'}):
            config = CityPulseConfig(project_id="test-project")
            assert config.environment == Environment.STAGING
    
    def test_invalid_environment_from_env_var(self):
        """Test handling of invalid environment from env var."""
        with patch.dict(os.environ, {'CITYPULSE_ENV': 'invalid'}):
            config = CityPulseConfig(project_id="test-project")
            # Should default to development with warning
            assert config.environment == Environment.DEVELOPMENT
    
    def test_nested_config_initialization(self):
        """Test that nested configurations are properly initialized."""
        config = CityPulseConfig(project_id="test-project")
        
        # All nested configs should have the same project_id
        assert config.database.project_id == "test-project"
        assert config.pubsub.project_id == "test-project"
        assert config.storage.project_id == "test-project"
        assert config.pipeline.project_id == "test-project"
        assert config.ai.project_id == "test-project"
    
    def test_config_validation(self):
        """Test configuration validation."""
        config = CityPulseConfig(project_id="test-project")
        assert config.validate_configuration() is True
    
    def test_config_to_dict(self):
        """Test configuration serialization to dictionary."""
        config = CityPulseConfig(project_id="test-project")
        config_dict = config.to_dict()
        
        assert config_dict["environment"] == "development"
        assert config_dict["project_id"] == "test-project"
        assert "database" in config_dict
        assert "api" in config_dict
        assert "collections" in config_dict
    
    def test_utility_methods(self):
        """Test utility methods."""
        config = CityPulseConfig(project_id="test-project")
        
        database_url = config.get_database_url()
        assert database_url == "firestore://test-project/(default)"
        
        dataset_id = config.get_bigquery_dataset_id()
        assert dataset_id == "test-project.citypulse_analytics"
    
    @patch('shared_config.Path')
    def test_get_credentials_path(self, mock_path):
        """Test credentials path resolution."""
        config = CityPulseConfig(project_id="test-project")
        
        # Mock Path.exists() to return True for specific paths
        mock_path.return_value.exists.return_value = True
        
        with patch.dict(os.environ, {'GOOGLE_APPLICATION_CREDENTIALS': '/path/to/creds.json'}):
            creds_path = config.get_credentials_path()
            assert creds_path == '/path/to/creds.json'


class TestGlobalConfigFunctions:
    """Test global configuration functions."""
    
    def setup_method(self):
        """Reset configuration before each test."""
        reset_config()
    
    def test_get_config(self):
        """Test getting global configuration instance."""
        with patch.dict(os.environ, {'GOOGLE_CLOUD_PROJECT': 'test-project'}):
            config = get_config()
            assert isinstance(config, CityPulseConfig)
            assert config.project_id == 'test-project'
    
    def test_get_config_singleton(self):
        """Test that get_config returns the same instance."""
        with patch.dict(os.environ, {'GOOGLE_CLOUD_PROJECT': 'test-project'}):
            config1 = get_config()
            config2 = get_config()
            assert config1 is config2
    
    def test_get_config_force_reload(self):
        """Test force reloading configuration."""
        with patch.dict(os.environ, {'GOOGLE_CLOUD_PROJECT': 'test-project'}):
            config1 = get_config()
            config2 = get_config(force_reload=True)
            assert config1 is not config2
    
    def test_reset_config(self):
        """Test resetting global configuration."""
        with patch.dict(os.environ, {'GOOGLE_CLOUD_PROJECT': 'test-project'}):
            config1 = get_config()
            reset_config()
            config2 = get_config()
            assert config1 is not config2
    
    def test_validate_environment_config(self):
        """Test environment configuration validation."""
        with patch.dict(os.environ, {'GOOGLE_CLOUD_PROJECT': 'test-project'}):
            assert validate_environment_config("development") is True
            assert validate_environment_config("staging") is True
            assert validate_environment_config("production") is True
            assert validate_environment_config("invalid") is False
    
    def test_get_config_summary(self):
        """Test configuration summary."""
        with patch.dict(os.environ, {'GOOGLE_CLOUD_PROJECT': 'test-project'}):
            summary = get_config_summary()
            assert summary["environment"] == "development"
            assert summary["project_id"] == "test-project"
            assert "api_port" in summary
            assert "database_dataset" in summary


class TestConfigurationIntegration:
    """Integration tests for the configuration system."""
    
    def setup_method(self):
        """Reset configuration before each test."""
        reset_config()
    
    def test_full_configuration_with_env_vars(self):
        """Test full configuration loading with environment variables."""
        env_vars = {
            'CITYPULSE_ENV': 'staging',
            'GOOGLE_CLOUD_PROJECT': 'staging-project',
            'GOOGLE_CLOUD_REGION': 'us-west1',
            'DB_BIGQUERY_DATASET': 'staging_analytics',
            'API_PORT': '9000',
            'API_DEBUG': 'true',
            'PIPELINE_MAX_NUM_WORKERS': '20',
            'AI_MODEL_NAME': 'gemini-pro-staging'
        }
        
        with patch.dict(os.environ, env_vars):
            config = get_config()
            
            assert config.environment == Environment.STAGING
            assert config.project_id == 'staging-project'
            assert config.region == 'us-west1'
            assert config.database.bigquery_dataset == 'staging_analytics'
            assert config.api.port == 9000
            assert config.api.debug is True
            assert config.pipeline.max_num_workers == 20
            assert config.ai.model_name == 'gemini-pro-staging'
    
    def test_configuration_error_handling(self):
        """Test configuration error handling."""
        # Test with invalid project ID
        with pytest.raises(ValueError):
            CityPulseConfig(project_id="")
        
        # Test with invalid environment
        with patch.dict(os.environ, {'CITYPULSE_ENV': 'invalid'}):
            # Should not raise error but log warning and use default
            config = CityPulseConfig(project_id="test-project")
            assert config.environment == Environment.DEVELOPMENT
