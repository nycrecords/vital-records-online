# -*- coding: utf-8 -*-
"""Public section, including homepage and signup."""
from vro.extensions import db
from flask import (
    abort,
    Blueprint,
    current_app,
    render_template,
    redirect,
    request,
    url_for
)
from sqlalchemy.sql import func
from sqlalchemy.orm import Session
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.exc import DataError
from vro.public.forms import (
    BrowseAllForm,
    SearchByNumberForm,
    SearchByNameForm
)
from vro.models import Certificate
from vro.constants import (
    certificate_types,
    counties
)
from datetime import datetime, timedelta
from azure.storage.blob import generate_blob_sas, BlobSasPermissions

blueprint = Blueprint("public", __name__, static_folder="../static")


@blueprint.route("/", methods=["GET"])
def index():
    """
    Homepage for Vital Records Online

    :return: Template for the homepage
    """
    browse_all_form = BrowseAllForm()
    search_by_number_form = SearchByNumberForm()
    search_by_name_form = SearchByNameForm()
    year_range = db.session.query(func.max(Certificate.year).label("year_max"),
                                   func.min(Certificate.year).label("year_min")).one()
    return render_template("public/index.html",
                           browse_all_form=browse_all_form,
                           search_by_number_form=search_by_number_form,
                           search_by_name_form=search_by_name_form,
                           year_range_min=year_range.year_min,
                           year_range_max=year_range.year_max)

@blueprint.route("/", methods=["POST"])
def homepage_search():
    """
    """
    if request.form["submit"] == "Search":
        filter_by_kwargs = {}
        filter_args = []
        for name, value, col in [
            ("type", request.form.get("type", ""), Certificate.type),
            ("county", request.form.get("county", ""), Certificate.county),
            ("year", request.form.get("year", ""), Certificate.year),
            ("number", request.form.get("number", ""), Certificate.number),
            ("first_name", request.form.get("first_name", ""), Certificate.first_name),
            ("last_name", request.form.get("last_name", ""), Certificate.last_name)
        ]:
            if value:
                if name in ("first_name", "last_name"):
                    filter_args.append(
                        col.ilike(value)
                    )
                else:
                    filter_by_kwargs[name] = value
        try:
            results = Certificate.query.filter_by(**filter_by_kwargs).filter(*filter_args, Certificate.filename.isnot(None))
            print(results)
            print()
        except:
            return abort(404)

        if len(results) == 1:
            return redirect(url_for("public.view_certificate", certificate_id=results[0].id))
        elif len(results) > 1:
            return redirect(url_for("public.results"))


@blueprint.route("/results", methods=["GET"])
def results():
    """
    This view function handles GET requests for the Browse All page.
    A query is made for the initial page of certificates shown.

    :return: Template for the browse all page and a list of certificates to display.
    """
    form = BrowseAllForm()
    certificates=[]
    return render_template("public/browse_all.html",
                           form=form,
                           certificates=certificates,
                           num_results=len(certificates))


@blueprint.route("/browse-all", methods=["GET"])
def browse_all():
    """
    This view function handles GET requests for the Browse All page.
    A query is made for the initial page of certificates shown.

    :return: Template for the browse all page and a list of certificates to display.
    """
    form = BrowseAllForm()
    page = request.args.get('page', 1, type=int)
    certificates = Certificate.query.filter(Certificate.filename.isnot(None)).order_by(Certificate.id.asc()).paginate(
        page=page, per_page=50)
    return render_template("public/browse_all.html",
                           form=form,
                           certificates=certificates,
                           num_results=format(certificates.total, ",d"))


@blueprint.route("/browse-all", methods=["POST"])
def browse_all_filter():
    """
    This view function handles POST requests for the Browse All page.
    Based on the data returned from the BrowseAllForm(), the query for certificates will change.
    The query can be modified based on certificate type, year, and county.

    :return: Template for browse all page and an updated list of certificates based on the filters.
    """
    form = BrowseAllForm()
    page = request.args.get('page', 1, type=int)
    certificate_type = request.form.get("type", "")
    county = request.form.get("county", "")
    year_range = request.form.get("year", "")
    Certificate.query.filter(Certificate.filename.isnot(None),
                             Certificate.type == certificate_type,
                             Certificate.county == county,
                             Certificate.year.between("", "")).order_by(Certificate.id.asc()).paginate(
        page=page, per_page=50)
    # Certificate.query.filter_by(**filter_by_kwargs).filter(*filter_args, Certificate.filename.isnot(None))
    return render_template("public/browse_all.html",
                           form=form,
                           certificates=certificates,
                           num_results=len(certificates))


@blueprint.route("/view/<certificate_id>", methods=["GET"])
def view_certificate(certificate_id):
    """
    This view function handles GET requests for the view certificate page.
    Query for certificate based on certificate id.
    Generate SAS token using the Azure Blob Storage SDK.
    Generate blob URL to be used as the source for the PDF viewer.

    :return: Template for view certificate page.
    """
    try:
        # Query for certificate
        certificate = Certificate.query.filter(Certificate.id==certificate_id, Certificate.filename.isnot(None)).one()

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


@blueprint.route("/search", methods=["GET"])
def search():
    search_by_number_form = SearchByNumberForm()
    search_by_name_form = SearchByNameForm()
    return render_template("public/search.html",
                           search_by_number_form=search_by_number_form,
                           search_by_name_form=search_by_name_form)


@blueprint.route("/search", methods=["POST"])
def search_post():
    return render_template("public/search.html")


@blueprint.route("/digital-vital-records", methods=["GET", "POST"])
def digital_vital_records():
    return render_template("public/digital_vital_records.html")


@blueprint.route("/conducting-research", methods=["GET", "POST"])
def conducting_research():
    return render_template("public/conducting_research.html")


@blueprint.route("/about/")
def about():
    """About page."""
    return render_template("public/about.html")
