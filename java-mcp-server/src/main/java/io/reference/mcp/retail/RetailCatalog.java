package io.reference.mcp.retail;

import java.util.LinkedHashMap;
import java.util.Map;

/** Mock retail catalog mirroring supplier (#1), location (#2), and cost ledger (#5) API shapes. */
public final class RetailCatalog {

    private static final Map<String, Map<String, Object>> SUPPLIERS = Map.of(
            "88421", Map.of(
                    "legacy_supplier_id", "88421",
                    "golden_id", "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
                    "canonical_name", "Pacific Fresh Produce Co.",
                    "country_code", "US",
                    "relationship_type", "DIRECT",
                    "status", "ACTIVE"),
            "55201", Map.of(
                    "legacy_supplier_id", "55201",
                    "golden_id", "f0e1d2c3-b4a5-6789-0123-456789abcdef",
                    "canonical_name", "Summit Household Brands",
                    "country_code", "US",
                    "relationship_type", "BROKER",
                    "status", "ACTIVE"));

    private static final Map<Integer, Map<String, Object>> LOCATIONS = Map.of(
            4701, Map.of(
                    "location_nbr", 4701,
                    "site_name", "Club 4701 — Northwest",
                    "base_division", "S",
                    "region", 12,
                    "market", 340,
                    "lifecycle_status", "OPEN",
                    "cost_zone", "NW-12"),
            6288, Map.of(
                    "location_nbr", 6288,
                    "site_name", "Club 6288 — Gulf Coast",
                    "base_division", "S",
                    "region", 8,
                    "market", 210,
                    "lifecycle_status", "OPEN",
                    "cost_zone", "GC-08"));

    private static final Map<String, Map<String, Object>> ITEM_COSTS = Map.of(
            "4701:10001", Map.of(
                    "club_nbr", 4701,
                    "item_nbr", 10001,
                    "unit_cost", 4.27,
                    "currency", "USD",
                    "effective_date", "2026-06-01",
                    "supplier_legacy_id", "88421",
                    "cost_zone", "NW-12"),
            "4701:20055", Map.of(
                    "club_nbr", 4701,
                    "item_nbr", 20055,
                    "unit_cost", 12.89,
                    "currency", "USD",
                    "effective_date", "2026-07-01",
                    "supplier_legacy_id", "55201",
                    "cost_zone", "NW-12"),
            "6288:10001", Map.of(
                    "club_nbr", 6288,
                    "item_nbr", 10001,
                    "unit_cost", 4.41,
                    "currency", "USD",
                    "effective_date", "2026-06-01",
                    "supplier_legacy_id", "88421",
                    "cost_zone", "GC-08"));

    private RetailCatalog() {
    }

    public static Map<String, Object> lookupSupplier(String legacySupplierId) {
        Map<String, Object> record = SUPPLIERS.get(legacySupplierId);
        if (record == null) {
            return Map.of("found", false, "legacy_supplier_id", legacySupplierId);
        }
        Map<String, Object> response = new LinkedHashMap<>(record);
        response.put("found", true);
        return response;
    }

    public static Map<String, Object> lookupLocation(int locationNbr) {
        Map<String, Object> record = LOCATIONS.get(locationNbr);
        if (record == null) {
            return Map.of("found", false, "location_nbr", locationNbr);
        }
        Map<String, Object> response = new LinkedHashMap<>(record);
        response.put("found", true);
        return response;
    }

    public static Map<String, Object> lookupItemCost(int clubNbr, int itemNbr) {
        Map<String, Object> record = ITEM_COSTS.get(clubNbr + ":" + itemNbr);
        if (record == null) {
            return Map.of("found", false, "club_nbr", clubNbr, "item_nbr", itemNbr);
        }
        Map<String, Object> response = new LinkedHashMap<>(record);
        response.put("found", true);
        return response;
    }
}
