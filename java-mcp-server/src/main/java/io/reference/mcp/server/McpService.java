package io.reference.mcp.server;

import com.fasterxml.jackson.databind.ObjectMapper;
import io.reference.mcp.audit.AuditLog;
import io.reference.mcp.governance.PolicyEngine;
import io.reference.mcp.governance.PolicyEngine.Decision;
import io.reference.mcp.tools.Tool;
import io.reference.mcp.tools.ToolRegistry;
import org.springframework.stereotype.Service;

import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.UUID;
import java.util.concurrent.ConcurrentHashMap;

/** Core MCP request handler: initialize, tools/list, tools/call -- governed and audited. */
@Service
public class McpService {

    static final String PROTOCOL_VERSION = "2024-11-05";

    private final ToolRegistry registry;
    private final PolicyEngine policy;
    private final AuditLog audit;
    private final ObjectMapper mapper;
    private final Map<String, Map<String, Object>> pendingApprovals = new ConcurrentHashMap<>();

    public McpService(ToolRegistry registry, PolicyEngine policy, AuditLog audit, ObjectMapper mapper) {
        this.registry = registry;
        this.policy = policy;
        this.audit = audit;
        this.mapper = mapper;
    }

    @SuppressWarnings("unchecked")
    public Map<String, Object> handle(Map<String, Object> message) {
        Object id = message.get("id");
        String method = String.valueOf(message.get("method"));
        Map<String, Object> params = (Map<String, Object>) message.getOrDefault("params", Map.of());

        return switch (method) {
            case "initialize" -> success(id, Map.of(
                    "protocolVersion", PROTOCOL_VERSION,
                    "capabilities", Map.of("tools", Map.of()),
                    "serverInfo", Map.of("name", "agent-mcp-java", "version", "1.0.0")));
            case "tools/list" -> success(id, Map.of(
                    "tools", registry.list().stream().map(Tool::toMcp).toList()));
            case "tools/call" -> handleToolsCall(id, params);
            default -> error(id, -32601, "unknown method: " + method);
        };
    }

    @SuppressWarnings("unchecked")
    private Map<String, Object> handleToolsCall(Object id, Map<String, Object> params) {
        String name = String.valueOf(params.get("name"));
        Map<String, Object> arguments = (Map<String, Object>) params.getOrDefault("arguments", Map.of());
        String role = String.valueOf(params.getOrDefault("role", "agent"));
        Object approvalToken = params.get("approvalToken");

        Tool tool = registry.get(name);
        if (tool == null) {
            return error(id, -32602, "unknown tool: " + name);
        }

        if (approvalToken != null && pendingApprovals.containsKey(approvalToken.toString())) {
            Map<String, Object> approvedArgs = pendingApprovals.remove(approvalToken.toString());
            Map<String, Object> result = tool.handler().apply(approvedArgs);
            audit.record(role, name, argsHash(approvedArgs), "approved", "executed");
            return success(id, toolResult(result));
        }

        PolicyEngine.PolicyDecision decision = policy.evaluate(role, tool.sensitivity());

        if (decision.decision() == Decision.DENY) {
            audit.record(role, name, argsHash(arguments), "deny", "blocked");
            return error(id, -32600, "denied: " + decision.reason());
        }

        if (decision.decision() == Decision.REQUIRE_APPROVAL) {
            String token = UUID.randomUUID().toString();
            pendingApprovals.put(token, arguments);
            audit.record(role, name, argsHash(arguments), "require_approval", "pending");
            Map<String, Object> result = new HashMap<>();
            result.put("content", List.of(Map.of("type", "text", "text", "approval_required")));
            result.put("approvalRequired", true);
            result.put("approvalToken", token);
            result.put("reason", decision.reason());
            result.put("isError", false);
            return success(id, result);
        }

        Map<String, Object> result = tool.handler().apply(arguments);
        audit.record(role, name, argsHash(arguments), "allow", "executed");
        return success(id, toolResult(result));
    }

    private Map<String, Object> toolResult(Map<String, Object> result) {
        try {
            return Map.of(
                    "content", List.of(Map.of("type", "text", "text", mapper.writeValueAsString(result))),
                    "isError", false);
        } catch (Exception e) {
            throw new IllegalStateException(e);
        }
    }

    private String argsHash(Map<String, Object> arguments) {
        try {
            return AuditLog.sha256(mapper.writeValueAsString(arguments));
        } catch (Exception e) {
            throw new IllegalStateException(e);
        }
    }

    private static Map<String, Object> success(Object id, Map<String, Object> result) {
        Map<String, Object> response = new HashMap<>();
        response.put("jsonrpc", "2.0");
        response.put("id", id);
        response.put("result", result);
        return response;
    }

    private static Map<String, Object> error(Object id, int code, String message) {
        Map<String, Object> response = new HashMap<>();
        response.put("jsonrpc", "2.0");
        response.put("id", id);
        response.put("error", Map.of("code", code, "message", message));
        return response;
    }
}
