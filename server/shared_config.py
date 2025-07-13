"""
Centralized configuration management for CityPulse.

This module provides a unified configuration system that can be used across
all components of the CityPulse platform (API, data models, pipelines, etc.).
Enhanced with Pydantic for type safety and validation.
"""

import os
from typing import Optional, Dict, Any, List
from dataclasses import dataclass
from pathlib import Path
from enum import Enum
from pydantic import BaseModel, field_validator, Field, ConfigDict
from pydantic_settings import BaseSettings
import logging

logger = logging.getLogger(__name__)


class Environment(str, Enum):
    """Environment enumeration for type safety."""
    DEVELOPMENT = "development"
    STAGING = "staging"
    PRODUCTION = "production"


class DatabaseConfig(BaseSettings):
    """Database configuration settings with validation."""
    project_id: str = Field(..., min_length=3, description="Google Cloud Project ID")
    firestore_database: str = Field(default="(default)", description="Firestore database name")
    bigquery_dataset: str = Field(default="citypulse_analytics", description="BigQuery dataset name")
    credentials_path: Optional[str] = Field(default=None, description="Path to service account credentials")

    @field_validator('project_id')
    @classmethod
    def validate_project_id(cls, v):
        if not v or len(v) < 3:
            raise ValueError('Project ID must be at least 3 characters long')
        if not v.replace('-', '').replace('_', '').isalnum():
            raise ValueError('Project ID must contain only alphanumeric characters, hyphens, and underscores')
        return v

    @field_validator('bigquery_dataset')
    @classmethod
    def validate_bigquery_dataset(cls, v):
        if not v.replace('_', '').isalnum():
            raise ValueError('BigQuery dataset name must contain only alphanumeric characters and underscores')
        return v

    @property
    def bigquery_events_table(self) -> str:
        return f"{self.bigquery_dataset}.events"

    @property
    def bigquery_users_table(self) -> str:
        return f"{self.bigquery_dataset}.users"

    @property
    def bigquery_feedback_table(self) -> str:
        return f"{self.bigquery_dataset}.feedback"

    model_config = ConfigDict(env_prefix="DB_")


class FirestoreCollections(BaseSettings):
    """Firestore collection names with validation."""
    events: str = Field(default="events", description="Events collection name")
    users: str = Field(default="users", description="Users collection name")
    feedback: str = Field(default="feedback", description="Feedback collection name")
    user_profiles: str = Field(default="user_profiles", description="User profiles collection name")

    @field_validator('events', 'users', 'feedback', 'user_profiles')
    @classmethod
    def validate_collection_names(cls, v):
        if not v or not isinstance(v, str):
            raise ValueError('Collection names must be non-empty strings')
        if not v.replace('_', '').isalnum():
            raise ValueError('Collection names must contain only alphanumeric characters and underscores')
        return v

    model_config = ConfigDict(env_prefix="COLLECTION_")


class PubSubConfig(BaseSettings):
    """Pub/Sub configuration settings with validation."""
    project_id: str = Field(..., min_length=3, description="Google Cloud Project ID")
    citizen_reports_topic: str = Field(default="citizen-reports", description="Citizen reports topic name")
    iot_data_topic: str = Field(default="iot-data", description="IoT data topic name")
    social_media_topic: str = Field(default="social-media-feeds", description="Social media feeds topic name")
    official_feeds_topic: str = Field(default="official-feeds", description="Official feeds topic name")
    dead_letter_topic: str = Field(default="dead-letter-queue", description="Dead letter topic name")

    @field_validator('citizen_reports_topic', 'iot_data_topic', 'social_media_topic', 'official_feeds_topic', 'dead_letter_topic')
    @classmethod
    def validate_pubsub_names(cls, v):
        if not v or not isinstance(v, str):
            raise ValueError('Topic names must be non-empty strings')
        if not v.replace('-', '').replace('_', '').isalnum():
            raise ValueError('Topic names must contain only alphanumeric characters, hyphens, and underscores')
        return v

    @property
    def citizen_reports_subscription(self) -> str:
        return f"{self.citizen_reports_topic}-subscription"

    @property
    def iot_data_subscription(self) -> str:
        return f"{self.iot_data_topic}-subscription"

    model_config = ConfigDict(env_prefix="PUBSUB_")


