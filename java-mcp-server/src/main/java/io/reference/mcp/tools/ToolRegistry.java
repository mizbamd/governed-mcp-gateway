package io.reference.mcp.tools;

import io.reference.mcp.governance.Sensitivity;
import org.springframework.stereotype.Component;

import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
import java.util.concurrent.ConcurrentHashMap;

/**
 * Registers the tools exposed over MCP. Backends are mocked in-memory; in production these call the
 * ledger-service, pricing-orchestration, and agentic-rag-engine services of the reference architecture.
 */
@Component
public class ToolRegistry {

    private final Map<String, Tool> tools = new ConcurrentHashMap<>();
    private final Map<String, Double> balances = new ConcurrentHashMap<>(Map.of(
            "merchant-1", 1250.00, "funding-1", -1250.00));

    public ToolRegistry() {
        register(new Tool(
                "get_account_balance",
                "Read the current balance of a ledger account.",
                schema("account_id"),
                Sensitivity.READ,
                args -> Map.of(
                        "account_id", args.get("account_id"),
                        "balance", balances.getOrDefault(String.valueOf(args.get("account_id")), 0.0))));

        register(new Tool(
                "search_docs",
                "Hybrid search over the enterprise knowledge base.",
                schema("query"),
                Sensitivity.READ,
                args -> Map.of(
                        "query", args.get("query"),
                        "results", List.of("payments-settlement.md", "rag-architecture.md"))));

        register(new Tool(
                "post_payment",
                "Move funds between two ledger accounts. WRITE: requires approval.",
                schema("debit_account", "credit_account", "amount"),
                Sensitivity.WRITE,
                args -> {
                    String debit = String.valueOf(args.get("debit_account"));
                    String credit = String.valueOf(args.get("credit_account"));
                    double amount = ((Number) args.get("amount")).doubleValue();
                    balances.merge(debit, -amount, Double::sum);
                    balances.merge(credit, amount, Double::sum);
                    return Map.of("status", "posted", "debit_account", debit,
                            "credit_account", credit, "amount", amount);
                }));

        register(new Tool(
                "propose_price_change",
                "Propose a price change for a SKU. WRITE: requires approval.",
                schema("sku", "new_price"),
                Sensitivity.WRITE,
                args -> Map.of("status", "proposed", "sku", args.get("sku"),
                        "new_price", ((Number) args.get("new_price")).doubleValue())));
    }

    private void register(Tool tool) {
        tools.put(tool.name(), tool);
    }

    public Tool get(String name) {
        return tools.get(name);
    }

    public List<Tool> list() {
        return List.copyOf(tools.values());
    }

    private static Map<String, Object> schema(String... required) {
        Map<String, Object> properties = new LinkedHashMap<>();
        for (String field : required) {
            properties.put(field, Map.of("type", "string"));
        }
        return Map.of("type", "object", "properties", properties, "required", List.of(required));
    }
}
