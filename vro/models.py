"""
Models for Vital Records Online
"""

from flask import url_for
from vro.database import db, PkModel
from vro.constants import (
    certificate_types,
    counties,
    months
)

class Certificate(PkModel):
    """
    Define the Certificate class for the `certificates` table with the following columns:

    id          integer, primary key
    county      county, certificate county (e.g. "queens")
    type        certificate_type, type of certificate (e.g. "birth")
    month       varchar, month of certificate
    day         varchar, day of certificate
    year        integer, year certificate was issued
    number      varchar(10), certificate number
    first_name  varchar, first name of individual pertaining to the certificate
    last_name   varchar, last name of individual pertaining to the certificate
    age         varchar, age of individual pertaining to the certificate
    soundex     varchar, certificate soundex
    path_prefix varchar, path prefix of file in Azure Storage Container
    filename    varchar, filename of certificate
    """
    __tablename__ = "certificates"

    type = db.Column(db.Enum(*certificate_types.ALL, name="certificate_type"), nullable=False)
    county = db.Column(db.Enum(*counties.ALL, name="county"), nullable=False)
    month = db.Column(db.String)
    day = db.Column(db.String)
    year = db.Column(db.Integer)
    number = db.Column(db.String(10))
    first_name = db.Column(db.String(64))
    last_name = db.Column(db.String(64))
    age = db.Column(db.String(10))
    soundex = db.Column(db.String(4))
    path_prefix = db.Column(db.String)
    filename = db.Column(db.String)
    marriage_data = db.relationship("MarriageData", backref=db.backref("certificate", uselist=False), lazy=True)

    def __init__(self,
                 type_,
                 county,
                 month,
                 day,
                 year,
                 number,
                 first_name,
                 last_name,
                 age,
                 soundex,
                 path_prefix,
                 filename):
        self.type = type_
        self.county = county
        self.month = month
        self.day = day
        self.year = year
        self.number = number
        self.first_name = first_name
        self.last_name = last_name
        self.age = age
        self.soundex = soundex
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
        import os
        # thumbnail = url_for("static", filename="img/thumbnails/{}_{}.png".format(county, certificate_type))
        thumbnail = "static/img/thumbnails/{}_{}.png".format(county, certificate_type)
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


    @property
    def name(self):
        """
        A property that generates the full name of the person on the certificate. If the first name if not present,
        only show the last name. Marriage licenses will show "Not Indexed" due to lack of index data.

        :return: Name of the person associated with the certificate.
        """
        if self.first_name is not None:
            return "{} {}".format(self.first_name, self.last_name)
        elif self.type == "marriage_license":
            return "Not Indexed"
        else:
            return self.last_name

    @property
    def date(self):
        """
        A property that generates a date string using year, month, and day in the format of YYYY-MM-DD.
        If day is missing use YYYY-MM.
        If month is missing use YYYY-00-DD.
        If month and day are missing use YYYY.

        :return: The date string associated with the certificate.
        """
        if self.year and self.month and self.day and self.day.isnumeric():
            return "{}-{}-{}".format(self.year, months.MONTHS.get(self.month, ""), self.day.zfill(2))
        elif self.year and self.month:
            return "{}-{}".format(self.year, months.MONTHS.get(self.month, ""))
        elif self.year and self.day and self.day.isnumeric():
            return "{}-00-{}".format(self.year, self.day.zfill(2))
        else: return self.year


class MarriageData(PkModel):
    """
    Define the MarriageData class for the `marriage_data` table with the following columns:

    id              integer, primary key
    certificate_id  integer, foreign key to the certificates table
    first_name      varchar, first name of individual pertaining to the certificate
    last_name       varchar, last name of individual pertaining to the certificate
    soundex         varchar, certificate soundex
    """
    __tablename__ = "marriage_data"
    certificate_id = db.Column(db.Integer, db.ForeignKey("certificates.id"), nullable=False)
    filename = db.Column(db.String)
    first_name = db.Column(db.String(64))
    last_name = db.Column(db.String(64))
    soundex = db.Column(db.String(4))

    @property
    def name(self):
        """
        A property that generates the full name of the person on the certificate. If the first name if not present,
        only show the last name.

        :return: Name of the person associated with the certificate.
        """
        if self.first_name is not None:
            return "{} {}".format(self.first_name, self.last_name)
        else:
            return self.last_name