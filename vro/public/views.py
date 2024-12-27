# -*- coding: utf-8 -*-
"""Public section, including homepage and signup."""
from datetime import datetime, timedelta
from urllib.parse import urlencode

from azure.storage.blob import generate_blob_sas, BlobSasPermissions
from elasticsearch_dsl import Search, Q
from flask import (
    abort,
    Blueprint,
    current_app,
    render_template,
    redirect,
    request,
    url_for, 
    session
)
from flask_paginate import Pagination
from sqlalchemy.exc import DataError
from sqlalchemy.orm.exc import NoResultFound

from vro.constants import (
    certificate_types,
    counties
)
from vro.extensions import cache, es
from vro.models import Certificate
from vro.public.forms import (
    BrowseAllForm,
    SearchByNumberForm,
    SearchByNameForm
)
from vro.services import get_certificate_count, get_year_range

blueprint = Blueprint("public", __name__, static_folder="../static")


@blueprint.route("/", methods=["GET"])
@cache.cached()
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
    cached_year_range = get_year_range()

    # Calculate digitization progress
    count = get_certificate_count()
    digitization_percentage = round(count / 13300000 * 100)

    return render_template("public/index.html",
                           browse_all_form=browse_all_form,
                           search_by_number_form=search_by_number_form,
                           search_by_name_form=search_by_name_form,
                           year_range_min=cached_year_range.year_min,
                           year_range_max=cached_year_range.year_max,
                           digitized=format(count, ",d"),
                           digitization_percentage=digitization_percentage)


