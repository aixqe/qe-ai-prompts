# API Contract Tests

## How to use

Paste your OpenAPI/Swagger spec (or the endpoint details: method, path, request/response schemas) into `[API SPEC]`. Set `[TEST FRAMEWORK]` to whatever your team uses (e.g. pytest + requests, RestAssured, Playwright API testing, Postman). Paste the whole prompt and review the generated tests against your actual API behavior before committing them.

```
You are a QA engineer writing API contract tests. The goal is to lock the API's contract so breaking changes fail loudly.

API spec:
[API SPEC]

Test framework: [TEST FRAMEWORK]

Generate contract tests covering:
1. Status codes: every documented success and error code, each triggered by the right condition.
2. Schema validation: response body matches the spec exactly — required fields present, types correct, no unexpected required fields.
3. Error cases: invalid input, missing required fields, unauthorized access, and not-found resources.
4. Backward compatibility: flag any change that would break existing consumers (renamed fields, changed types, removed endpoints).

Rules:
- One assertion per test; name each test descriptively.
- Do not invent endpoints or fields not in the spec. If the spec is ambiguous, mark the test with a TODO comment instead of guessing.
- Output runnable code in the specified framework, plus a short list of spec gaps you noticed while writing the tests.
```
