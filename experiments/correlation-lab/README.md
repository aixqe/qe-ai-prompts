# Correlation lab: changed does not mean required

Companion experiment for AI x QE, planned 18 November 2026.
Python 3.10+, no packages, account, API key or external traffic required.

## Run step by step

1. Clone the repository:
   ```sh
   git clone https://github.com/aixqe/qe-ai-prompts.git
   ```
2. Open the experiment directory:
   ```sh
   cd qe-ai-prompts/experiments/correlation-lab
   ```
3. Run seven replay cases, twenty fresh sessions per case:
   ```sh
   python3 lab.py --trials 20 --output results-local
   ```
   Windows users can use `py -3` in place of `python3`.
4. Read `results-local/captures.json` and `results-local/replay-results.json`.
5. Give the captures and the [review prompt](../../prompts/performance-correlation-review.md)
   to your chosen AI. First withhold server source: necessity should remain uncertain.
   Then supply `lab.py` as the disclosed application contract. Compare its recommendations
   with `results/assistant-plan.json` and falsify them through the replay cases.

Optional k6 example, after installing k6 separately:

1. Start the local server in one terminal:
   ```sh
   python3 lab.py --serve
   ```
2. In another terminal run:
   ```sh
   k6 run examples/correlated.js
   ```

The Python replay was executed here; the k6 example was not runtime-tested in the authoring
environment because k6 was unavailable. This server is a functional teaching fixture, not a
performance target or production authentication implementation. Restart it between long
interactive sessions; unsubmitted demo sessions remain in memory until restart.

## Design and ground truth

Each GET creates a new session cookie, CSRF token, timestamp with nonce, HMAC signature and
irrelevant trace ID. The POST checks the same session, token, timestamp, signature, and
constant `flow=demo-login`. It deliberately ignores `trace_id`. No credentials are involved;
`authenticated=true` is a synthetic business assertion. Every submitted session is consumed.
Attribute order is value-before-name to demonstrate why simple HTML regex can be brittle.

| Case | Expected accepted / 20 | What it isolates |
|---|---:|---|
| Stale fields without recorded session | 0 | Recorded replay fails; does not isolate token cause |
| Fresh cookie, stale fields | 0 | Cookie handling alone is insufficient |
| Fresh cookie + CSRF, stale timestamp pair | 0 | One extractor is insufficient |
| Fresh cookie/CSRF/timestamp, old signature | 0 | Linked values must match |
| Fresh fields without cookie | 0 | Body extraction cannot replace session handling |
| Fresh values, missing static flow | 0 | Unchanged can still be required |
| Fresh values + flow, no trace ID | 20 | Changing can be irrelevant |

The checked-in results were generated on 11 November 2026. All 140 replay outcomes matched
the expected acceptance/rejection. This is a controlled replay demonstration, not an AI
accuracy benchmark, capacity test, speedup claim, security test or evidence about GitHub login.
The candidate plan was reviewed by the authoring ChatGPT assistant with the server contract
visible. The harness contains that frozen plan; it does not call an LLM. It is not a blind
model evaluation. No model version, latency, token cost or manual baseline was measured.

## How to measure AI value next

Freeze a prompt and record provider, exact model identifier, date, settings, input hash and
raw answer. Use separate development and held-out journeys, reviewed ground truth and
multiple independent runs. Count required dependencies found/missed, unnecessary changes,
replay failures, active engineering minutes and review/rework/API cost. Compare against
manual work and tool-native correlation on equivalent journeys. Don't use this toy server
to claim production ROI.

## Other tool equivalents

- JMeter: HTTP Cookie Manager; CSS Selector Extractor beneath GET `/login`;
  selector `input[name="authenticity_token"]`, attribute `value`, variable `AuthToken`,
  match 1, default `NOT_FOUND`. Assert extraction before POST; repeat for the pair.
  Send `${AuthToken}` in the form. Preserve `flow`.
- LoadRunner Web HTTP/HTML: use an HTML-aware extractor supported by your version,
  register extraction **before** the GET returning the token, validate the match,
  then send `{AuthToken}`. Maintain cookies and encode form values correctly.
- k6: see the complete local smoke example; session handling is per VU.

## Sources checked 11 November 2026

- [k6 correlation](https://grafana.com/docs/k6/latest/examples/correlation-and-dynamic-data/)
- [k6 Studio HTTP tests and Assistant autocorrelation](https://grafana.com/docs/k6/latest/k6-studio/get-started/create-an-http-test/)
- [Apache JMeter components](https://jmeter.apache.org/usermanual/component_reference.html)
- [Gatling AI and Playwright](https://docs.gatling.io/tutorials/create-with-ai/playwright-recorder/)
- [OpenText 26.1 scripting, analysis and MCP](https://community.opentext.com/devops-cloud/b/devops-blog/posts/opentext-performance-engineering-26-1-ai-and-mcp-in-scripting-analysis-and-agent-workflows)

Read the [publication draft](newsletter.md) and [image briefs](image-briefs.md).
