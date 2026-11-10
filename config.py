import os
from dataclasses import dataclass

@dataclass
class Settings:
    telegram_bot_token: str = os.getenv("TELEGRAM_BOT_TOKEN", "")
    flashtoken_api_key: str = os.getenv("FLASHTOKEN_API_KEY", "")
    admin_ids: tuple = tuple(int(x.strip()) for x in os.getenv("ADMIN_IDS", "").split(",") if x.strip())
    database_url: str = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///./bot.db")
    markup_percent: float = float(os.getenv("MARKUP_PERCENT", "40"))
    poll_interval: int = int(os.getenv("ORDER_POLL_SECONDS", "8"))
    support_username: str = os.getenv("SUPPORT_USERNAME", "")
    api_base: str = "https://flashtoken.shop/api/reseller/v1"

settings = Settings()
if settings.database_url.startswith("postgres://"):
    settings.database_url = settings.database_url.replace("postgres://", "postgresql+asyncpg://", 1)
elif settings.database_url.startswith("postgresql://") and "+asyncpg" not in settings.database_url:
    settings.database_url = settings.database_url.replace("postgresql://", "postgresql+asyncpg://", 1)
