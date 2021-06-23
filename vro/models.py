"""
Models for Vital Records Online
"""

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
    """
    __tablename__ = "certificates"

    type = db.Column(db.Enum(*certificate_types.ALL, name="certificate_type"), nullable=False)
    county = db.Column(db.Enum(*counties.ALL, name="county"), nullable=False)
    year = db.Column(db.Integer)
    number = db.Column(db.String(10))

    def __init__(self, type_, county, year, number):
        self.type = type_
        self.county = county
        self.year = year
        self.number = number
