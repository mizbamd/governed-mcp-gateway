package io.reference.mcp.redaction;

import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;

public class PayloadRedactor {

    private final RedactionPolicy policy;

    public PayloadRedactor(RedactionPolicy policy) {
        this.policy = policy;
    }

    public static PayloadRedactor forRuleSet(RedactionRuleSet ruleSet) {
        return new PayloadRedactor(RedactionPolicy.forRuleSet(ruleSet));
    }

    public Map<String, Object> redact(Map<String, Object> payload) {
        Map<String, Object> copy = new LinkedHashMap<>();
        for (Map.Entry<String, Object> entry : payload.entrySet()) {
            String key = entry.getKey();
            Object value = entry.getValue();
            if (policy.sensitiveKeys().contains(key)) {
                copy.put(key, policy.replacement());
            } else if (value instanceof Map<?, ?> nested) {
                copy.put(key, redact(castMap(nested)));
            } else if (value instanceof List<?> list) {
                copy.put(key, redactList(list));
            } else if (value instanceof String text) {
                copy.put(key, redactStringValue(text));
            } else {
                copy.put(key, value);
            }
        }
        return copy;
    }

    private List<Object> redactList(List<?> list) {
        return list.stream()
                .map(element -> {
                    if (element instanceof Map<?, ?> nested) {
                        return redact(castMap(nested));
                    }
                    if (element instanceof String text) {
                        return redactStringValue(text);
                    }
                    return element;
                })
                .toList();
    }

    private String redactStringValue(String text) {
        String result = text;
        for (var pattern : policy.valuePatterns()) {
            result = pattern.matcher(result).replaceAll(policy.replacement());
        }
        return result;
    }

    @SuppressWarnings("unchecked")
    private static Map<String, Object> castMap(Map<?, ?> nested) {
        return (Map<String, Object>) nested;
    }
}
