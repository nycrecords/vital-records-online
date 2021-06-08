# -*- coding: utf-8 -*-
"""Public section, including homepage and signup."""
from flask import (
    Blueprint,
    render_template,
)

blueprint = Blueprint("public", __name__, static_folder="../static")


@blueprint.route("/", methods=["GET", "POST"])
def index():
    """NYC Core Framework test page."""
    return render_template("public/index.html")


@blueprint.route("/browse-all", methods=["GET", "POST"])
def browse_all():
    return render_template("public/browse_all.html")


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
