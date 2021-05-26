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


@blueprint.route("/about/")
def about():
    """About page."""
    return render_template("public/about.html")
