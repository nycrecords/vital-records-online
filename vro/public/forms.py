from flask_wtf import Form
from wtforms import (
    SelectField,
    SubmitField,
    IntegerField,
)
from wtforms.validators import NumberRange
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