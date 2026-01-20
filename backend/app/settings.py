import os

APP_NAME = os.getenv("APP_NAME", "VasteLijn Portal")
JWT_SECRET = os.getenv("JWT_SECRET", "CHANGE_ME")
JWT_EXPIRE_MINUTES = int(os.getenv("JWT_EXPIRE_MINUTES", "10080"))
DB_PATH = os.getenv("DB_PATH", "/app/data/portal.db")

HEADWIND_BASE_URL = os.getenv("HEADWIND_BASE_URL", "")
HEADWIND_ADMIN_USER = os.getenv("HEADWIND_ADMIN_USER", "")
HEADWIND_ADMIN_PASS = os.getenv("HEADWIND_ADMIN_PASS", "")
