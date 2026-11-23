"""Application configuration using pydantic-settings."""
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    database_url: str = "sqlite:////tmp/aml_workbench.db"
    secret_key: str = "dev-secret-key-change-in-production-min-32-chars"  # Default for dev
    jwt_algorithm: str = "HS256"
    jwt_expiry_minutes: int = 480
    cors_origins: str = "http://localhost:5173"
    rate_limit_enabled: bool = True
    debug: bool = False
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )
    
    @property
    def cors_origins_list(self) -> list[str]:
        """Parse CORS origins from comma-separated string."""
        return [origin.strip() for origin in self.cors_origins.split(",")]
    
    def validate_secret_key(self) -> None:
        """Validate that secret key meets minimum security requirements."""
        if len(self.secret_key) < 32:
            raise ValueError("SECRET_KEY must be at least 32 characters long")


settings = Settings()
