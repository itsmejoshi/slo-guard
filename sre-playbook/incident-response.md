# Incident Response Runbook

## Severity levels

| Level | Definition | Examples | Response |
|-------|------------|----------|----------|
| SEV1 | Full outage or data loss affecting all/most users | Site down, payments failing globally, data corruption | Page on-call immediately, open incident channel, notify leadership within 15 min |
| SEV2 | Significant degradation affecting a subset of users or a core feature | Elevated error rate on checkout, regional outage, major feature broken | Page on-call, open incident channel within 15 min |
| SEV3 | Minor issue, workaround available, limited user impact | Non-critical feature degraded, isolated errors | Ticket + fix during business hours, no page |
| SEV4 | Cosmetic or negligible impact | UI glitch, log noise | Backlog |

## Roles during an incident

- **Incident Commander (IC):** Owns the response. Coordinates, makes calls, does not personally debug.
- **Communications Lead:** Owns status page updates and stakeholder comms so the IC and responders can focus on mitigation.
- **Subject Matter Expert(s) (SMEs):** Debug and mitigate. Report status to the IC, don't self-direct comms.

Small teams can combine IC + Comms; never combine IC + primary debugger on a SEV1/SEV2 — the person mitigating shouldn't also be fielding Slack questions.

## Response sequence

1. **Acknowledge.** Ack the page within the on-call SLA (commonly 5 minutes). Silence is the worst signal you can send.
2. **Assess and declare.** Confirm real impact (check dashboards/SLO burn-rate alerts, not just the page text), assign a severity, and declare the incident in the incident channel/tool.
3. **Stabilize before you diagnose.** If a recent deploy or config change correlates with the start of the incident, roll it back first and investigate root cause after service is restored. Mitigation beats explanation during an active incident.
4. **Communicate on a cadence.** Post an update at a fixed interval (e.g. every 30 minutes for SEV1) even if the update is "still investigating, no new info" — silence reads as "IC lost control."
5. **Confirm recovery.** Watch the relevant SLO/error-budget burn-rate alert clear (not just "error rate looks lower") before declaring resolved; burn-rate alerts are designed to require confirmation over a second window precisely to avoid premature all-clears.
6. **Resolve and schedule the postmortem.** Resolving the page is not resolving the incident — schedule the postmortem within 1-2 business days while memory is fresh.

## Using burn-rate alerts during an incident

Multi-window burn-rate alerts (see `slo-guard`) are designed to answer two questions responders always ask:

- **"How bad is this, really?"** — the burn-rate multiplier tells you how many times faster than "acceptable" the service is failing, independent of raw error-rate noise.
- **"Is it actually over?"** — because the alert requires both a long window and a short window to clear, a flapping recovery won't falsely signal "all clear."

If only the fast-burn (short-window) alert is firing and the slow-burn one is not, the issue is likely new and acute. If the slow-burn alert is firing but fast-burn is not, you likely have a longer-running, lower-grade leak worth a ticket rather than an all-hands page.

## Anti-patterns to avoid

- Debugging in the incident channel with no IC — it becomes noise no one can follow.
- Making the on-call engineer also write the customer-facing status update during a SEV1.
- Declaring resolution the instant the error graph dips, without waiting for the burn-rate confirmation window.
- Skipping the postmortem because "we know what happened" — the point is the process, not just the notes.
