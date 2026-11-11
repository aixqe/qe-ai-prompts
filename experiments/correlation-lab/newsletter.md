# AI can suggest the correlation. Replay has to prove it.

*AI x QE · Planned for 18 November 2026 · DJ*

You record a performance script on Monday. It runs clean.

On Tuesday, it fails.

The script has not changed. The session has.

A recorded token can be valid for one session and useless in the next. You do not even need to wait until Tuesday. The next replay may be enough.

This is **correlation**: capture a value returned by the server and reuse it in a later request, in the right session and at the right time.

Anyone who has worked on protocol-level performance scripts knows the routine. Find the value. Find its source. Add the extractor. Replace the recorded value. Replay. Repeat for the next failure.

AI can help with that work. But there is a gap between spotting a changing value and proving that your script needs it.

That gap became the most useful part of this experiment.

## First, a correction to an attractive idea

Here is a tempting shortcut:

> Capture the same page twice. Ask AI what changed. Your correlation list writes itself.

Almost.

Your **candidate list** writes itself.

A changing value might be a session token. It might also be a trace ID, a rotating banner, or a timestamp the next request never uses. An unchanged value can still be required.

Two page responses cannot establish the complete dependency chain. You also need to inspect later requests and verify what happens when you replay them.

There is another practical catch: saving a page does not normally save its response headers. You may see a hidden form token and miss the cookie that makes it valid.

So I changed the experiment. Rather than make claims about a public login page, I used a small local application whose rules we could inspect and test.

## The experiment: propose, then break the proposal

The companion GitHub lab runs on your laptop with Python. It needs no account, password, API key or external website.

The local page issues:

- A session cookie.
- A hidden `authenticity_token`.
- A timestamp and a matching signature, named `timestamp_secret` in the demo.
- A changing `trace_id`.
- A constant `flow=demo-login` field.

The timestamp/signature relationship is deliberately implemented in this demo. Similar-looking fields on another application do not prove the same relationship.

We captured the page in two independent sessions. Four hidden field values changed, along with the session cookie. The `flow` value stayed the same.

Then we reviewed the captures and the local application's validation rules with AI assistance. The proposed handling was straightforward:

| Value | Proposed handling |
|---|---|
| Session cookie | Let the configured cookie manager carry it within the same virtual user's session |
| Authenticity token | Extract from the current response and send it back |
| Timestamp and signature | Extract together from the same response and session |
| Trace ID | Omit; this demo does not validate it |
| Flow | Preserve the required value, even though it did not change |

That table was still a proposal. The next step was to try to prove it wrong.

## What actually happened

On 11 November, we ran seven cases, each with 20 attempts using fresh sessions.

| Replay case | Accepted |
|---|---:|
| Recorded fields without the original session | 0/20 |
| Fresh cookie, recorded form values | 0/20 |
| Fresh cookie and CSRF token, stale timestamp pair | 0/20 |
| Fresh values, but a signature from another session | 0/20 |
| Fresh form values without the session cookie | 0/20 |
| Fresh values, but the unchanged `flow` field removed | 0/20 |
| Fresh cookie, token and matching pair; flow retained; trace ID omitted | 20/20 |

All 140 outcomes matched the expected acceptance or rejection. The test checked both HTTP status and the demo's `authenticated` result.

The point is not that 20 successful requests make a production-ready script. They do not.

The point is that we tested the recommendation against known rules and deliberate failures.

The changing trace ID was unnecessary. The unchanged flow field was necessary. The signature could not be mixed with a different session's values.

**Changed does not mean required. Unchanged does not mean optional.**

[Image 1: two captures, with the changing trace ID and unchanged flow field clearly labelled.]

## What this proves about AI—and what it does not

The AI-assisted review produced a plan that agreed with the controlled application's rules. Replay supported that plan.

This was an assisted walkthrough, with the server contract visible. It was not a blind model benchmark. The replay harness uses a frozen plan and does not call an LLM.

We did not measure manual effort, AI latency, model accuracy across applications or financial return. There is no honest percentage saving to report from this experiment.

A structural diff can find these changing fields without AI. The useful AI question comes after that:

*Where does each value come from, where is it used, what scope does it belong to, and how would we test the recommendation?*

AI can help assemble that explanation and draft the extractor. It can also guess incorrectly. Passing replay with meaningful assertions is stronger evidence than a confident answer.

## The code is small. The checks matter.

In k6, the extraction can look like this:

```javascript
const page = http.get(`${base}/login`);
const fields = page.html().find('input[name="authenticity_token"]');
if (fields.size() !== 1) fail('Expected exactly one authenticity token');
const token = fields.attr('value');
if (!token) fail('Missing authenticity token');
```

Then send `token` in the next request, alongside the other required fields. Keep both requests in the same virtual user's session. The repository includes the complete local smoke script.

