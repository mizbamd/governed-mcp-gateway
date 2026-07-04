package io.reference.mcp.redaction;

import java.util.List;
import java.util.Set;
import java.util.regex.Pattern;

public record RedactionPolicy(
        Set<String> sensitiveKeys,
        List<Pattern> valuePatterns,
        String replacement) {

    public static RedactionPolicy retail() {
        return new RedactionPolicy(
                Set.of("unitCost", "targetMarginPct", "rebatePct", "lumpSumAmount"),
                List.of(),
                "[REDACTED]");
    }

    public static RedactionPolicy pci() {
        return new RedactionPolicy(
                Set.of(
                        "pan", "cardNumber", "creditCardNumber", "primaryAccountNumber",
                        "cvv", "cvc", "cardSecurityCode", "expiryDate", "expirationDate"),
                List.of(Pattern.compile("\\b\\d{13,19}\\b")),
                "[PCI_REDACTED]");
    }

    public static RedactionPolicy hipaa() {
        return new RedactionPolicy(
                Set.of(
                        "patientName", "patientId", "mrn", "medicalRecordNumber",
                        "ssn", "socialSecurityNumber", "dateOfBirth", "dob",
                        "diagnosis", "diagnosisCode", "procedureCode", "phi"),
                List.of(Pattern.compile("\\b\\d{3}-\\d{2}-\\d{4}\\b")),
                "[PHI_REDACTED]");
    }

    public static RedactionPolicy forRuleSet(RedactionRuleSet ruleSet) {
        return switch (ruleSet) {
            case RETAIL -> retail();
            case PCI -> pci();
            case HIPAA -> hipaa();
        };
    }
}
