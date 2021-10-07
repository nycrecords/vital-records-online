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
from vro.models import (
    Certificate,
    MarriageData
)
from vro.constants import (
    certificate_types,
    counties
)
from datetime import datetime, timedelta
from azure.storage.blob import generate_blob_sas, BlobSasPermissions
from urllib.parse import urlencode

blueprint = Blueprint("public", __name__, static_folder="../static")


@blueprint.route("/", methods=["GET"])
def index():
    """
    Homepage for Vital Records Online

    :return: Template for the homepage
    """
    # Initialize forms
    browse_all_form = BrowseAllForm()
    search_by_number_form = SearchByNumberForm()
    search_by_name_form = SearchByNameForm()
    # Get default year range
    year_range = db.session.query(func.max(Certificate.year).label("year_max"),
                                   func.min(Certificate.year).label("year_min")).one()
    # Calculate digitization progress
    digitized = Certificate.query.filter(Certificate.filename.isnot(None)).count()
    digitization_percentage = round(digitized / 13300000 * 100)
    return render_template("public/index.html",
                           browse_all_form=browse_all_form,
                           search_by_number_form=search_by_number_form,
                           search_by_name_form=search_by_name_form,
                           year_range_min=year_range.year_min,
                           year_range_max=year_range.year_max,
                           digitized=format(digitized, ",d"),
                           digitization_percentage=digitization_percentage)


@blueprint.route("/browse-all", methods=["GET"])
def browse_all():
    """
    This view function handles GET requests for the Browse All page.
    A query is made for the initial page of certificates shown.

    :return: Template for the browse all page and a list of certificates to display.
             Redirect to public.view_certificate if only one certificate is returned.
    """
    # Get default year range/values
    year_range_query = db.session.query(func.max(Certificate.year).label("year_max"),
                                   func.min(Certificate.year).label("year_min")).one()
    default_year_range_value = "{} - {}".format(year_range_query.year_min, year_range_query.year_max)


    form = BrowseAllForm()
    page = request.args.get('page', 1, type=int)
    search_by_last_name = request.args.get("last_name", None)
    certificate_type = request.args.get("certificate_type", "")

    filter_by_kwargs = {}
    filter_args = []

    # Set query filters based on form values submitted
    if search_by_last_name and certificate_type in ("marriage", "marriage_license"):
        for name, value, col in [
            ("type", request.args.get("certificate_type", ""), Certificate.type),
            ("number", request.args.get("number", ""), Certificate.number),
            ("county", request.args.get("county", ""), Certificate.county),
            ("year", request.args.get("year", ""), Certificate.year),
            ("year_range", request.args.get("year_range", ""), Certificate.year),
            ("number", request.args.get("number", ""), Certificate.number),
            ("first_name", request.args.get("first_name", ""), MarriageData.first_name),
            ("last_name", request.args.get("last_name", ""), MarriageData.last_name)
        ]:
            if value:
                # Use ilike for case insensitive query
                if name in ("first_name", "last_name"):
                    filter_args.append(
                        col.ilike(value)
                    )
                # Split year_range into two separate values
                elif name == "year_range":
                    year_range = [int(year) for year in value.split() if year.isdigit()]
                    filter_args.append(
                        col.between(year_range[0], year_range[1])
                    )
                # Marriage certificates and marriage licenses are considered the same record type to the user
                elif name == "type" and value == 'marriage':
                    filter_args.append(col.in_(['marriage', 'marriage_license']))
                else:
                    filter_args.append(col == value)
        # Query used for search by last name and marriage records
        base_query = Certificate.query.distinct().join(MarriageData).filter(
            Certificate.filename.isnot(None),
            *filter_args,
        )
    else:
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
                # Use ilike for case insensitive query
                if name in ("first_name", "last_name"):
                    filter_args.append(
                        col.ilike(value)
                    )
                # Split year_range into two separate values
                elif name == "year_range":
                    year_range = [int(year) for year in value.split() if year.isdigit()]
                    filter_args.append(
                        col.between(year_range[0], year_range[1])
                    )
                # Marriage certificates and marriage licenses are considered the same record type to the user
                elif name == "type" and value == 'marriage':
                    filter_args.append(col.in_(['marriage', 'marriage_license']))
                else:
                    filter_by_kwargs[name] = value
        base_query = Certificate.query.filter_by(**filter_by_kwargs).filter(
            Certificate.filename.isnot(None),
            *filter_args,
        )
    # Set order by criteria and limit to 5000 results (100 pages)
    certificates = base_query.order_by(Certificate.type.asc(),
                                       Certificate.year.asc(),
                                       Certificate.last_name.asc(),
                                       Certificate.county.asc()).limit(5000).from_self().paginate(
        page=page,
        per_page=50
    )
    num_results = base_query.count()

    # If only one certificate is returned, go directly to the view certificate page
    if num_results == 1:
        return redirect(url_for("public.view_certificate", certificate_id=certificates.items[0].id))

    # Set form data from previous form submissions
    form.certificate_type.data = request.args.get("certificate_type", "")
    form.county.data = request.args.get("county", "")
    form.year_range.data = request.args.get("year_range", "")
    form.year.data = request.args.get("year", "")
    form.number.data = request.args.get("number", "")
    form.last_name.data = request.args.get("last_name", "")
    form.first_name.data = request.args.get("first_name", "")

    # Handle filter labels and URLs
    remove_filters = {}
    current_args = request.args.to_dict()
    for key, value in request.args.items():
        if key != "page" and value:
            if not (key == "year_range" and value == default_year_range_value):
                # Handle filter label
                if key == "certificate_type":
                    value = certificate_types.CERTIFICATE_TYPE_VALUES.get(value)
                elif key == "county":
                    value = counties.COUNTY_VALUES.get(value)
                elif key == "number":
                    value = "Certificate Number: {}".format(value)
                elif key == "first_name":
                    value = "First Name: {}".format(value)
                elif key == "last_name":
                    value = "Last Name: {}".format(value)

                # Handle new URL
                current_args.pop(key)
                new_url = "{}?{}".format(request.base_url, urlencode(current_args))

                remove_filters[key] = (value, new_url)
        current_args = request.args.to_dict()

    return render_template("public/browse_all.html",
                           form=form,
                           year_range_min=year_range_query.year_min,
                           year_range_max=year_range_query.year_max,
                           year_min_value=year_range[0] if request.args.get("year_range", "") else year_range_query.year_min,
                           year_max_value=year_range[1] if request.args.get("year_range", "") else year_range_query.year_max,
                           certificates=certificates,
                           num_results=format(num_results, ",d"),
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
    """
    This view function handles GET requests for the search page.
    The search page handles two search forms, search by number and search by names.
    Form submissions are redirected to public.browse_all afterwards.

    :return: Template for search page.
    """
    # Initialize search forms
    search_by_number_form = SearchByNumberForm()
    search_by_name_form = SearchByNameForm()
    return render_template("public/search.html",
                           search_by_number_form=search_by_number_form,
                           search_by_name_form=search_by_name_form)


@blueprint.route("/digital-vital-records", methods=["GET"])
def digital_vital_records():
    return render_template("public/digital_vital_records.html")


@blueprint.route("/about", methods=["GET"])
def about():
    """About page."""
    return render_template("public/about.html")
