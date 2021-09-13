KINGS = "kings"
QUEENS = "queens"
BRONX = "bronx"
MANHATTAN = "manhattan"
RICHMOND = "richmond"  # staten island

COUNTIES = {
    KINGS: "K",
    QUEENS: "Q",
    BRONX: "B",
    MANHATTAN: "M",
    RICHMOND: "R"
}

COUNTY_VALUES = {
    KINGS: "Kings (Brooklyn)",
    QUEENS: "Queens",
    BRONX: "Bronx",
    MANHATTAN: "Manhattan",
    RICHMOND: "Richmond"
}

DROPDOWN = [
    ("", "ALL"),
    (KINGS, "Kings (Brooklyn)"),
    (BRONX, "Bronx"),
    (MANHATTAN, "Manhattan"),
    (QUEENS, "Queens"),
    (RICHMOND, "Richmond (Staten Island)")
]

SEARCH_DROPDOWN = [
    (KINGS, "Kings (Brooklyn"),
    (BRONX, "Bronx"),
    (MANHATTAN, "Manhattan"),
    (QUEENS, "Queens"),
    (RICHMOND, "Richmond (Staten Island)")
]

ALL = frozenset((KINGS, QUEENS, BRONX, MANHATTAN, RICHMOND))
