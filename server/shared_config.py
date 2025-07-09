"""
Centralized configuration management for CityPulse.

This module provides a unified configuration system that can be used across
all components of the CityPulse platform (API, data models, pipelines, etc.).
"""

import os
from typing import Optional, Dict, Any
from dataclasses import dataclass
from pathlib import Path


@dataclass
class DatabaseConfig:
    """Database configuration settings."""
    project_id: str
    firestore_database: str = "(default)"
    bigquery_dataset: str = "citypulse_analytics"
    credentials_path: Optional[str] = None
    
    @property
    def bigquery_events_table(self) -> str:
        return f"{self.bigquery_dataset}.events"
    
    @property
    def bigquery_users_table(self) -> str:
        return f"{self.bigquery_dataset}.users"
    
    @property
    def bigquery_feedback_table(self) -> str:
        return f"{self.bigquery_dataset}.feedback"


@dataclass
class FirestoreCollections:
    """Firestore collection names."""
    events: str = "events"
    users: str = "users"
    feedback: str = "feedback"
    user_profiles: str = "user_profiles"


@dataclass
class PubSubConfig:
    """Pub/Sub configuration settings."""
    project_id: str
    citizen_reports_topic: str = "citizen-reports"
    iot_data_topic: str = "iot-data"
    social_media_topic: str = "social-media-feeds"
    official_feeds_topic: str = "official-feeds"
    dead_letter_topic: str = "dead-letter-queue"
    
    @property
    def citizen_reports_subscription(self) -> str:
        return f"{self.citizen_reports_topic}-subscription"
    
    @property
    def iot_data_subscription(self) -> str:
        return f"{self.iot_data_topic}-subscription"


@dataclass
class StorageConfig:
    """Cloud Storage configuration settings."""
    project_id: str
    temp_bucket: str
    staging_bucket: str
    media_bucket: str
    
    def get_temp_bucket_name(self) -> str:
        return f"{self.project_id}-{self.temp_bucket}"
    
    def get_staging_bucket_name(self) -> str:
        return f"{self.project_id}-{self.staging_bucket}"
    
    def get_media_bucket_name(self) -> str:
        return f"{self.project_id}-{self.media_bucket}"


@dataclass
class APIConfig:
    """API configuration settings."""
    host: str = "0.0.0.0"
    port: int = 8000
    debug: bool = False
    cors_origins: list = None
    max_request_size: int = 10 * 1024 * 1024  # 10MB
    rate_limit_per_minute: int = 100
    
    def __post_init__(self):
        if self.cors_origins is None:
            self.cors_origins = ["http://localhost:3000", "https://citypulse.example.com"]


@dataclass
class DataPipelineConfig:
    """Data pipeline configuration settings."""
    project_id: str
    region: str = "us-central1"
    temp_location: str = ""
    staging_location: str = ""
    max_num_workers: int = 10
    machine_type: str = "n1-standard-1"
    
    def __post_init__(self):
        if not self.temp_location:
            self.temp_location = f"gs://{self.project_id}-temp"
        if not self.staging_location:
            self.staging_location = f"gs://{self.project_id}-staging"


@dataclass
class AIConfig:
    """AI/ML configuration settings."""
    project_id: str
    region: str = "us-central1"
    model_name: str = "gemini-pro"
    vision_model_name: str = "gemini-pro-vision"
    max_tokens: int = 1000
    temperature: float = 0.7

    # AI Prompts
    analysis_prompt: str = """Analyze the following issue report from a citizen.
---
Description: {text_to_process}
---
1.  Summarize the issue in one sentence.
2.  Classify it into: [Pothole, Water Logging, Broken Streetlight,
    Garbage Dump, Traffic Jam, Public Safety, Other].
3.  If an image is provided, list key objects detected.
Return a JSON object with keys "summary", "category", "image_tags"."""

    icon_prompt: str = """A simple, modern, flat icon representing '{category}'
for a city services app. Minimalist, vector style, on a white background."""