For JMeter, use an HTTP Cookie Manager and a CSS Selector Extractor on the response: selector `input[name="authenticity_token"]`, attribute `value`, variable `AuthToken`. Validate extraction, then reference `${AuthToken}` in the next request.

For LoadRunner Web HTTP/HTML scripts, register the supported extractor **before** the request that returns the value. Validate the extraction before submitting `{AuthToken}`.

An HTML parser avoids depending on whether `name` appears before `value` in the markup. A missing token should stop the iteration, not quietly fall back to yesterday's recording.

## How the wider job is changing

The change is bigger than writing scripts.

| Performance task | Where AI can help | What the engineer must establish |
|---|---|---|
| Workload design | Draft journeys and traffic mixes from requirements and telemetry | Whether volumes, pacing, data and concurrency represent real demand |
| Scripting | Draft scripts and propose correlation rules | Correct dependencies, sessions and business assertions |
| Maintenance | Suggest a patch after an application change | Whether it fixes the script or hides a real defect |
| Execution | Coordinate approved runs and collect evidence | Environment, load limits, duration and stop conditions |
| Analysis | Group failures and propose causes | Whether comparable runs and telemetry support the explanation |

There are real product capabilities behind parts of this. Grafana documents Assistant-based autocorrelation in k6 Studio. Gatling documents creating tests from Playwright sessions with AI. OpenText documents Aviator assistance for scripting and analysis, and MCP support for performance workflows.

Those are capability statements. They do not establish a universal productivity gain, and availability depends on the product, version and setup.

For me, the engineering rule stays the same: a green script is only useful if it exercises the right business transaction under a credible workload.

## Where agents fit

An assistant proposes a fix. An agent can also apply the patch, run a smoke test, inspect the result and prepare the next action.

That makes the validation loop more valuable—and makes its boundaries matter.

Give the agent a specific failing script, authorized local tools and explicit acceptance checks. Let it propose a patch and run a small replay. Save the before-and-after evidence. Review workload changes before moving to a larger run.

A correlation patch should not quietly remove an assertion, skip a failed transaction or lower concurrency to make the report green.

The useful output is a reviewable change with replay evidence. That gives the engineer something concrete to accept or reject.

[Image 2: a compact agent workflow with a failed replay looping back to patch review.]

## One more change: testing AI applications themselves

When the application calls an LLM or uses agents, response time is only part of the picture.

Your test plan may also need time to first token, end-to-end completion time, token consumption, cost per successful task, tool-call retries, rate-limit behaviour and task success under load.

A fast answer that fails the task is still a failure. Compare equivalent task mixes and record model versions, output lengths and cache conditions so you can interpret the results.

That is a separate experiment worth doing properly. This correlation lab does not measure it.

## Try it yourself

Start with the local lab:

1. Clone `aixqe/qe-ai-prompts`.
2. Open `experiments/correlation-lab`.
3. Run `python3 lab.py --trials 20 --output results-local`.
4. Give the saved captures to your AI and ask:

> Identify changing values and possible dependencies. Separate evidence from assumptions. For each value, explain what additional request evidence or replay test would establish whether it must be reused. Include unchanged fields that may still be required. Do not claim a successful replay without running one.

First use only the captures. Then provide the server rules. Watch how the answer should change as the evidence improves.

Use sanitized captures from your own authorized application when you move beyond the demo. Keep real credentials, cookies and personal data out of shared prompts and public repositories.

If you want to claim a saving, measure active engineering time, review and rework, replay failures and tool cost across several comparable journeys. Include manual work and your tool's existing correlation features as baselines.

**AI can shorten the investigation. Replay has to prove the script.**

Next edition: my AI journey, from the first experiments to the spec-driven model.

DJ

---

### Code and sources

- [Run the correlation lab](https://github.com/aixqe/qe-ai-prompts/tree/newsletter/performance-correlation-nov18/experiments/correlation-lab)
- [k6 correlation and dynamic data](https://grafana.com/docs/k6/latest/examples/correlation-and-dynamic-data/)
- [k6 Studio: create an HTTP test](https://grafana.com/docs/k6/latest/k6-studio/get-started/create-an-http-test/)
- [Apache JMeter component reference](https://jmeter.apache.org/usermanual/component_reference.html)
- [Gatling: create a test from Playwright with AI](https://docs.gatling.io/tutorials/create-with-ai/playwright-recorder/)
- [OpenText 26.1: scripting, analysis and agent workflows](https://community.opentext.com/devops-cloud/b/devops-blog/posts/opentext-performance-engineering-26-1-ai-and-mcp-in-scripting-analysis-and-agent-workflows)

Sources checked 11 November 2026. Local experiment results are in `results/replay-results.json`.
