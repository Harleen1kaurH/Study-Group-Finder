from pydantic_settings import BaseSettings

""" pydantic-settings provides BaseSettings, which makes app configuration easy by:

defining typed settings classes,
loading values from environment variables,
optionally reading a .env file. """

class Settings(BaseSettings):
    DATABASE_URL: str
    JWT_SECRET: str
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRE_DAYS: int = 7
    SENDGRID_API_KEY: str = ""
    SENDGRID_FROM_EMAIL: str = ""

    class Config:
        env_file = ".env"


settings = Settings()