class CityPulseConfig:
    """Main configuration class for CityPulse platform."""
    
    def __init__(self, environment: str = None):
        """
        Initialize configuration based on environment.
        
        Args:
            environment: Environment name (development, staging, production)
        """
        self.environment = environment or os.getenv("CITYPULSE_ENV", "development")
        self.project_id = os.getenv("GOOGLE_CLOUD_PROJECT", "citypulse-21")
        self.region = os.getenv("GOOGLE_CLOUD_REGION", "us-central1")
        
        # Initialize all configuration sections
        self._init_database_config()
        self._init_pubsub_config()
        self._init_storage_config()
        self._init_api_config()
        self._init_pipeline_config()
        self._init_ai_config()
        self._init_collections()
    
    def _init_database_config(self):
        """Initialize database configuration."""
        credentials_path = self._get_credentials_path()
        
        self.database = DatabaseConfig(
            project_id=self.project_id,
            firestore_database=os.getenv("FIRESTORE_DATABASE", "(default)"),
            bigquery_dataset=os.getenv("BIGQUERY_DATASET", "citypulse_analytics"),
            credentials_path=credentials_path
        )
    
    def _init_pubsub_config(self):
        """Initialize Pub/Sub configuration."""
        self.pubsub = PubSubConfig(
            project_id=self.project_id,
            citizen_reports_topic=os.getenv("CITIZEN_REPORTS_TOPIC", "citizen-reports"),
            iot_data_topic=os.getenv("IOT_DATA_TOPIC", "iot-data"),
            social_media_topic=os.getenv("SOCIAL_MEDIA_TOPIC", "social-media-feeds"),
            official_feeds_topic=os.getenv("OFFICIAL_FEEDS_TOPIC", "official-feeds"),
            dead_letter_topic=os.getenv("DEAD_LETTER_TOPIC", "dead-letter-queue")
        )
    
    def _init_storage_config(self):
        """Initialize storage configuration."""
        self.storage = StorageConfig(
            project_id=self.project_id,
            temp_bucket=os.getenv("TEMP_BUCKET", "temp"),
            staging_bucket=os.getenv("STAGING_BUCKET", "staging"),
            media_bucket=os.getenv("MEDIA_BUCKET", "media")
        )
    
    def _init_api_config(self):
        """Initialize API configuration."""
        debug = self.environment == "development"
        cors_origins = self._get_cors_origins()
        
        self.api = APIConfig(
            host=os.getenv("API_HOST", "0.0.0.0"),
            port=int(os.getenv("API_PORT", "8000")),
            debug=debug,
            cors_origins=cors_origins,
            max_request_size=int(os.getenv("MAX_REQUEST_SIZE", str(10 * 1024 * 1024))),
            rate_limit_per_minute=int(os.getenv("RATE_LIMIT_PER_MINUTE", "100"))
        )
    
    def _init_pipeline_config(self):
        """Initialize data pipeline configuration."""
        self.pipeline = DataPipelineConfig(
            project_id=self.project_id,
            region=self.region,
            temp_location=os.getenv("PIPELINE_TEMP_LOCATION", ""),
            staging_location=os.getenv("PIPELINE_STAGING_LOCATION", ""),
            max_num_workers=int(os.getenv("PIPELINE_MAX_WORKERS", "10")),
            machine_type=os.getenv("PIPELINE_MACHINE_TYPE", "n1-standard-1")
        )
    
    def _init_ai_config(self):
        """Initialize AI configuration."""
        self.ai = AIConfig(
            project_id=self.project_id,
            region=self.region,
            model_name=os.getenv("AI_MODEL_NAME", "gemini-pro"),
            vision_model_name=os.getenv("AI_VISION_MODEL_NAME", "gemini-pro-vision"),
            max_tokens=int(os.getenv("AI_MAX_TOKENS", "1000")),
            temperature=float(os.getenv("AI_TEMPERATURE", "0.7"))
        )
    
    def _init_collections(self):
        """Initialize Firestore collection names."""
        self.collections = FirestoreCollections(
            events=os.getenv("EVENTS_COLLECTION", "events"),
            users=os.getenv("USERS_COLLECTION", "users"),
            feedback=os.getenv("FEEDBACK_COLLECTION", "feedback"),
            user_profiles=os.getenv("USER_PROFILES_COLLECTION", "user_profiles")
        )
    
    def _get_credentials_path(self) -> Optional[str]:
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
    
    def _get_cors_origins(self) -> list:
        """Get CORS origins based on environment."""
        if self.environment == "production":
            return [
                "https://citypulse.example.com",
                "https://www.citypulse.example.com",
                "https://api.citypulse.example.com"
            ]
        elif self.environment == "staging":
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
            "environment": self.environment,
            "project_id": self.project_id,
            "region": self.region,
            "database": self.database.__dict__,
            "pubsub": self.pubsub.__dict__,
            "storage": self.storage.__dict__,
            "api": self.api.__dict__,
            "pipeline": self.pipeline.__dict__,
            "ai": self.ai.__dict__,
            "collections": self.collections.__dict__
        }


# Global configuration instance
_config_instance = None


def get_config(environment: str = None) -> CityPulseConfig:
    """
    Get the global configuration instance.
    
    Args:
        environment: Environment name (development, staging, production)
        
    Returns:
        CityPulseConfig instance
    """
    global _config_instance
    if _config_instance is None:
        _config_instance = CityPulseConfig(environment)
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
