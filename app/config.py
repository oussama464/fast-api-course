import pathlib

from pydantic_settings import BaseSettings, SettingsConfigDict

ENV_FILE = pathlib.Path(__file__).parent.parent.joinpath(".env")


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=ENV_FILE, env_file_encoding="utf-8")
    database_hostname: str
    database_port: str
    database_password: str
    database_name: str
    database_username: str
    secret_key: str
    algorithm: str
    access_token_expire_minutes: int


settings = Settings()  # type: ignore[call-arg]
