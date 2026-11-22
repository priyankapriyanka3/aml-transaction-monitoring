from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import model_validator


class Settings(BaseSettings):
    database_url: str = "sqlite:///./app.db"
    jwt_secret_key: str = "dev-secret-key-change-in-production"
    jwt_algorithm: str = "HS256"
    jwt_expiration_minutes: int = 480
    cors_origins: str = "http://localhost:5173"
    debug: bool = False
    rate_limit_enabled: bool = True
    
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")
    
    @model_validator(mode="after")
    def validate_jwt_secret_in_production(self):
        if not self.debug and "dev-secret-key" in self.jwt_secret_key:
            raise ValueError(
                "JWT_SECRET_KEY must be set to a secure value in production. "
                "The default 'dev-secret-key-change-in-production' is only allowed in debug mode."
            )
        return self
    
    @property
    def cors_origins_list(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",")]


settings = Settings()
