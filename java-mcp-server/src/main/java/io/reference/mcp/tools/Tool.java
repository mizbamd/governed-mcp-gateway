package io.reference.mcp.tools;

import io.reference.mcp.governance.Sensitivity;

import java.util.Map;
import java.util.function.Function;

public record Tool(
        String name,
        String description,
        Map<String, Object> inputSchema,
        Sensitivity sensitivity,
        Function<Map<String, Object>, Map<String, Object>> handler) {

    public Map<String, Object> toMcp() {
        return Map.of(
                "name", name,
                "description", description,
                "inputSchema", inputSchema,
                "annotations", Map.of("sensitivity", sensitivity.name().toLowerCase()));
    }
}
