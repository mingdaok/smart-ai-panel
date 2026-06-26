import pytest
from backend.config import Settings, get_settings

def test_settings_loads_from_env(monkeypatch):
    monkeypatch.setenv("DEEPSEEK_API_KEY", "sk-test-key")
    monkeypatch.setenv("DEEPSEEK_BASE_URL", "https://test.api.com/v1")
    monkeypatch.setenv("DB_FILE_PATH", ":memory:")
    monkeypatch.setenv("PORT", "4000")
    monkeypatch.setenv("LLM_MODE", "mock")

    settings = Settings()

    assert settings.deepseek_api_key == "sk-test-key"
    assert settings.deepseek_base_url == "https://test.api.com/v1"
    assert settings.db_file_path == ":memory:"
    assert settings.port == 4000
    assert settings.llm_mode == "mock"

def test_settings_defaults():
    settings = Settings()
    assert settings.port == 3000
    assert settings.db_file_path == "./database/ai_panel.db"
    assert settings.llm_mode == "mock"
    assert settings.max_retries == 2
    assert settings.llm_timeout == 30
