"""Mock retail catalog backing merchandising MCP tools.

Shapes mirror the sibling portfolio repos:
- supplier-golden-record-platform  (#1)
- location-reference-cache         (#2)
- item-cost-ledger-platform        (#5)

Production deployments call those services over HTTP; this module keeps the gateway runnable offline.
"""
from __future__ import annotations

SUPPLIERS: dict[str, dict] = {
    "88421": {
        "legacy_supplier_id": "88421",
        "golden_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
        "canonical_name": "Pacific Fresh Produce Co.",
        "country_code": "US",
        "relationship_type": "DIRECT",
        "status": "ACTIVE",
    },
    "55201": {
        "legacy_supplier_id": "55201",
        "golden_id": "f0e1d2c3-b4a5-6789-0123-456789abcdef",
        "canonical_name": "Summit Household Brands",
        "country_code": "US",
        "relationship_type": "BROKER",
        "status": "ACTIVE",
    },
}

LOCATIONS: dict[int, dict] = {
    4701: {
        "location_nbr": 4701,
        "site_name": "Club 4701 — Northwest",
        "base_division": "S",
        "region": 12,
        "market": 340,
        "lifecycle_status": "OPEN",
        "cost_zone": "NW-12",
    },
    6288: {
        "location_nbr": 6288,
        "site_name": "Club 6288 — Gulf Coast",
        "base_division": "S",
        "region": 8,
        "market": 210,
        "lifecycle_status": "OPEN",
        "cost_zone": "GC-08",
    },
}

ITEM_COSTS: dict[tuple[int, int], dict] = {
    (4701, 10001): {
        "club_nbr": 4701,
        "item_nbr": 10001,
        "unit_cost": 4.27,
        "currency": "USD",
        "effective_date": "2026-06-01",
        "supplier_legacy_id": "88421",
        "cost_zone": "NW-12",
    },
    (4701, 20055): {
        "club_nbr": 4701,
        "item_nbr": 20055,
        "unit_cost": 12.89,
        "currency": "USD",
        "effective_date": "2026-07-01",
        "supplier_legacy_id": "55201",
        "cost_zone": "NW-12",
    },
    (6288, 10001): {
        "club_nbr": 6288,
        "item_nbr": 10001,
        "unit_cost": 4.41,
        "currency": "USD",
        "effective_date": "2026-06-01",
        "supplier_legacy_id": "88421",
        "cost_zone": "GC-08",
    },
}


def lookup_supplier(legacy_supplier_id: str) -> dict:
    record = SUPPLIERS.get(legacy_supplier_id)
    if record is None:
        return {"found": False, "legacy_supplier_id": legacy_supplier_id}
    return {"found": True, **record}


def lookup_location(location_nbr: int) -> dict:
    record = LOCATIONS.get(location_nbr)
    if record is None:
        return {"found": False, "location_nbr": location_nbr}
    return {"found": True, **record}


def lookup_item_cost(club_nbr: int, item_nbr: int) -> dict:
    record = ITEM_COSTS.get((club_nbr, item_nbr))
    if record is None:
        return {"found": False, "club_nbr": club_nbr, "item_nbr": item_nbr}
    return {"found": True, **record}
