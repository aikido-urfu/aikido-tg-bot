from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    bot_token: SecretStr
    server_url: SecretStr
    git_path: SecretStr
    base_host: SecretStr
    debug_chat_id: SecretStr
    tg_auth_token: SecretStr
    server_auth_token: SecretStr
    model_config = SettingsConfigDict(env_file='.env', env_file_encoding='utf-8')


config = Settings()
