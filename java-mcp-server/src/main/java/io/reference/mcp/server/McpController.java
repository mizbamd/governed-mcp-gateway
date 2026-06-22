package io.reference.mcp.server;

import io.reference.mcp.audit.AuditLog;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RestController;

import java.util.List;
import java.util.Map;

/** Exposes MCP JSON-RPC over HTTP plus a read-only audit view. */
@RestController
public class McpController {

    private final McpService service;
    private final AuditLog audit;

    public McpController(McpService service, AuditLog audit) {
        this.service = service;
        this.audit = audit;
    }

    @PostMapping("/mcp")
    public Map<String, Object> rpc(@RequestBody Map<String, Object> message) {
        return service.handle(message);
    }

    @GetMapping("/audit")
    public Map<String, Object> auditLog() {
        return Map.of("verified", audit.verify(), "entries", audit.entries());
    }
}
