# On-Call & Escalation Guide

## On-call expectations

- **Ack SLA:** acknowledge a page within 5 minutes during on-call hours.
- **Handoff:** primary on-call reviews open incidents, muted alerts, and any in-flight action items with the incoming on-call at shift change. A handoff with no verbal/written summary is not a handoff.
- **Alert fatigue is a bug, not a fact of life.** If an alert fires and the response is consistently "ignore it," fix or delete the alert — don't normalize ignoring pages. Multi-window burn-rate alerting (long + short window agreement) exists specifically to cut this kind of noise; a page-worthy alert should page rarely and mean something when it does.

## Escalation path

1. **Primary on-call** — first responder, owns triage and initial mitigation.
2. **Secondary on-call** — paged automatically if primary doesn't ack within the SLA, or pulled in by primary for a second pair of hands on a SEV1/SEV2.
3. **Team lead / EM** — looped in for SEV1, for incidents needing cross-team coordination, or for customer-impacting incidents needing executive comms.
4. **Incident Commander pool** (for orgs with a dedicated IC rotation) — takes the IC role for SEV1 so the primary responder can stay heads-down on mitigation.

Escalate early. Pulling in a second person 10 minutes into a SEV1 that resolves in 5 more minutes costs little; waiting 45 minutes to escalate a SEV1 that needed a second team from the start costs a lot.

## Alert -> action mapping

| Alert type | What it means | First action |
|------------|----------------|--------------|
| Fast-burn (short+long window, high multiplier) | Severe, acute error-budget burn | Page immediately, treat as candidate SEV1/SEV2, check recent deploys first |
| Medium-burn | Sustained, moderate burn | Page, investigate within the hour |
| Slow-burn | Slow leak over days | Ticket, no page; review during business hours |
| Single-window-only fast alert (long window not yet confirmed) | Possible early signal or noise | Watch, don't page yet — this is why multi-window exists |

## Runbook hygiene

- Every alert should link to a runbook (or explicitly note "no runbook needed, self-explanatory").
- Runbooks should be reviewed whenever the underlying service's architecture changes materially — a stale runbook during an incident is worse than no runbook, because it costs time to discover it's wrong.
- Keep runbooks in version control alongside the alerting rules that reference them, so they change together.
