# -*- coding: utf-8 -*-
"""Model unit tests."""
import pytest

from vro.constants import certificate_types, counties
from vro.extensions import db
from vro.models import Certificate
from .factories import CertificateFactory


@pytest.mark.usefixtures("db")
class TestCertificate:
    """Certificate tests."""

    def test_year_is_nullable(self):
        """Test null year."""
        certificate = Certificate(type_=certificate_types.BIRTH,
                                  county=counties.QUEENS,
                                  month="jan",
                                  day="1",
                                  year=None,
                                  number="00100",
                                  first_name="John",
                                  last_name="Smith",
                                  age="50",
                                  soundex="ABCD",
                                  path_prefix="REC0051_VitalRecords/Births/Bronx/1900/",
                                  filename="B-B-1900-0000001.pdf")
        certificate.save()
        assert certificate.year is None

    def test_number_is_nullable(self):
        """Test null number."""
        certificate = Certificate(type_=certificate_types.BIRTH,
                                  county=counties.QUEENS,
                                  month="jan",
                                  day="1",
                                  year=1995,
                                  number=None,
                                  first_name="Jane",
                                  last_name="Doe",
                                  age="50",
                                  soundex="ABCD",
                                  path_prefix="REC0051_VitalRecords/Births/Bronx/1900/",
                                  filename="B-B-1900-0000001.pdf")
        certificate.save()
        assert certificate.number is None

    def test_certificate_factory(self):
        """Test certificate factory."""
        certificate = CertificateFactory()
        db.session.commit()
        assert bool(certificate.type)
        assert bool(certificate.county)
        assert bool(certificate.year)
        assert bool(certificate.number)