@blueprint.route("/browse-all", methods=["GET"])
def browse_all():
    """
    This view function handles GET requests for the Browse All page.
    A query is made for the initial page of certificates shown.

    :return: Template for the browse all page and a list of certificates to display.
             Redirect to public.view_certificate if only one certificate is returned.
    """
    def clean_query_params(args_dict, default_year_range):
        """Remove default values from query"""
        cleaned = args_dict.copy()
        if cleaned.get('year_range') == default_year_range:
            cleaned.pop('year_range')
        return cleaned

    # Get default year range/values
    cached_year_range = get_year_range()
    default_year_range_value = f"{cached_year_range.year_min} to {cached_year_range.year_max}"

    form = BrowseAllForm()
    page = request.args.get('page', 1, type=int)

    # Set up variables for search, results, and total documents
    size = 50
    q_list = []
    num_results = 0
    total_documents = 0
    
    # Initialize year-related variables
    year_value = request.args.get("year", "")
    year_range_value = request.args.get("year_range", "")
    year_min = cached_year_range.year_min
    year_max = cached_year_range.year_max

    if year_value:
        q_list.append(Q("range", year={"gte": int(year_value), "lte": int(year_value)}))
        year_range_value = f"{year_value} - {year_value}"
        year_min = year_max = int(year_value)
    elif year_range_value and year_range_value != default_year_range_value:
        if " to " in year_range_value:
            range_parts = [year.strip() for year in year_range_value.split("to") if year.strip().isdigit()]
            if len(range_parts) == 2:
                year_min, year_max = map(int, range_parts)
                q_list.append(Q("range", year={"gte": year_min, "lte": year_max}))

    for key, value in [
        ("cert_type", request.args.get("certificate_type", "")),
        ("number", request.args.get("number", "").lstrip("0")),
        ("county", request.args.get("county", "")),
        ("first_name", request.args.get("first_name", "")),
        ("last_name", request.args.get("last_name", ""))
    ]:
        if value:
            if key in ["first_name", "last_name"]:
                q_list.append(Q("multi_match", query=value.capitalize(), fields=[key, "spouse_"+key]))
            elif key == "cert_type" and value == "marriage":
                q_list.append(Q("terms", cert_type=[certificate_types.MARRIAGE, certificate_types.MARRIAGE_LICENSE]))
            else:
                q_list.append(Q("match", **{key: value}))
    q = Q("bool", must=q_list)

    # Create Search object
    s = Search(using=es, index="certificates").query(q).extra(track_total_hits=True)

    # Add sort
    s = s.sort("cert_type", "year", "last_name", "county", "_id")

    # Get count
    count = s.count()

    # Calculate total pages
    total_pages = (count + size - 1) // size

    # Testing the last page logic, instead of always showing 50 it will show the remainder 
    # if there is one. And then use that instead. Before it used to be a loop. 
    if page == total_pages:
        size = count - (total_pages - 1) * 50

    # Apply search_after if it exists and we're not on the first page
    if page > 1 and 'search_after' in session:
        s = s.extra(search_after=session['search_after'])

    # Set size
    s = s[:size]

    # Execute search
    res = s.execute()

    # Store search_after for next page
    if len(res) == size and page < total_pages:
        session['search_after'] = list(res[-1].meta.sort)
    else:
        session.pop('search_after', None)

    # Flask Pagination Setup
    pagination = Pagination(
        page=page, 
        per_page=50, 
        total=count, 
        css_framework='bootstrap4', 
        format_total=True, 
        format_number=True, 
        search=False, 
        inner_window=2, 
        outer_window=0,
        view_args=clean_query_params(request.args.to_dict(), default_year_range_value)
    )

    # This is for the no results mainly. But also for pagination and the boundaries. 
    no_results = False
    if page > total_pages and total_pages > 0:
        no_results = True
        num_results = "0"
        total_documents = "0"
    elif page < 1:
        query_params = clean_query_params(request.args.to_dict(), default_year_range_value)
        query_params['page'] = 1
        return redirect(url_for('public.browse_all', **query_params))
    else:
        num_results = format(count, ",d")
        total_documents = format(count, ",d")

    # Set form data from previous form submissions
    form.certificate_type.data = request.args.get("certificate_type", "")
    form.county.data = request.args.get("county", "")
    form.year_range.data = request.args.get("year_range", "") if request.args.get("year_range") != default_year_range_value else ""
    form.year.data = request.args.get("year", "")
    form.number.data = request.args.get("number", "")
    form.last_name.data = request.args.get("last_name", "")
    form.first_name.data = request.args.get("first_name", "")

    # Handle filter labels and URLs
    remove_filters = {}
    current_args = request.args.to_dict()
    for key, value in request.args.items():
        if key != "page" and value:
            if key == "year_range" and value == default_year_range_value:
                continue
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
            
            current_args_copy = clean_query_params(current_args.copy(), default_year_range_value)
            current_args_copy.pop(key, None)
            new_url = "{}?{}".format(request.base_url, urlencode(current_args_copy))

            remove_filters[key] = (value, new_url)
        current_args = request.args.to_dict()

    # Pagination Controls
    has_prev = page > 1
    has_next = page < total_pages

    return render_template( "public/browse_all.html",
                            form=form,
                            year_range_min=cached_year_range.year_min,
                            year_range_max=cached_year_range.year_max,
                            year_min_value=year_min,
                            year_max_value=year_max,
                            certificates=res,
                            page=page,
                            has_prev=has_prev,
                            has_next=has_next,
                            total_pages=total_pages,
                            num_results=num_results,
                            total_documents=total_documents,
                            remove_filters=remove_filters,
                            pagination=pagination,
                            no_results=no_results,
                            certificate_types=certificate_types)


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

    # Get default year range
    cached_year_range = get_year_range()

    return render_template("public/search.html",
                           search_by_number_form=search_by_number_form,
                           search_by_name_form=search_by_name_form,
                           year_range_min=cached_year_range.year_min)


@blueprint.route("/digital-vital-records", methods=["GET"])
def digital_vital_records():
    """
    Digital Vital Records page
    """
    return render_template("public/digital_vital_records.html")


@blueprint.route("/about", methods=["GET"])
@cache.cached()
def about():
    """About page."""
    # Calculate digitization progress
    count = get_certificate_count()
    digitization_percentage = round(count / 13300000 * 100)
    return render_template("public/about.html",
                           digitized=format(count, ",d"),
                           digitization_percentage=digitization_percentage)


@blueprint.route("/faq", methods=["GET"])
def faq():
    """
    FAQ page
    """
    return render_template("public/faq.html")
