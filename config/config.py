from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    LOG_LEVEL: str = Field(default="INFO")
    DEBUG: bool = Field(default=True)

    OPENAI_API_KEY: str = Field(description="Open ai Key")
    INTENT_API_URL: str = Field(description="INTENT url name")

    POSTGRES_HOST: str = Field(description="pg host")
    POSTGRES_PORT: int = Field(description="pg port")
    POSTGRES_DB: str = Field(description="pg db name")
    POSTGRES_USER: str = Field(description="pg user name")
    POSTGRES_PASSWORD: str = Field(description="pg user password")

    REDIS_URL: str = Field(description="Redis URL")

    @property
    def DB_URL(self) -> str:
        return (
            f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_HOST}:"
            f"{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        )

    # model_config = SettingsConfigDict(env_file=".env")


settings = Settings()
