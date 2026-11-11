import http from 'k6/http';
import { check, fail } from 'k6';

// Functional smoke only. The Python demo is not a load-test target.
export const options = { vus: 1, iterations: 20, thresholds: { checks: ['rate==1'] } };
const base = 'http://127.0.0.1:8765';

export default function () {
  const res = http.get(`${base}/login`);
  if (res.status !== 200) fail('GET /login failed');
  const doc = res.html();
  const payload = {};
  for (const name of ['authenticity_token', 'timestamp', 'timestamp_secret', 'flow']) {
    const elements = doc.find(`input[name="${name}"]`);
    if (elements.size() !== 1) fail(`Expected one ${name}`);
    const value = elements.attr('value');
    if (!value) fail(`Missing ${name}`);
    payload[name] = value;
  }
  // k6's per-VU cookie jar carries the session. trace_id is intentionally omitted.
  const login = http.post(`${base}/login`, payload);
  check(login, {
    'login accepted': r => r.status === 200,
    'business outcome authenticated': r => r.json('authenticated') === true,
  });
}
