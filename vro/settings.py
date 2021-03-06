# -*- coding: utf-8 -*-
"""Application configuration.

Most configuration is set via environment variables.

For local development, use a .env file to set
environment variables.
"""
from environs import Env

env = Env()
env.read_env()

ENV = env.str("FLASK_ENV", default="production")
DEBUG = ENV == "development"
ELASTICSEARCH_URL = env.str("ELASTICSEARCH_URL")

# Database Settings
SQLALCHEMY_DATABASE_URI = env.str("DATABASE_URL")
SQLALCHEMY_ENGINE_OPTIONS = {
    "pool_size": env.int("DATABASE_POOL_SIZE", default=5)
}
DATABASE_NAME = env.str("POSTGRES_DB")
DATABASE_USER = env.str("POSTGRES_USER")
DATABASE_PASSWORD = env.str("POSTGRES_PASSWORD")
DATABASE_HOST = env.str("DATABASE_HOST")
DATABASE_PORT = env.str("DATABASE_PORT")
DATABASE_SSLMODE = env.str("DATABASE_SSLMODE")

SECRET_KEY = env.str("SECRET_KEY")
SEND_FILE_MAX_AGE_DEFAULT = env.int("SEND_FILE_MAX_AGE_DEFAULT")
BCRYPT_LOG_ROUNDS = env.int("BCRYPT_LOG_ROUNDS", default=13)
DEBUG_TB_ENABLED = DEBUG
DEBUG_TB_INTERCEPT_REDIRECTS = False
CACHE_TYPE = "simple"  # Can be "memcached", "redis", etc.
CACHE_DEFAULT_TIMEOUT = env.int("CACHE_DEFAULT_TIMEOUT", default=86400)
SQLALCHEMY_TRACK_MODIFICATIONS = False

# Azure Settings
AZURE_STORAGE_ACCOUNT_NAME = env.str("AZURE_STORAGE_ACCOUNT_NAME")
AZURE_STORAGE_ACCOUNT_KEY = env.str("AZURE_STORAGE_ACCOUNT_KEY")
AZURE_CONTAINER_NAME = env.str("AZURE_CONTAINER_NAME")

# Session Settings
SESSION_COOKIE_PATH = '/'
SESSION_COOKIE_SECURE = True
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = "Strict"

GOOGLE_ANALYTICS_ID = env.str("GOOGLE_ANALYTICS_ID")
