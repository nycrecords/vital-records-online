# -*- coding: utf-8 -*-
"""Extensions module. Each extension is initialized in the app factory located in app.py."""
from elasticsearch import Elasticsearch
from flask_caching import Cache
from flask_debugtoolbar import DebugToolbarExtension
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from flask_static_digest import FlaskStaticDigest
from flask_wtf.csrf import CSRFProtect
from vro.settings import CACHE_DEFAULT_TIMEOUT, ELASTICSEARCH_URL

csrf_protect = CSRFProtect()
db = SQLAlchemy()
es = Elasticsearch(ELASTICSEARCH_URL, timeout=120)
migrate = Migrate()
cache = Cache(config={
    "CACHE_TYPE": "SimpleCache",
    "CACHE_DEFAULT_TIMEOUT": CACHE_DEFAULT_TIMEOUT,
})
debug_toolbar = DebugToolbarExtension()
flask_static_digest = FlaskStaticDigest()
