"""Application configuration loaded from environment variables."""
from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    database_url: str = "sqlite:///./earthbucks.db"
    secret_key: str = "dev-only-change-me"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 10080
    cors_origins: str = "http://localhost:5173,http://localhost:8000,http://127.0.0.1:5500"

    # vote_weight = 1 + b_contribution / (pool_excluding_b * size_factor)
    # size_factor targets an ideal pool size. Override via SIZE_FACTOR env var.
    size_factor: float = 1.0

    # -- Org experience (Build Phase 2) --------------------------------------
    # Fuzzy-name duplicate detection threshold for org self-registration
    # (difflib ratio, 0..1 - higher = stricter match required to warn).
    org_dup_threshold: float = 0.82
    # Guaranteed-to-pool rates (placeholders - tune later). An unclaimed /
    # merely-nominated mission guarantees this fraction to the pool; a real
    # representative CLAIMING the mission bumps it.
    pool_rate_unclaimed: float = 0.20
    pool_rate_claimed: float = 0.35
    # Version tag recorded with each click-through legal acceptance.
    attestation_version: str = "draft-2026-07"
    # Scaffolding cap: max EBX a ben can put on an UNAPPROVED org (10 = 1 vote).
    unapproved_org_ebx_cap: int = 10
    # -- Money, S/S/S & Resolutions (build seq 1) -----------------------------
    # Each landed RESOLUTION (resolved suggestion or mission step) bumps the
    # mission's credit-coin value by this much.
    resolution_value_bump: float = 0.02
    # Global coin value = 1 + net_platform_flow / coin_value_scale (placeholder).
    coin_value_scale: float = 100000.0

    @property
    def cors_origins_list(self) -> list[str]:
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()
