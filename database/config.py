import os

from pydantic_settings import BaseSettings, SettingsConfigDict

# BASE_DIR - loyihaning asosiy papkasi (bir papka yuqori database/ dan)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


class Settings(BaseSettings):
    DATABASE_URL: str
    bot_token: str
    model_config = SettingsConfigDict(
        # env_file="../.env",
        env_file=os.path.join(BASE_DIR, ".env"),
        case_sensitive=False,
        extra="ignore",  # << muhim: ortiqcha env bo'lsa ham yiqilmasin
    )


settings = Settings()


def get_allowed_tg_ids() -> set[int]:
    raw = os.getenv("ALLOWED_TG_IDS", "")
    return {int(x) for x in raw.split(",") if x.strip()}