class StorageConfig(BaseSettings):
    """Cloud Storage configuration settings with validation."""
    project_id: str = Field(..., min_length=3, description="Google Cloud Project ID")
    temp_bucket: str = Field(default="temp", description="Temporary storage bucket suffix")
    staging_bucket: str = Field(default="staging", description="Staging storage bucket suffix")
    media_bucket: str = Field(default="media", description="Media storage bucket suffix")

    @field_validator('temp_bucket', 'staging_bucket', 'media_bucket')
    @classmethod
    def validate_bucket_names(cls, v):
        if not v or not isinstance(v, str):
            raise ValueError('Bucket names must be non-empty strings')
        if not v.replace('-', '').replace('_', '').isalnum():
            raise ValueError('Bucket names must contain only alphanumeric characters, hyphens, and underscores')
        return v

    def get_temp_bucket_name(self) -> str:
        return f"{self.project_id}-{self.temp_bucket}"

    def get_staging_bucket_name(self) -> str:
        return f"{self.project_id}-{self.staging_bucket}"

    def get_media_bucket_name(self) -> str:
        return f"{self.project_id}-{self.media_bucket}"

    model_config = ConfigDict(env_prefix="STORAGE_")


class APIConfig(BaseSettings):
    """API configuration settings with validation."""
    host: str = Field(default="0.0.0.0", description="API host address")
    port: int = Field(default=8000, ge=1, le=65535, description="API port number")
    debug: bool = Field(default=False, description="Debug mode flag")
    cors_origins: List[str] = Field(default_factory=lambda: ["http://localhost:3000", "https://citypulse.example.com"], description="CORS allowed origins")
    max_request_size: int = Field(default=10 * 1024 * 1024, ge=1024, description="Maximum request size in bytes")
    rate_limit_per_minute: int = Field(default=100, ge=1, description="Rate limit per minute")

    @field_validator('cors_origins')
    @classmethod
    def validate_cors_origins(cls, v):
        if not isinstance(v, list):
            raise ValueError('CORS origins must be a list')
        for origin in v:
            if not isinstance(origin, str) or not origin.strip():
                raise ValueError('Each CORS origin must be a non-empty string')
        return v

    model_config = ConfigDict(env_prefix="API_")


class DataPipelineConfig(BaseSettings):
    """Data pipeline configuration settings with validation."""
    project_id: str = Field(..., min_length=3, description="Google Cloud Project ID")
    region: str = Field(default="us-central1", description="Google Cloud region")
    temp_location: str = Field(default="", description="Temporary location for pipeline")
    staging_location: str = Field(default="", description="Staging location for pipeline")
    max_num_workers: int = Field(default=10, ge=1, le=1000, description="Maximum number of workers")
    machine_type: str = Field(default="n1-standard-1", description="Machine type for workers")

    @field_validator('region')
    @classmethod
    def validate_region(cls, v):
        # Basic validation for GCP region format
        if not v or not isinstance(v, str):
            raise ValueError('Region must be a non-empty string')
        return v

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Set default locations after initialization if not provided
        if not self.temp_location:
            self.temp_location = f"gs://{self.project_id}-temp"
        if not self.staging_location:
            self.staging_location = f"gs://{self.project_id}-staging"

    model_config = ConfigDict(env_prefix="PIPELINE_")


class AIConfig(BaseSettings):
    """AI/ML configuration settings with validation."""
    project_id: str = Field(..., min_length=3, description="Google Cloud Project ID")
    region: str = Field(default="us-central1", description="Google Cloud region")
    model_name: str = Field(default="gemini-pro", description="AI model name")
    vision_model_name: str = Field(default="gemini-pro-vision", description="Vision AI model name")
    max_tokens: int = Field(default=1000, ge=1, le=8192, description="Maximum tokens for AI responses")
    temperature: float = Field(default=0.7, ge=0.0, le=2.0, description="AI model temperature")

    # AI Prompts
    analysis_prompt: str = Field(
        default="""Analyze the following issue report from a citizen.
---
Description: {text_to_process}
---
1.  Summarize the issue in one sentence.
2.  Classify it into: [Pothole, Water Logging, Broken Streetlight,
    Garbage Dump, Traffic Jam, Public Safety, Other].
3.  If an image is provided, list key objects detected.
Return a JSON object with keys "summary", "category", "image_tags".""",
        description="AI analysis prompt template"
    )

    icon_prompt: str = Field(
        default="""A simple, modern, flat icon representing '{category}' for a city services app. Minimalist, vector style, on a white background.""",
        description="AI icon generation prompt template"
    )

    @field_validator('model_name', 'vision_model_name')
    @classmethod
    def validate_model_names(cls, v):
        if not v or not isinstance(v, str):
            raise ValueError('Model names must be non-empty strings')
        return v

    model_config = ConfigDict(env_prefix="AI_")


