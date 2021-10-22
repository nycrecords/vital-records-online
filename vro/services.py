# -*- coding: utf-8 -*-
"""Functions for database query abstractions."""
from vro.extensions import cache, db
from vro.models import Certificate
from sqlalchemy.sql import func


@cache.cached(key_prefix="year_range")
def get_year_range():
    return db.session.query(func.max(Certificate.year).label("year_max"),
                            func.min(Certificate.year).label("year_min")).one()

def get_count(q):
    count_q = q.statement.with_only_columns([func.count()]).order_by(None)
    return q.session.execute(count_q).scalar()

@cache.cached(key_prefix="certificate_count")
def get_certificate_count():
    q = Certificate.query.filter(Certificate.filename.isnot(None))
    count_q = q.statement.with_only_columns([func.count()]).order_by(None)
    return q.session.execute(count_q).scalar()
