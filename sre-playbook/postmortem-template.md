# Postmortem: [Incident Title]

**Date of incident:** YYYY-MM-DD
**Severity:** SEV1 / SEV2 / SEV3
**Duration:** HH:MM (start) — HH:MM (resolved)
**Authors:** [names]
**Status:** Draft / In review / Final

> This is a **blameless** postmortem. The goal is to understand systemic
> conditions that allowed the incident to happen, not to assign fault to
> an individual. Assume everyone involved made reasonable decisions given
> what they knew at the time.

## Summary

One paragraph: what broke, who/what was affected, how it was resolved.

## Impact

- Users/requests affected (rough %, or absolute count if known)
- Error budget consumed (reference the relevant SLO and burn-rate alert that fired)
- Revenue/SLA impact if applicable
- Duration of user-visible impact vs. total incident duration

## Timeline

All times in UTC.

| Time | Event |
|------|-------|
| 14:02 | Deploy of service X v1.4.2 begins |
| 14:05 | Fast-burn alert fires for `checkout-availability` SLO |
| 14:07 | On-call acknowledges page |
| 14:12 | IC declared, incident channel opened |
| 14:20 | Root cause identified as v1.4.2 config regression |
| 14:23 | Rollback initiated |
| 14:31 | Burn-rate alert clears (both windows) |
| 14:35 | Incident resolved |

## Root cause

What was the actual mechanism of failure? Go one or two levels past the immediate trigger — "a bad deploy" is a trigger, not a root cause; "the deploy pipeline had no automated check for X" is closer to root cause.

## What went well

- Concrete, specific things — not "good communication" but "IC posted updates every 15 minutes, which kept stakeholders from pinging individually."

## What went poorly

- Concrete, specific things — e.g. "the burn-rate alert fired but the runbook link in the alert annotation was stale."

## Where we got lucky

Things that could have made this worse but didn't, by chance rather than by design. Worth turning into real safeguards.

## Action items

| Action | Owner | Priority | Ticket |
|--------|-------|----------|--------|
| Add automated config validation to deploy pipeline | @owner | P1 | LINK |
| Update runbook link in alert annotation | @owner | P2 | LINK |
| Add canary stage before full rollout | @owner | P1 | LINK |

Every action item needs an owner and a ticket — "we should be more careful" is not an action item.
