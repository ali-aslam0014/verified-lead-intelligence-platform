import os
import json
from typing import List, Union, Any
from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

# Pre-sanitize environment variables from Vercel to prevent Pydantic ValidationError on empty strings
for env_key in list(os.environ.keys()):
    if isinstance(os.environ[env_key], str) and os.environ[env_key].strip() == "":
        del os.environ[env_key]

if "CORS_ORIGINS" in os.environ:
    raw_cors = os.environ["CORS_ORIGINS"].strip()
    if not raw_cors:
        del os.environ["CORS_ORIGINS"]
    elif not raw_cors.startswith("["):
        origins = [i.strip() for i in raw_cors.split(",") if i.strip()]
        os.environ["CORS_ORIGINS"] = json.dumps(origins)

for port_key in ["POSTGRES_PORT", "REDIS_PORT"]:
    if port_key in os.environ and not os.environ[port_key].isdigit():
        del os.environ[port_key]


class Settings(BaseSettings):
    PROJECT_NAME: str = "Verified Lead Intelligence Platform"
    ENVIRONMENT: str = "development"
    LOG_LEVEL: str = "INFO"
    SECRET_KEY: str = "development_secret_key_change_in_production_32bytes_min"
    API_V1_STR: str = "/api/v1"

    # PostgreSQL Database Configuration
    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str = "postgres"
    POSTGRES_DB: str = "lead_intelligence"
    POSTGRES_HOST: str = "localhost"
    POSTGRES_PORT: int = 5432
    DATABASE_URL: str = "postgresql+asyncpg://neondb_owner:npg_3ruCd9azkPeW@ep-lucky-moon-axqfo3b8-pooler.c-4.us-east-2.aws.neon.tech/neondb?ssl=require"

    # Redis & Queue Configuration
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_URL: str = "redis://localhost:6379/0"

    # Google Places API (New) Credentials
    GOOGLE_PLACES_API_KEY: str = "AIzaSyAaM4DohN1fiCKtKnbYP7dOagMjcidIebo"
    GOOGLE_MAPS_API_KEY: str = "AIzaSyAaM4DohN1fiCKtKnbYP7dOagMjcidIebo"
    GOOGLE_PLACES_ENABLED: bool = True

    # CORS Origins
    CORS_ORIGINS: Any = ["http://localhost:3000", "http://127.0.0.1:3000", "*"]

    @field_validator("POSTGRES_PORT", "REDIS_PORT", mode="before")
    @classmethod
    def assemble_ports(cls, v: Any, info) -> int:
        if v is None or v == "" or (isinstance(v, str) and not v.strip()):
            return 5432 if info.field_name == "POSTGRES_PORT" else 6379
        if isinstance(v, str):
            try:
                return int(v.strip())
            except ValueError:
                return 5432 if info.field_name == "POSTGRES_PORT" else 6379
        return int(v)

    @field_validator("DATABASE_URL", mode="before")
    @classmethod
    def assemble_db_url(cls, v: str) -> str:
        if isinstance(v, str):
            if v.startswith("postgresql://"):
                v = v.replace("postgresql://", "postgresql+asyncpg://", 1)
            elif v.startswith("postgres://"):
                v = v.replace("postgres://", "postgresql+asyncpg://", 1)
            if "sslmode=" in v:
                v = v.replace("sslmode=", "ssl=", 1)
        return v

    @field_validator("CORS_ORIGINS", mode="before")
    @classmethod
    def assemble_cors_origins(cls, v: Any) -> List[str]:
        if not v:
            return ["*"]
        if isinstance(v, list):
            return [str(i) for i in v]
        if isinstance(v, str):
            v_str = v.strip()
            if not v_str:
                return ["*"]
            if v_str.startswith("["):
                try:
                    import json
                    parsed = json.loads(v_str)
                    if isinstance(parsed, list):
                        return [str(i) for i in parsed]
                except Exception:
                    pass
            return [i.strip() for i in v_str.split(",") if i.strip()]
        return ["*"]

    model_config = SettingsConfigDict(
        env_file=(".env", "../.env"),
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore"
    )


settings = Settings()
