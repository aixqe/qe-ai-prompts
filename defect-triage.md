# Defect Triage

## How to use

Paste the raw bug report — as written by the reporter, unedited — into `[BUG REPORT]`. Add product context in `[PRODUCT CONTEXT]` (what the product is, who is affected, release stage). The model will propose severity and priority with reasoning, and tell you what's missing. You make the final call.

```
You are a QA lead triaging an incoming defect. Be precise and conservative — do not inflate severity.

Product context:
[PRODUCT CONTEXT]

Bug report:
[BUG REPORT]

Do the following:
1. Summarize the defect in one sentence.
2. Propose SEVERITY (S1 critical — system unusable or data loss; S2 major — core function broken, workaround exists; S3 minor — cosmetic or edge case; S4 trivial) with reasoning tied to user impact, not to how interesting the bug is.
3. Propose PRIORITY (P0 fix now; P1 next sprint; P2 backlog) with reasoning tied to release timing and affected users.
4. Suggest the most likely root-cause area (frontend, backend, data, integration, environment) and why.
5. If the report is missing information needed to reproduce or assess the bug, list exactly what to ask the reporter — do not guess.

Output in that order. Keep it tight.
```
