# -*- coding: utf-8 -*-
"""Factories to help in tests."""
from factory.alchemy import SQLAlchemyModelFactory

from vro.database import db
from vro.models import Certificate
from vro.constants import (certificate_types,
                           counties,
                           months)

import random
import string

class BaseFactory(SQLAlchemyModelFactory):
    """Base factory."""

    class Meta:
        """Factory configuration."""

        abstract = True
        sqlalchemy_session = db.session


class CertificateFactory(BaseFactory):
    """Certificate factory."""

    type_ = random.sample(certificate_types.ALL, 1)[0]
    county = random.sample(counties.ALL, 1)[0]
    month = random.sample(months.ALL, 1)[0]
    day = str(random.randint(1, 30))
    year = random.randint(1000, 2000)
    number = str(random.randint(1, 10000))
    first_name = "".join(random.choices(string.ascii_uppercase, k = 10))
    last_name = "".join(random.choices(string.ascii_uppercase, k = 10))
    age = str(random.randint(1, 100))
    soundex = "".join(random.choices(string.ascii_uppercase + string.digits, k = 4))
    path_prefix = "REC0051_VitalRecords/Births/Bronx/1900/"
    filename = "B-B-1900-0000001.pdf"

    class Meta:
        """Factory configuration."""

        model = Certificate
