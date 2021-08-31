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

DROPDOWN = [
    ("", "ALL"),
    (BIRTH, "Birth Certificate"),
    (DEATH, "Death Certificate"),
    (MARRIAGE, "Marriage Certificate")
]

SEARCH_DROPDOWN = [
    (BIRTH, "Birth Certificate"),
    (DEATH, "Death Certificate"),
    (MARRIAGE, "Marriage Certificate")
]

ALL = frozenset((BIRTH, DEATH, MARRIAGE, MARRIAGE_LICENSE))
