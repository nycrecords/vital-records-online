# -*- coding: utf-8 -*-
"""Test forms."""

from vro.public.forms import (BrowseAllForm,
                              SearchByNumberForm,
                              SearchByNameForm)

class TestBrowseAllForm:
    def test_certificate_type_choice_invalid(self, testapp, db):
        form = BrowseAllForm(
            certificate_type="vital",
            year_range="1862 - 1949",
            county="queens"
        )
        assert form.validate() is False

    def test_county_choice_invalid(self, testapp, db):
        form = BrowseAllForm(
            certificate_type="vital",
            year_range="1862 - 1949",
            county="jersey"
        )
        assert form.validate() is False


class TestSearchByNumberForm:
    def test_validate_success(self, testapp, db):
        form = SearchByNumberForm(
            certificate_type="birth",
            year=1900,
            county="queens",
            number=1
        )
        assert form.validate() is True

    def test_certificate_type_required(self, testapp, db):
        form = SearchByNumberForm(
            year=1900,
            county="queens",
            number=1
        )
        assert form.validate() is False

    def test_certificate_type_choice_invalid(self, testapp, db):
        form = SearchByNumberForm(
            certificate_type="vital",
            year=1900,
            county="queens",
            number=1
        )
        assert form.validate() is False

    def test_year_out_of_range(self, testapp, db):
        form = SearchByNumberForm(
            certificate_type="birth",
            year=1600,
            county="test",
            number=1
        )
        assert form.validate() is False

    def test_county_choice_invalid(self, testapp, db):
        form = SearchByNumberForm(
            certificate_type="birth",
            year=1900,
            county="jersey",
            number=1
        )
        assert form.validate() is False

    def test_number_out_of_range(self, testapp, db):
        form = SearchByNumberForm(
            certificate_type="birth",
            year=1900,
            county="test",
            number=0
        )
        assert form.validate() is False


class TestSearchByNameForm:
    def test_validate_success(self, testapp, db):
        form = SearchByNameForm(
            certificate_type="birth",
            last_name="Smith",
            first_name="John",
            year=1900,
            county="queens"
        )
        assert form.validate() is True

    def test_certificate_type_required(self, testapp, db):
        form = SearchByNameForm(
            last_name="Smith",
            first_name="John",
            year=1900,
            county="queens"
        )
        assert form.validate() is False

    def test_certificate_type_choice_invalid(self, testapp, db):
        form = SearchByNameForm(
            certificate_type="vital",
            last_name="Smith",
            first_name="John",
            year=1900,
            county="queens"
        )
        assert form.validate() is False

    def test_last_name_required(self, testapp, db):
        form = SearchByNameForm(
            certificate_type="birth",
            first_name="John",
            year=1900,
            county="queens"
        )
        assert form.validate() is False

    def test_year_out_of_range(self, testapp, db):
        form = SearchByNameForm(
            certificate_type="birth",
            last_name="Smith",
            first_name="John",
            year=0,
            county="queens"
        )
        assert form.validate() is False

    def test_county_choice_invalid(self, testapp, db):
        form = SearchByNameForm(
            certificate_type="birth",
            last_name="Smith",
            first_name="John",
            year=1900,
            county="jersey"
        )
        assert form.validate() is False
