# ADR-0002: Human-in-the-loop approval for write actions

- Status: Accepted
- Date: 2026-06-22

## Context
LLM agents are non-deterministic and susceptible to prompt injection. Allowing them to autonomously
execute writes against systems of record (move money, change prices) is an unacceptable risk for
most enterprises today.

## Decision
Classify every tool READ or WRITE. WRITE calls are not executed inline: the server returns an
`approvalRequired` response with a single-use `approvalToken`. Execution only occurs when the call is
replayed with a valid token, representing an out-of-band human (or trusted second system) approval.
A configurable trusted role can bypass approval for fully automated, low-risk paths.

## Consequences
- Positive: bounded blast radius; maker-checker control; injection-resistant.
- Negative: writes are not instantaneous; requires an approval UX/workflow integration in production.
