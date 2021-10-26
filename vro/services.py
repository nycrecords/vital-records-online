# -*- coding: utf-8 -*-
"""Functions for database query abstractions."""
from vro.extensions import cache, db
from vro.models import Certificate
from sqlalchemy.sql import func


@cache.cached(key_prefix="year_range")
def get_year_range():
    """
    Get the minimum and maximum values for Certificate year. Result is cached.

    :return: sqlalchemy Row object containing min and max value of Certificate year.
             ex. (1862, 1949)
    """
    return db.session.query(func.max(Certificate.year).label("year_max"),
                            func.min(Certificate.year).label("year_min")).one()

def get_count(q):
    """
    Efficiently get the count of a SQLAlchemy query by the avoiding query.count() subquery.

    :param q: SQLAlchemy BaseQuery object
    :return: Integer count value
    """
    count_q = q.statement.with_only_columns([func.count()]).order_by(None)
    return q.session.execute(count_q).scalar()

@cache.cached(key_prefix="certificate_count")
def get_certificate_count():
    """
    Get the total number of Certificates. Result is cached.

    :return: Integer count value
    """
    q = Certificate.query.filter(Certificate.filename.isnot(None))
    count_q = q.statement.with_only_columns([func.count()]).order_by(None)
    return q.session.execute(count_q).scalar()
