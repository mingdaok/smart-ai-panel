import os
from dataclasses import dataclass, field
from dotenv import load_dotenv

load_dotenv()

@dataclass
class Settings:
    deepseek_api_key: str = field(default_factory=lambda: os.getenv("DEEPSEEK_API_KEY", ""))
    deepseek_base_url: str = field(default_factory=lambda: os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com/v1"))
    db_file_path: str = field(default_factory=lambda: os.getenv("DB_FILE_PATH", "./database/ai_panel.db"))
    port: int = field(default_factory=lambda: int(os.getenv("PORT", "3000")))
    llm_mode: str = field(default_factory=lambda: os.getenv("LLM_MODE", "real"))
    max_retries: int = 2
    llm_timeout: int = 30


_settings: Settings | None = None


def get_settings() -> Settings:
    global _settings
    if _settings is None:
        _settings = Settings()
    return _settings
