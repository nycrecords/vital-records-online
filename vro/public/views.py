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
    # Get default year range/values
    cached_year_range = get_year_range()
    default_year_range_value = "{} - {}".format(cached_year_range.year_min, cached_year_range.year_max)

    form = BrowseAllForm()
    page = request.args.get('page', 1, type=int)

    # Set up variables for search
    size = 50
    q_list = []

    # "Search by Year" for Search by Year Function/Parameter
    year_value = request.args.get("year", "")
    year_range_value = request.args.get("year_range", "")

    if year_value:
        q_list.append(Q("range", year={"gte": int(year_value), "lte": int(year_value)}))
        year_range_value = f"{year_value} - {year_value}"
    elif year_range_value and " to " in year_range_value:  # Only process range if it contains "to"
        year_range = [int(year.strip()) for year in year_range_value.split("to") if year.strip().isdigit()]
        if len(year_range) == 2:
            q_list.append(Q("range", year={"gte": year_range[0], "lte": year_range[1]}))
    
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

    s_test = Search(using=es, index="certificates").query(q)
    count_test = es.count(index="certificates", body=s_test.to_dict())["count"]

    # Add sort
    s = s.sort("cert_type", "year", "last_name", "county", "_id")

    # Apply search_after if it exists and we're not on the first page
    if page > 1 and 'search_after' in session:
        s = s.extra(search_after=session['search_after'])
    
    # Set size
    s = s[:size]

    # Execute search
    res = s.execute()

    # Store search_after for next page
    if len(res) == size:
        session['search_after'] = list(res[-1].meta.sort)
    else:
        session.pop('search_after', None)

    # Get total count
    count = res.hits.total.value

    # Calculate total pages
    # total_pages = min((count + size - 1) // size, 200) - This was a previous version of what I had, newer is below# 
    total_pages = (count + size - 1) // size

    # Flag for no results when going past a certain page
    no_results = False
    
    # This is the condition to get rid of the page loop
    if page > total_pages and total_pages > 0:
        no_results = True 

    # Handle the case when the page is less than 1
    elif page < 1:
        query_params = request.args.to_dict()
        query_params['page'] = 1
        return redirect(url_for('public.browse_all', **query_params))

    # Flask Pagination Stuff
    pagination = Pagination(
        page=page, 
        per_page=size, 
        total=count_test, 
        css_framework='bootstrap4', 
        format_total=True, 
        format_number=True, 
        search=False, 
        inner_window=2, 
        outer_window=0
    )

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
                """
                elif key == "year":
                    value = f"Year: {value}"
                """

                # Handle new URL
                current_args.pop(key)
                new_url = "{}?{}".format(request.base_url, urlencode(current_args))

                remove_filters[key] = (value, new_url)
        current_args = request.args.to_dict()

    # Pagination Controls
    has_prev = page > 1
    has_next = len(res) == size

    return render_template("public/browse_all.html",
                           form=form,
                           year_range_min=cached_year_range.year_min,
                           year_range_max=cached_year_range.year_max,
                           year_min_value=int(year_value) if year_value else (year_range[0] if year_range_value and " to " in year_range_value else cached_year_range.year_min),
                           year_max_value=int(year_value) if year_value else (year_range[1] if year_range_value and " to " in year_range_value else cached_year_range.year_max),
                           certificates=res,
                           page=page,
                           has_prev=has_prev,
                           has_next=has_next,
                           total_pages=total_pages,
                           num_results=format(count, ",d"),
                           total_documents=format(count, ",d"), 
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


"""
@blueprint.route('/browse-ledgers')
def browse_ledgers():
    Displaying Ledgers Page
    return render_template('public/browse_ledgers.html')
"""