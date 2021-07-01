# -*- coding: utf-8 -*-
"""Public section, including homepage and signup."""
from flask import (
    Blueprint,
    render_template,
)
from vro.public.forms import BrowseAllForm
from vro.models import Certificate

blueprint = Blueprint("public", __name__, static_folder="../static")


@blueprint.route("/", methods=["GET", "POST"])
def index():
    """
    Homepage for Vital Records Online

    :return: Template for the homepage
    """
    return render_template("public/index.html")


@blueprint.route("/browse-all", methods=["GET"])
def browse_all():
    """
    This view function handles GET requests for the Browse All page.
    A query is made for the initial page of certificates shown.

    :return: Template for the browse all page and a list of certificates to display.
    """
    form = BrowseAllForm()
    certificates = Certificate.query.limit(50).all()
    return render_template("public/browse_all.html",
                           form=form,
                           certificates=certificates,
                           num_results=len(certificates))


@blueprint.route("/browse-all", methods=["POST"])
def browse_all_filter():
    """
    This view function handles POST requests for the Browse All page.
    Based on the data returned from the BrowseAllForm(), the query for certificates will change.
    The query can be modified based on certificate type, year, and county.

    :return: Template for browse all page and an updated list of certificates based on the filters.
    """
    form = BrowseAllForm()
    certificates = Certificate.query.limit(50).all()
    return render_template("public/browse_all.html",
                           form=form,
                           certificates=certificates,
                           num_results=len(certificates))


@blueprint.route("/archives-holdings", methods=["GET", "POST"])
def archives_holdings():
    return render_template("public/archives_holdings.html")


@blueprint.route("/search", methods=["GET", "POST"])
def search():
    return render_template("public/search.html")


@blueprint.route("/genealogical-research", methods=["GET", "POST"])
def genealogical_research():
    return render_template("public/genealogical_research.html")


@blueprint.route("/about/")
def about():
    """About page."""
    return render_template("public/about.html")