class CityPulseConfig(BaseSettings):
    """Main configuration class for CityPulse platform with enhanced validation."""

    environment: Environment = Field(default=Environment.DEVELOPMENT, description="Application environment")
    project_id: str = Field(..., min_length=3, description="Google Cloud Project ID")
    region: str = Field(default="us-central1", description="Google Cloud region")

    # Configuration sections - will be initialized in __init__
    database: Optional[DatabaseConfig] = Field(default=None, description="Database configuration")
    pubsub: Optional[PubSubConfig] = Field(default=None, description="Pub/Sub configuration")
    storage: Optional[StorageConfig] = Field(default=None, description="Storage configuration")
    api: Optional[APIConfig] = Field(default=None, description="API configuration")
    pipeline: Optional[DataPipelineConfig] = Field(default=None, description="Pipeline configuration")
    ai: Optional[AIConfig] = Field(default=None, description="AI configuration")
    collections: Optional[FirestoreCollections] = Field(default=None, description="Firestore collections")

    def __init__(self, **kwargs):
        """Initialize configuration with validation and environment-specific settings."""
        # Set environment from env var if not provided
        if 'environment' not in kwargs:
            env_str = os.getenv("CITYPULSE_ENV", "development")
            try:
                kwargs['environment'] = Environment(env_str)
            except ValueError:
                logger.warning(f"Invalid environment '{env_str}', defaulting to development")
                kwargs['environment'] = Environment.DEVELOPMENT

        # Set project_id from env var if not provided
        if 'project_id' not in kwargs:
            kwargs['project_id'] = os.getenv("GOOGLE_CLOUD_PROJECT", "citypulse-21")

        # Set region from env var if not provided
        if 'region' not in kwargs:
            kwargs['region'] = os.getenv("GOOGLE_CLOUD_REGION", "us-central1")

        super().__init__(**kwargs)

        # Initialize nested configurations with project context
        self._init_nested_configs()

    def _init_nested_configs(self):
        """Initialize nested configurations with project context."""
        # Initialize configurations with appropriate context
        self.database = DatabaseConfig(project_id=self.project_id)
        self.pubsub = PubSubConfig(project_id=self.project_id)
        self.storage = StorageConfig(project_id=self.project_id)
        self.api = APIConfig()
        self.pipeline = DataPipelineConfig(project_id=self.project_id, region=self.region)
        self.ai = AIConfig(project_id=self.project_id, region=self.region)
        self.collections = FirestoreCollections()

    model_config = ConfigDict(
        env_prefix="CITYPULSE_",
        env_nested_delimiter="__",
        case_sensitive=False
    )


    def get_credentials_path(self) -> Optional[str]:
        """Get the path to GCP credentials file."""
        # Check for explicit credentials path
        creds_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
        if creds_path and Path(creds_path).exists():
            return creds_path

        # Check for project-specific credentials
        project_creds = f"keys/{self.project_id}.json"
        if Path(project_creds).exists():
            return project_creds

        # Check for default credentials in keys directory
        default_creds = "keys/citypulse-21-90f84cb134a2.json"
        if Path(default_creds).exists():
            return default_creds

        # Return None to use default credentials (e.g., in GCP environments)
        return None

    def get_cors_origins_for_environment(self) -> List[str]:
        """Get CORS origins based on environment."""
        if self.environment == Environment.PRODUCTION:
            return [
                "https://citypulse.example.com",
                "https://www.citypulse.example.com",
                "https://api.citypulse.example.com"
            ]
        elif self.environment == Environment.STAGING:
            return [
                "https://staging.citypulse.example.com",
                "https://staging-api.citypulse.example.com",
                "http://localhost:3000"
            ]
        else:  # development
            return [
                "http://localhost:3000",
                "http://localhost:3001",
                "http://127.0.0.1:3000",
                "http://127.0.0.1:3001"
            ]

    def get_database_url(self) -> str:
        """Get database connection URL."""
        return f"firestore://{self.project_id}/{self.database.firestore_database}"

    def get_bigquery_dataset_id(self) -> str:
        """Get full BigQuery dataset ID."""
        return f"{self.project_id}.{self.database.bigquery_dataset}"

    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary."""
        return {
            "environment": self.environment.value,
            "project_id": self.project_id,
            "region": self.region,
            "database": self.database.model_dump(),
            "pubsub": self.pubsub.model_dump(),
            "storage": self.storage.model_dump(),
            "api": self.api.model_dump(),
            "pipeline": self.pipeline.model_dump(),
            "ai": self.ai.model_dump(),
            "collections": self.collections.model_dump()
        }

    def validate_configuration(self) -> bool:
        """Validate the entire configuration."""
        try:
            # Pydantic automatically validates on initialization
            # Additional custom validation can be added here
            logger.info(f"Configuration validated successfully for environment: {self.environment.value}")
            return True
        except Exception as e:
            logger.error(f"Configuration validation failed: {e}")
            return False


# Global configuration instance
_config_instance = None


def get_config(environment: str = None, force_reload: bool = False) -> CityPulseConfig:
    """
    Get the global configuration instance with enhanced error handling.

    Args:
        environment: Environment name (development, staging, production)
        force_reload: Force reload of configuration instance

    Returns:
        CityPulseConfig instance

    Raises:
        ValueError: If configuration validation fails
    """
    global _config_instance
    if _config_instance is None or force_reload:
        try:
            if environment:
                _config_instance = CityPulseConfig(environment=Environment(environment))
            else:
                _config_instance = CityPulseConfig()

            # Validate configuration
            if not _config_instance.validate_configuration():
                raise ValueError("Configuration validation failed")

        except Exception as e:
            logger.error(f"Failed to initialize configuration: {e}")
            raise ValueError(f"Configuration initialization failed: {e}")

    return _config_instance


def reset_config():
    """Reset the global configuration instance (useful for testing)."""
    global _config_instance
    _config_instance = None


# Convenience functions for common configuration access
def get_database_config() -> DatabaseConfig:
    """Get database configuration."""
    return get_config().database


def get_pubsub_config() -> PubSubConfig:
    """Get Pub/Sub configuration."""
    return get_config().pubsub


def get_storage_config() -> StorageConfig:
    """Get storage configuration."""
    return get_config().storage


def get_api_config() -> APIConfig:
    """Get API configuration."""
    return get_config().api


def get_pipeline_config() -> DataPipelineConfig:
    """Get pipeline configuration."""
    return get_config().pipeline


def get_ai_config() -> AIConfig:
    """Get AI configuration."""
    return get_config().ai


def get_collections_config() -> FirestoreCollections:
    """Get collections configuration."""
    return get_config().collections


# Configuration validation utilities
def validate_environment_config(environment: str) -> bool:
    """
    Validate configuration for a specific environment.

    Args:
        environment: Environment to validate

    Returns:
        True if configuration is valid, False otherwise
    """
    try:
        config = CityPulseConfig(environment=Environment(environment))
        return config.validate_configuration()
    except Exception as e:
        logger.error(f"Environment configuration validation failed for {environment}: {e}")
        return False


def get_config_summary() -> Dict[str, Any]:
    """
    Get a summary of the current configuration.

    Returns:
        Dictionary containing configuration summary
    """
    config = get_config()
    return {
        "environment": config.environment.value,
        "project_id": config.project_id,
        "region": config.region,
        "database_dataset": config.database.bigquery_dataset,
        "api_port": config.api.port,
        "api_debug": config.api.debug,
        "pipeline_workers": config.pipeline.max_num_workers,
        "ai_model": config.ai.model_name
    }
