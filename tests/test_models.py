# -*- coding: utf-8 -*-
"""Model unit tests."""
import pytest

from vro.extensions import db

from vro.models import Certificate

from .factories import CertificateFactory


@pytest.mark.usefixtures("db")
class TestCertificate:
    """Certificate tests."""

    def test_query_by_id(self):
        """Get certificate by ID."""
        certificate = Certificate('birth', 'queens', 1995, '100')
        db.session.add(certificate)
        db.session.commit()

        retrieved = Certificate.query.filter_by(id=certificate.id).one_or_none()
        assert retrieved == certificate


    def test_certificate_factory(self):
        """Test certificate factory."""
        certificate = CertificateFactory()
        db.session.add(certificate)
        db.session.commit()
        assert bool(certificate.type)
        assert bool(certificate.county)
        assert bool(certificate.year)
        assert bool(certificate.number)
