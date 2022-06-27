BIRTH = "birth"
DEATH = "death"
MARRIAGE = "marriage"
MARRIAGE_LICENSE = "marriage_license"

TYPES = {
    BIRTH: "B",
    DEATH: "D",
    MARRIAGE: "M",
    MARRIAGE_LICENSE: "L"
}

CERTIFICATE_TYPE_VALUES = {
    BIRTH: "Birth Certificate",
    DEATH: "Death Certificate",
    MARRIAGE: "Marriage Record",
}

DROPDOWN = [
    ("", "ALL"),
    (BIRTH, "Birth Certificate"),
    (DEATH, "Death Certificate"),
    (MARRIAGE, "Marriage Record")
]

SEARCH_DROPDOWN = [
    (BIRTH, "Birth Certificate"),
    (DEATH, "Death Certificate"),
    (MARRIAGE, "Marriage Record")
]

ALL = frozenset((BIRTH, DEATH, MARRIAGE, MARRIAGE_LICENSE))
