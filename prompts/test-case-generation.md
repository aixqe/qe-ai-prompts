# Test Case Generation

## How to use

Paste your user story, acceptance criteria, or requirements section into `[REQUIREMENTS]`. Tell the model your application context in `[APP CONTEXT]` (what the app does, who uses it, tech stack if relevant) and your preferred output format in `[FORMAT]` (e.g. Gherkin, numbered test steps, or a table). Paste the entire prompt, review every generated case, and delete or fix anything that doesn't match your domain — the model doesn't know your business rules.

```
You are a senior QA engineer writing test cases for review, not final sign-off.

Application context:
[APP CONTEXT]

Requirements:
[REQUIREMENTS]

Generate test cases in this format: [FORMAT]

Rules:
1. Cover the happy path, boundary values, and negative cases. For every input field, include at least one invalid-input case.
2. Tag each case with a priority: P0 (blocks release), P1 (core functionality), P2 (edge case).
3. Number preconditions explicitly where a case depends on prior state (logged in, data exists, etc.).
4. If any requirement is ambiguous, contradictory, or untestable, do NOT guess — list it under "Questions for the product owner" instead of writing a case for it.
5. Keep each case independent: no case may depend on another case's execution order.

Output the test cases first, then the questions list. No commentary beyond that.
```
