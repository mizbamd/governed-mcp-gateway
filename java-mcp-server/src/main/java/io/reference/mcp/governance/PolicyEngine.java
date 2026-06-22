package io.reference.mcp.governance;

import org.springframework.stereotype.Component;

import java.util.Set;

/**
 * Role-based policy mirroring the Python server: READ is allowed for known roles, WRITE requires
 * human approval unless the caller holds a trusted role, unknown roles are denied.
 */
@Component
public class PolicyEngine {

    public enum Decision {ALLOW, DENY, REQUIRE_APPROVAL}

    public record PolicyDecision(Decision decision, String reason) {
    }

    private final Set<String> trustedRoles = Set.of("system-operator");
    private final Set<String> knownRoles = Set.of("analyst", "agent", "system-operator");

    public PolicyDecision evaluate(String role, Sensitivity sensitivity) {
        if (!knownRoles.contains(role)) {
            return new PolicyDecision(Decision.DENY, "unknown role '" + role + "'");
        }
        if (sensitivity == Sensitivity.READ) {
            return new PolicyDecision(Decision.ALLOW, "read access permitted");
        }
        if (trustedRoles.contains(role)) {
            return new PolicyDecision(Decision.ALLOW, "role '" + role + "' trusted for writes");
        }
        return new PolicyDecision(Decision.REQUIRE_APPROVAL, "write requires human approval");
    }
}
