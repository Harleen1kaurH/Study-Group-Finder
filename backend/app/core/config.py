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

    # "development" locally, "production" on Railway (set as a Railway env var).
    # Drives cookie behaviour below: frontend and backend live on the same
    # origin (localhost) in dev, but on two different domains in production
    # (Vercel + Railway), which changes what the auth cookie needs to look like.
    ENVIRONMENT: str = "development"

    # Comma-separated list of allowed frontend origins for CORS. Defaults to
    # the local Next.js dev server; set to the real Vercel URL(s) in
    # production via the ALLOWED_ORIGINS env var.
    ALLOWED_ORIGINS: str = "http://localhost:3000"

    class Config:
        env_file = ".env"

    @property
    def allowed_origins_list(self) -> list[str]:
        return [origin.strip() for origin in self.ALLOWED_ORIGINS.split(",") if origin.strip()]

    @property
    def cookie_secure(self) -> bool:
        # Secure cookies require HTTPS. Railway/Vercel both serve HTTPS, so
        # this is safe to turn on in production and must stay off for local
        # http://localhost dev (browsers refuse Secure cookies over plain http).
        return self.ENVIRONMENT == "production"

    @property
    def cookie_samesite(self) -> str:
        # "lax" works fine when frontend and backend share an origin (local
        # dev). In production they're on different domains (Vercel vs
        # Railway), which is a cross-site request from the browser's
        # perspective, and SameSite=Lax cookies are NOT sent on cross-site
        # fetch/XHR, only on top-level navigation, so auth would silently
        # break. "none" is required there (and only valid alongside Secure).
        return "none" if self.ENVIRONMENT == "production" else "lax"


settings = Settings()
