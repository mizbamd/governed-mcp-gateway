package io.reference.mcp.audit;

import io.reference.mcp.redaction.PayloadRedactor;
import io.reference.mcp.redaction.RedactionRuleSet;
import org.springframework.stereotype.Component;

import java.util.Map;

/** Applies RETAIL + PCI + HIPAA rule sets before tool arguments enter the audit hash chain. */
@Component
public class AuditArgumentRedactor {

    public Map<String, Object> redactForAudit(Map<String, Object> arguments) {
        Map<String, Object> current = arguments;
        for (RedactionRuleSet ruleSet : RedactionRuleSet.values()) {
            current = PayloadRedactor.forRuleSet(ruleSet).redact(current);
        }
        return current;
    }
}
