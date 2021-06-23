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
        certificate = Certificate(type_=certificate_types.BIRTH, county=counties.QUEENS, year=None, number="00100")
        certificate.save()
        assert certificate.year is None

    def test_number_is_nullable(self):
        """Test null number."""
        certificate = Certificate(type_=certificate_types.BIRTH, county=counties.QUEENS, year=1995, number=None)
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
