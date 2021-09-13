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


@blueprint.route("/browse-all", methods=["GET"])
def browse_all():
    """
    This view function handles GET requests for the Browse All page.
    A query is made for the initial page of certificates shown.

    :return: Template for the browse all page and a list of certificates to display.
    """
    year_range_query = db.session.query(func.max(Certificate.year).label("year_max"),
                                   func.min(Certificate.year).label("year_min")).one()
    form = BrowseAllForm()
    page = request.args.get('page', 1, type=int)

    filter_by_kwargs = {}
    filter_args = []
    remove_filters = {}

    for name, value, col in [
        ("type", request.args.get("certificate_type", ""), Certificate.type),
        ("number", request.args.get("number", ""), Certificate.number),
        ("county", request.args.get("county", ""), Certificate.county),
        ("year", request.args.get("year", ""), Certificate.year),
        ("year_range", request.args.get("year_range", ""), Certificate.year),
        ("number", request.args.get("number", ""), Certificate.number),
        ("first_name", request.args.get("first_name", ""), Certificate.first_name),
        ("last_name", request.args.get("last_name", ""), Certificate.last_name)
    ]:
        if value:
            if name in ("first_name", "last_name"):
                filter_args.append(
                    col.ilike(value)
                )
                remove_filters[name] = value
            elif name == "year_range":
                year_range = [int(year) for year in value.split() if year.isdigit()]
                filter_args.append(
                    col.between(year_range[0], year_range[1])
                )
                if year_range[0] != year_range_query.year_min and year_range[1] != year_range_query.year_max:
                    remove_filters[name] = value
            elif name == "type" and value == 'marriage':
                filter_args.append(col.in_(['marriage', 'marriage_license']))
                remove_filters[name] = value
            else:
                filter_by_kwargs[name] = value
                remove_filters[name] = value

    certificates = Certificate.query.filter_by(**filter_by_kwargs).filter(
        Certificate.filename.isnot(None),
        *filter_args,
    ).order_by(Certificate.id.asc()).paginate(
        page=page,
        per_page=50
    )

    form.certificate_type.data = request.args.get("certificate_type", "")
    form.county.data = request.args.get("county", "")
    form.year_range.data = request.args.get("year_range", "")
    form.year.data = request.args.get("year", "")
    form.number.data = request.args.get("number", "")
    form.last_name.data = request.args.get("last_name", "")
    form.first_name.data = request.args.get("first_name", "")

    if certificates.total == 1:
        return redirect(url_for("public.view_certificate", certificate_id=certificates.items[0].id))

    return render_template("public/browse_all.html",
                           form=form,
                           year_range_min=year_range_query.year_min,
                           year_range_max=year_range_query.year_max,
                           year_min_value=year_range[0] if request.args.get("year_range", "") else year_range_query.year_min,
                           year_max_value=year_range[1] if request.args.get("year_range", "") else year_range_query.year_max,
                           certificates=certificates,
                           num_results=format(certificates.total, ",d"),
                           remove_filters=remove_filters)


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
        if certificate.type == "marriage":
            spouse_certificate = Certificate.query.filter(Certificate.filename == certificate.filename,
                                                          Certificate.id != certificate.id,
                                                          Certificate.soundex != certificate.soundex).first()
            spouse_name = spouse_certificate.name
        else:
            spouse_name = ""

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
                           url=url,
                           spouse_name=spouse_name)


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
