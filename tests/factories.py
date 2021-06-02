# -*- coding: utf-8 -*-
"""Factories to help in tests."""
from factory.alchemy import SQLAlchemyModelFactory

from vro.database import db
from vro.models import Certificate
from vro.constants import certificate_types, counties

import random


class BaseFactory(SQLAlchemyModelFactory):
    """Base factory."""

    class Meta:
        """Factory configuration."""

        abstract = True
        sqlalchemy_session = db.session


class CertificateFactory(BaseFactory):
    """Certificate factory."""

    type = random.sample(certificate_types.ALL, 1)[0]
    county = random.sample(counties.ALL, 1)[0]
    year = random.randint(1000, 2000)
    number = str(random.randint(1, 10000))

    class Meta:
        """Factory configuration."""

        model = Certificate