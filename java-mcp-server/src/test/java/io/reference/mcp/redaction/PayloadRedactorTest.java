package io.reference.mcp.redaction;

import org.junit.jupiter.api.Test;

import java.util.Map;

import static org.assertj.core.api.Assertions.assertThat;

class PayloadRedactorTest {

    @Test
    void pciRedactsPanKey() {
        Map<String, Object> redacted = PayloadRedactor.forRuleSet(RedactionRuleSet.PCI)
                .redact(Map.of("pan", "4111111111111111", "note", "ok"));
        assertThat(redacted.get("pan")).isEqualTo("[PCI_REDACTED]");
        assertThat(redacted.get("note")).isEqualTo("ok");
    }

    @Test
    void hipaaRedactsSsnPatternInNote() {
        Map<String, Object> redacted = PayloadRedactor.forRuleSet(RedactionRuleSet.HIPAA)
                .redact(Map.of("note", "member 123-45-6789"));
        assertThat(redacted.get("note")).isEqualTo("member [PHI_REDACTED]");
    }
}
