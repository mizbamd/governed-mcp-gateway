from agent_mcp.audit import AuditLog
from agent_mcp.redaction import PayloadRedactor, RedactionRuleSet, redact_for_audit
from agent_mcp.server import McpServer

from test_server_and_client import rpc


def test_pci_redacts_pan_key():
    redacted = PayloadRedactor.for_rule_set(RedactionRuleSet.PCI).redact(
        {"pan": "4111111111111111", "note": "ok"})
    assert redacted["pan"] == "[PCI_REDACTED]"
    assert redacted["note"] == "ok"


def test_redact_for_audit_applies_all_rule_sets():
    redacted = redact_for_audit({
        "unitCost": 2.5,
        "pan": "4111111111111111",
        "ssn": "123-45-6789",
    })
    assert redacted["unitCost"] == "[REDACTED]"
    assert redacted["pan"] == "[PCI_REDACTED]"
    assert redacted["ssn"] == "[PHI_REDACTED]"


def test_audit_hashes_redacted_arguments():
    audit = AuditLog()
    server = McpServer(audit=audit)
    rpc(server, "tools/call", {
        "name": "search_docs",
        "arguments": {"query": "settlement", "pan": "4111111111111111"},
    })
    rpc(server, "tools/call", {
        "name": "search_docs",
        "arguments": {"query": "settlement", "pan": "4222222222222222"},
    })
    assert len(audit.entries) == 2
    assert audit.entries[0].arguments_hash == audit.entries[1].arguments_hash
    assert audit.verify() is True
