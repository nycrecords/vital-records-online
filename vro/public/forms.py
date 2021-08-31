from flask_wtf import Form
from wtforms import (
    SelectField,
    SubmitField,
    IntegerField,
    StringField
)
from wtforms.validators import NumberRange, DataRequired
from vro.constants import certificate_types, counties


class BrowseAllForm(Form):
    """
    Form used for Browse All page filters.

    certificate_type: a select dropdown with the options for all supported certificate types.
                      Marriage Certificates and Marriage Licenses will be treated as the same in this form.
    year: a integer field with the range of supported years, 1866 - 1949.
    county: a select dropdown with options for all supported counties.
    """
    certificate_type = SelectField("Certificate Type:", choices=certificate_types.DROPDOWN)
    year = IntegerField("Year Range", validators=[NumberRange(1866, 1949)])
    county = SelectField("Borough:", choices=counties.DROPDOWN)
    submit = SubmitField("Update")

    def __init__(self):
        super(BrowseAllForm, self).__init__()


class SearchByNumberForm(Form):
    """

    """
    certificate_type = SelectField("Certificate Type:*", choices=certificate_types.SEARCH_DROPDOWN, validators=[DataRequired()])
    year = IntegerField("Year:", validators=[NumberRange(1866, 1949)], render_kw={"placeholder": "####"})
    county = SelectField("Borough:", choices=counties.SEARCH_DROPDOWN)
    number = IntegerField("Certificate Number:*", validators=[NumberRange(1, 9999999), DataRequired()], render_kw={"placeholder": "#######"})
    submit = SubmitField("Search")

    def __init__(self):
        super(SearchByNumberForm, self).__init__()


class SearchByNameForm(Form):
    """

    """
    certificate_type = SelectField("Certificate Type:*", choices=certificate_types.SEARCH_DROPDOWN, validators=[DataRequired()])
    last_name = StringField("Last Name:*", validators=[DataRequired()], render_kw={"placeholder": "#######"})
    first_name = StringField("First Name:", render_kw={"placeholder": "#######"})
    year = IntegerField("Year:", validators=[NumberRange(1866, 1949)], render_kw={"placeholder": "####"})
    county = SelectField("Borough:", choices=counties.SEARCH_DROPDOWN)
    submit = SubmitField("Search")

    def __init__(self):
        super(SearchByNameForm, self).__init__()