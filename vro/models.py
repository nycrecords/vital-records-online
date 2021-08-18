"""
Models for Vital Records Online
"""

from flask import url_for
from vro.database import db, PkModel
from vro.constants import (
    certificate_types,
    counties
)

class Certificate(PkModel):
    """
    Define the Certificate class for the `certificates` table with the following columns:

    id          integer, primary key
    type        certificate_type, type of certificate (e.g. "birth")
    county      county, certificate county (e.g. "queens")
    year        integer, year certificate was issued
    number      varchar(10), certificate number
    path_prefix varchar, path prefix of file in Azure Storage Container
    filename    varchar, filename of certificate
    """
    __tablename__ = "certificates"

    type = db.Column(db.Enum(*certificate_types.ALL, name="certificate_type"), nullable=False)
    county = db.Column(db.Enum(*counties.ALL, name="county"), nullable=False)
    year = db.Column(db.Integer)
    number = db.Column(db.String(10))
    path_prefix = db.Column(db.String)
    filename = db.Column(db.String)

    def __init__(self, type_, county, year, number, path_prefix, filename):
        self.type = type_
        self.county = county
        self.year = year
        self.number = number
        self.path_prefix = path_prefix
        self.filename = filename


    @property
    def display_string(self):
        """
        A property to generate a string to identify each certificate with the following format:
        <CERTIFICATE_TYPE>-<COUNTY>-<YEAR>-<CERTIFICATE_NUMBER>

        :return: A string with the above format to be used in the Browse All page.
        """
        return self.filename[:-4]


    @property
    def thumbnail(self):
        """
        A property that determines which thumbnail image to use based on county and certificate type.
        Thumbnail images have the following file name format:
        <COUNTY_INITIAL>_<CERTIFICATE_TYPE>.png

        :return: The path to the thumbnail image.
        """
        county = counties.COUNTIES.get(self.county, "")
        # Marriage Licenses will use the same thumbnail as marriage certificates
        if self.type == certificate_types.MARRIAGE_LICENSE:
            certificate_type = certificate_types.MARRIAGE
        else:
            certificate_type = self.type
        thumbnail = url_for("static", filename="img/thumbnails/{}_{}.png".format(county, certificate_type))
        return thumbnail


    @property
    def certificate_number_string(self):
        """
        A property that generates a 7 digit string with certificate number and leading zeros.

        :return: A 7 digit string with certificate number and leading zeros.
        """
        return self.number.zfill(7)


    @property
    def blob_name(self):
        """
        A property that generates a certificate's Azure blob name by concatenating path_prefix and filename.

        :return: The blob name used to generate blob SAS token and blob URL.
        """
        return self.path_prefix + self.filename
