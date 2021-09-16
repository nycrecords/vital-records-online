# -*- coding: utf-8 -*-
"""Test views."""
from .factories import CertificateFactory


class TestHomepage:
    def test_homepage_returns_200(self, testapp, db):
        # Goes to homepage
        res = testapp.get("/")
        assert res.status_code == 200
        assert b'The New York City Municipal Archives is undertaking a mass digitization project' in res


class TestViewCertificate:
    def test_view_certificate_returns_200(self, testapp, db):
        certificate = CertificateFactory()
        db.session.commit()
        res = testapp.get("/view/{}".format(certificate.id))
        assert res.status_code == 200
        assert b'Purchase Certified Copy' in res


class TestBrowseAll:
    def test_browse_all_returns_200(self, testapp, db):
        for i in range(5):
            CertificateFactory()
        db.session.commit()
        res = testapp.get("/browse-all")
        assert res.status_code == 200
        assert b'5 Vital Record Results' in res

    def test_no_results_found(self, testapp, db):
        res = testapp.get("/browse-all")
        assert res.status_code == 200
        assert b'No Results' in res


class TestSearch:
    def test_search_returns_200(self, testapp, db):
        res = testapp.get("/search")
        assert res.status_code == 200
        assert b'By Certificate Number' in res

