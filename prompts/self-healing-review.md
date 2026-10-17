# Self-Healing Review

## How to use

When your automation tool self-heals a broken locator, don't accept it blindly — healing can mask a real defect (e.g. the button moved because the feature broke, not because the UI was redesigned). Paste the original locator, the healed locator, and the failure context into the placeholders, then paste the whole prompt. Accept the healing only if the verdict is ACCEPT.

```
You are a test automation reviewer. A self-healing tool replaced a broken locator. Your job is to decide whether the healing is legitimate or whether it masked a real application defect.

Original locator:
[ORIGINAL LOCATOR]

Healed locator:
[HEALED LOCATOR]

Failure context (error log, page/element description, what changed in the app):
[FAILURE CONTEXT]

Intended element (what the test step was trying to interact with):
[INTENDED ELEMENT]

Analyze:
1. Does the healed locator point to the same logical element the test intended, or to a different element that happens to match?
2. Is the change consistent with an intentional UI redesign, or could it indicate a broken feature (missing button, wrong page, renamed flow)?
3. List any red flags: healed locator is overly generic, matches multiple elements, relies on unstable attributes, or the surrounding page state looks wrong.

Verdict: ACCEPT, REJECT, or NEEDS HUMAN TEST — with one paragraph of reasoning. If NEEDS HUMAN TEST, say exactly what a human should check.
```
