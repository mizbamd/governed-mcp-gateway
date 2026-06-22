package io.reference.mcp.audit;

import org.springframework.stereotype.Component;

import java.nio.charset.StandardCharsets;
import java.security.MessageDigest;
import java.util.ArrayList;
import java.util.HexFormat;
import java.util.List;

/**
 * Append-only, hash-chained audit log. Each entry hashes the previous entry's hash, so tampering
 * with any historical record invalidates every entry after it (verify() detects this).
 */
@Component
public class AuditLog {

    public record AuditEntry(long timestamp, String role, String tool, String argumentsHash,
                             String decision, String outcome, String prevHash, String entryHash) {
    }

    private final List<AuditEntry> entries = new ArrayList<>();

    public synchronized AuditEntry record(String role, String tool, String argumentsHash,
                                          String decision, String outcome) {
        String prevHash = entries.isEmpty() ? "genesis" : entries.get(entries.size() - 1).entryHash();
        long ts = System.currentTimeMillis();
        String entryHash = hash(ts, role, tool, argumentsHash, decision, outcome, prevHash);
        AuditEntry entry = new AuditEntry(ts, role, tool, argumentsHash, decision, outcome, prevHash, entryHash);
        entries.add(entry);
        return entry;
    }

    public synchronized boolean verify() {
        String prev = "genesis";
        for (AuditEntry e : entries) {
            String expected = hash(e.timestamp(), e.role(), e.tool(), e.argumentsHash(),
                    e.decision(), e.outcome(), prev);
            if (!e.prevHash().equals(prev) || !e.entryHash().equals(expected)) {
                return false;
            }
            prev = e.entryHash();
        }
        return true;
    }

    public synchronized List<AuditEntry> entries() {
        return List.copyOf(entries);
    }

    public static String sha256(String value) {
        try {
            MessageDigest digest = MessageDigest.getInstance("SHA-256");
            return HexFormat.of().formatHex(digest.digest(value.getBytes(StandardCharsets.UTF_8)));
        } catch (Exception e) {
            throw new IllegalStateException(e);
        }
    }

    private static String hash(long ts, String role, String tool, String argsHash,
                               String decision, String outcome, String prevHash) {
        return sha256(ts + "|" + role + "|" + tool + "|" + argsHash + "|" + decision + "|" + outcome + "|" + prevHash);
    }
}
