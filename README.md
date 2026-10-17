# QE AI Prompts

A library of copy-paste-ready prompt templates for using AI in quality engineering work: test design, defect triage, self-healing review, API testing, and regression risk assessment.

Each prompt is a starting point, not a finished product. Fill in the bracketed placeholders with your own context, review the output like you would a junior tester's work, and adapt the template as you learn what your models are good at.

## How to use

1. Open the prompt file you need.
2. Replace every `[PLACEHOLDER]` with your actual context (requirements, logs, specs).
3. Paste the whole thing into your AI assistant of choice.
4. Review the output critically — AI-generated tests that pass despite real bugs are a documented failure mode. The human review gate is policy, not preference.

## Contents

| Prompt | What it does |
|---|---|
| [test-case-generation](prompts/test-case-generation.md) | Generate test cases from a user story or requirements document |
| [self-healing-review](prompts/self-healing-review.md) | Review a self-healed locator and decide if the healing masked a real defect |
| [defect-triage](prompts/defect-triage.md) | Triage a bug report: severity, priority, and reasoning |
| [api-contract-tests](prompts/api-contract-tests.md) | Generate API contract tests from an OpenAPI spec |
| [regression-risk](prompts/regression-risk.md) | Assess regression risk of a code change and recommend what to test |
