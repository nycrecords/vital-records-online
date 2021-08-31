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

DROPDOWN = [
    ("", "ALL"),
    (KINGS, "Brooklyn (Kings)"),
    (BRONX, "Bronx"),
    (MANHATTAN, "Manhattan"),
    (QUEENS, "Queens"),
    (RICHMOND, "Staten Island (Richmond)")
]

SEARCH_DROPDOWN = [
    (KINGS, "Brooklyn (Kings)"),
    (BRONX, "Bronx"),
    (MANHATTAN, "Manhattan"),
    (QUEENS, "Queens"),
    (RICHMOND, "Staten Island (Richmond)")
]

ALL = frozenset((KINGS, QUEENS, BRONX, MANHATTAN, RICHMOND))
