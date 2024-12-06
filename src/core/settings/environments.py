import os
from typing import Annotated

from pydantic import Field, field_validator, EmailStr, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

from core.settings import BASE_DIR

ENV_FILE = BASE_DIR / '../environments/.env'


class DatabaseEnvs(BaseSettings):
    name: Annotated[str, Field(..., alias='POSTGRES_DB')]
    host: Annotated[str, Field('localhost')]
    port: Annotated[int, Field(5432)]
    user: Annotated[str, Field('postgres')]
    password: Annotated[str, Field('postgres')]

    model_config = SettingsConfigDict(
        env_file=ENV_FILE,
        extra='ignore',
        env_prefix='POSTGRES_',
    )


class SuperuserEnvs(BaseSettings):
    username: str
    email: EmailStr
    password: str

    model_config = SettingsConfigDict(
        env_file=ENV_FILE,
        extra='ignore',
        env_prefix='DJANGO_SUPERUSER_',
    )

    @model_validator(mode='after')
    def load_env(self):
        for field, value in self.model_dump().items():
            key = f'{self.model_config['env_prefix']}{field}'.upper()
            os.environ.setdefault(key, value)
        return self


class AppEnvs(BaseSettings):
    secret_key: str
    debug: Annotated[bool, Field(False)]
    allowed_hosts: Annotated[str | list[str], Field(['localhost', '0.0.0.0'])]

    model_config = SettingsConfigDict(env_file=ENV_FILE, extra='ignore', env_prefix='DJANGO_')

    @field_validator('allowed_hosts', mode='before')
    def get_allowed_hosts_as_list(cls, v: str | list[str]) -> list[str]:
        if isinstance(v, str):
            return v.split(' ')
        return v


class Envs:
    app: AppEnvs = AppEnvs()
    db: DatabaseEnvs = DatabaseEnvs()
    admin: SuperuserEnvs = SuperuserEnvs()


envs = Envs
