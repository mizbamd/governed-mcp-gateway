package io.reference.mcp;

import com.fasterxml.jackson.databind.ObjectMapper;
import io.reference.mcp.audit.AuditArgumentRedactor;
import io.reference.mcp.audit.AuditLog;
import io.reference.mcp.governance.PolicyEngine;
import io.reference.mcp.server.McpService;
import io.reference.mcp.tools.ToolRegistry;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;

import java.util.Map;

import static org.assertj.core.api.Assertions.assertThat;

class McpServiceTest {

    private McpService service;
    private AuditLog audit;

    @BeforeEach
    void setup() {
        audit = new AuditLog();
        service = new McpService(new ToolRegistry(), new PolicyEngine(), audit,
                new AuditArgumentRedactor(), new ObjectMapper());
    }

    private Map<String, Object> call(Map<String, Object> params) {
        return service.handle(Map.of("jsonrpc", "2.0", "id", 1, "method", "tools/call", "params", params));
    }

    @Test
    @SuppressWarnings("unchecked")
    void initializeAndListTools() {
        Map<String, Object> init = service.handle(Map.of("id", 1, "method", "initialize"));
        assertThat(((Map<String, Object>) init.get("result")).get("protocolVersion")).isEqualTo("2024-11-05");

        Map<String, Object> list = service.handle(Map.of("id", 2, "method", "tools/list"));
        var tools = (java.util.List<Map<String, Object>>) ((Map<String, Object>) list.get("result")).get("tools");
        assertThat(tools).extracting(t -> t.get("name"))
                .contains("get_account_balance", "post_payment", "search_docs", "propose_price_change",
                        "lookup_supplier", "lookup_location", "lookup_item_cost");
    }

    @Test
    @SuppressWarnings("unchecked")
    void readToolExecutesWithoutApproval() {
        Map<String, Object> response = call(Map.of(
                "name", "get_account_balance", "arguments", Map.of("account_id", "merchant-1")));
        Map<String, Object> result = (Map<String, Object>) response.get("result");
        assertThat(result.get("isError")).isEqualTo(false);
    }

    @Test
    @SuppressWarnings("unchecked")
    void writeToolRequiresApprovalThenExecutes() {
        Map<String, Object> first = (Map<String, Object>) call(Map.of(
                "name", "post_payment",
                "arguments", Map.of("debit_account", "funding-1", "credit_account", "merchant-1", "amount", 10)
        )).get("result");
        assertThat(first.get("approvalRequired")).isEqualTo(true);
        String token = String.valueOf(first.get("approvalToken"));

        Map<String, Object> second = (Map<String, Object>) call(Map.of(
                "name", "post_payment",
                "arguments", Map.of("debit_account", "funding-1", "credit_account", "merchant-1", "amount", 10),
                "approvalToken", token
        )).get("result");
        assertThat(String.valueOf(((java.util.List<Map<String, Object>>) second.get("content")).get(0).get("text")))
                .contains("posted");
    }

    @Test
    void trustedRoleSkipsApproval() {
        @SuppressWarnings("unchecked")
        Map<String, Object> result = (Map<String, Object>) call(Map.of(
                "name", "post_payment", "role", "system-operator",
                "arguments", Map.of("debit_account", "funding-1", "credit_account", "merchant-1", "amount", 5)
        )).get("result");
        assertThat(result.get("isError")).isEqualTo(false);
    }

    @Test
    void unknownRoleIsDenied() {
        Map<String, Object> response = call(Map.of(
                "name", "get_account_balance", "role", "intruder",
                "arguments", Map.of("account_id", "merchant-1")));
        assertThat(response).containsKey("error");
    }

    @Test
    void auditLogIsHashChainedAndVerifiable() {
        call(Map.of("name", "get_account_balance", "arguments", Map.of("account_id", "merchant-1")));
        call(Map.of("name", "search_docs", "arguments", Map.of("query", "settlement")));
        assertThat(audit.entries()).hasSize(2);
        assertThat(audit.verify()).isTrue();
    }

    @Test
    @SuppressWarnings("unchecked")
    void retailMerchandisingToolsResolveMockCatalog() {
        Map<String, Object> supplier = (Map<String, Object>) call(Map.of(
                "name", "lookup_supplier", "arguments", Map.of("legacy_supplier_id", "88421"))).get("result");
        assertThat(supplier.get("isError")).isEqualTo(false);

        Map<String, Object> location = (Map<String, Object>) call(Map.of(
                "name", "lookup_location", "arguments", Map.of("location_nbr", 4701))).get("result");
        assertThat(location.get("isError")).isEqualTo(false);

        Map<String, Object> cost = (Map<String, Object>) call(Map.of(
                "name", "lookup_item_cost",
                "arguments", Map.of("club_nbr", 4701, "item_nbr", 10001))).get("result");
        assertThat(cost.get("isError")).isEqualTo(false);
    }

    @Test
    void auditHashesRedactedArguments() {
        call(Map.of("name", "search_docs", "arguments", Map.of(
                "query", "settlement", "pan", "4111111111111111")));
        call(Map.of("name", "search_docs", "arguments", Map.of(
                "query", "settlement", "pan", "4222222222222222")));
        assertThat(audit.entries()).hasSize(2);
        assertThat(audit.entries().get(0).argumentsHash())
                .isEqualTo(audit.entries().get(1).argumentsHash());
        assertThat(audit.verify()).isTrue();
    }
}
