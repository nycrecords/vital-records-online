GENERAL = "general"
SALES = "sales"
PURCHASES = "purchases"

TYPES = {
    GENERAL: "G",
    SALES: "S",
    PURCHASES: "T",
}

LEDGER_TYPE_VALUES = {
    GENERAL: "General Ledger",
    SALES: "Sales Ledger",
    PURCHASES: "Purchases Ledger"
}

DROPDOWN = [
    ("", "ALL"),
    (GENERAL, "General Ledger"),
    (SALES, "Sales Ledger"),
    (PURCHASES, "Purchases Ledger")
]

SEARCH_DROPDOWN = [
    (GENERAL, "General Ledger"),
    (SALES, "Sales Ledger"),
    (PURCHASES, "Purchases Ledger")
]

ALL = frozenset((GENERAL, SALES, PURCHASES))