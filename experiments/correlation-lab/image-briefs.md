# Image suggestions for the 18 November edition

Use three figures at most. Keep large type, strong contrast and captions that survive mobile viewing.
Avoid robots, glowing brains and fabricated screenshots. Precise diagrams and result charts should
be drawn from the experiment data, rather than generated as pictures of data.

## 1. Cover: Yesterday's token. Today's failure.

Suggested canvas: 1600 × 900 (editorial working size; preview the crop in LinkedIn).
Dark navy background, white type, teal for fresh values, amber for review, muted red for rejection.
Two script cards: `Recorded token` and `Current session`. One deliberately mismatched token
connects to `403`; a correctly extracted token connects to `Accepted`.
Main title: **AI can suggest the correlation.**
Subtitle: **Replay has to prove it.**
Small footer: AI x QE | DJ | 18 Nov 2026.
Use schematic tokens such as TOKEN_A and TOKEN_B. No live secrets or vendor logos.
If generating decorative artwork, keep it abstract and add all exact labels separately.
Alt text: Two session cards show why a recorded token fails and a fresh correlated token succeeds.

## 2. Inline figure: Changed does not mean required

Draw a real vector/table figure showing two synthetic captures, side by side. Use shortened values
from results/captures.json or clearly marked schematic placeholders. Show these six rows:

| Item | Capture A | Capture B | Handling |
|---|---|---|---|
| Cookie | SESSION_A | SESSION_B | Cookie manager |
| CSRF | TOKEN_A | TOKEN_B | Extract |
| Timestamp | TIME_A | TIME_B | Extract together with signature |
| Signature | SIGN_A | SIGN_B | Extract together with timestamp |
| Trace ID | TRACE_A | TRACE_B | Omit in this demo |
| Flow | demo-login | demo-login | Retain: required |

Highlight the last two rows. Label this **Synthetic local demo**, not GitHub login.
Caption: The changing trace ID was optional. The unchanged flow value was required.
Alt text: Two synthetic captures show that changing data can be optional and constant data required.

## 3. Inline figure: Agent workflow with a replay gate

A compact top-down diagram: Captures + later requests → candidate plan → reviewable patch → smoke replay.
Branch: failed replay returns to patch review; passed replay goes to engineer review, then approved load run.
Attach visible evidence cards to the replay: extraction count, HTTP status, business assertion.
Caption: The agent proposes and tests a change. The engineer reviews the evidence before a larger run.
Alt text: A replay gate sends failed changes back for review and passing changes to engineer approval.

Optional replacement for figure 3: an exact horizontal bar chart from replay-results.json,
showing accepted attempts out of 20 for all seven cases. Title it **Replay acceptance in this local demo**.
Do not label it AI accuracy, performance improvement or 100% automation success.
