"""Настройки бота. Все секреты берутся из переменных окружения (файл .env)."""
import os
from dataclasses import dataclass

from dotenv import load_dotenv

DEFAULT_SYSTEM_PROMPT = (
    "Ты дружелюбный помощник в Telegram. Отвечай по-русски, коротко и по делу. "
    "Если не уверен в ответе, так и скажи."
)


@dataclass(frozen=True)
class Settings:
    telegram_token: str
    anthropic_api_key: str
    model: str
    system_prompt: str
    allowed_user_ids: frozenset[int]
    max_history: int

    @classmethod
    def from_env(cls) -> "Settings":
        load_dotenv()
        token = os.getenv("TELEGRAM_TOKEN", "").strip()
        api_key = os.getenv("ANTHROPIC_API_KEY", "").strip()
        if not token or not api_key:
            raise RuntimeError(
                "Задайте TELEGRAM_TOKEN и ANTHROPIC_API_KEY в файле .env (см. .env.example)"
            )
        ids = {
            int(x) for x in os.getenv("ALLOWED_USER_IDS", "").replace(" ", "").split(",") if x
        }
        return cls(
            telegram_token=token,
            anthropic_api_key=api_key,
            model=os.getenv("CLAUDE_MODEL", "claude-sonnet-5-5"),
            system_prompt=os.getenv("SYSTEM_PROMPT", DEFAULT_SYSTEM_PROMPT),
            allowed_user_ids=frozenset(ids),
            max_history=int(os.getenv("MAX_HISTORY", "20")),
        )
