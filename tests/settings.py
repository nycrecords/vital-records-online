"""Settings module for test app."""
from environs import Env

env = Env()
env.read_env()

ENV = "development"
TESTING = True
SQLALCHEMY_DATABASE_URI = "sqlite://"
SECRET_KEY = "not-so-secret-in-tests"
BCRYPT_LOG_ROUNDS = (
    4  # For faster tests; needs at least 4 to avoid "ValueError: Invalid rounds"
)
DEBUG_TB_ENABLED = False
CACHE_TYPE = "simple"  # Can be "memcached", "redis", etc.
SQLALCHEMY_TRACK_MODIFICATIONS = False
WTF_CSRF_ENABLED = False  # Allows form testing

AZURE_STORAGE_ACCOUNT_NAME = env.str("AZURE_STORAGE_ACCOUNT_NAME")
AZURE_STORAGE_ACCOUNT_KEY = env.str("AZURE_STORAGE_ACCOUNT_KEY")
AZURE_CONTAINER_NAME = env.str("AZURE_CONTAINER_NAME")