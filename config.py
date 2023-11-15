from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import SecretStr


class Settings(BaseSettings):
    bot_token: SecretStr
    api_id: SecretStr
    api_hash: SecretStr
    channel_name: SecretStr
    channel_link: SecretStr
    channel_id: SecretStr
    private_channel_link: SecretStr
    private_channel_id: SecretStr
    model_config = SettingsConfigDict(env_file='.env', env_file_encoding='utf-8')

config = Settings()