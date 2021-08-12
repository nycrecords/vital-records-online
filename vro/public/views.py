# -*- coding: utf-8 -*-
"""Public section, including homepage and signup."""
from flask import (
    current_app,
    abort,
    Blueprint,
    render_template
)
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.exc import DataError
from vro.public.forms import BrowseAllForm
from vro.models import Certificate
from vro.constants import (
    certificate_types,
    counties
)
from datetime import datetime, timedelta
from azure.storage.blob import generate_blob_sas, BlobSasPermissions

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
    certificates = Certificate.query.order_by(Certificate.id.asc()).limit(50).all()
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


@blueprint.route("/view/<certificate_id>", methods=["GET"])
def view_certificate(certificate_id):
    """

    """
    try:
        # Query for certificate
        certificate = Certificate.query.filter_by(id=certificate_id).one()

        # Generate SAS token
        sas_token = generate_blob_sas(account_name=current_app.config['AZURE_STORAGE_ACCOUNT_NAME'],
                                      account_key=current_app.config['AZURE_STORAGE_ACCOUNT_KEY'],
                                      container_name=current_app.config['AZURE_CONTAINER_NAME'],
                                      blob_name=certificate.blob_name,
                                      permission=BlobSasPermissions(read=True),
                                      expiry=datetime.utcnow() + timedelta(hours=1))

        # Generate blob URL
        url = "https://{0}.blob.core.windows.net/{1}/{2}?{3}".format(current_app.config['AZURE_STORAGE_ACCOUNT_NAME'],
                                                                     current_app.config['AZURE_CONTAINER_NAME'],
                                                                     certificate.blob_name,
                                                                     sas_token)
    except NoResultFound:
        return abort(404)
    except DataError:
        return abort(404)
    return render_template("public/view_certificate.html",
                           certificate=certificate,
                           certificate_types=certificate_types,
                           counties=counties,
                           url=url)


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
