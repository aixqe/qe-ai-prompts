"""Local-only correlation experiment. Python 3.10+, standard library only."""
import argparse
from collections import Counter
from datetime import datetime, timezone
from html import escape
from html.parser import HTMLParser
from http.cookiejar import CookieJar
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import hashlib
import hmac
import json
from pathlib import Path
import secrets
import threading
import urllib.error
import urllib.parse
import urllib.request


class Fields(HTMLParser):
    def __init__(self, body):
        super().__init__(convert_charrefs=True)
        self.values = {}
        self.feed(body)

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == 'input' and a.get('type') == 'hidden' and 'name' in a:
            if a['name'] in self.values:
                raise ValueError('Duplicate field: ambiguous extraction')
            self.values[a['name']] = a.get('value', '')


class LabServer(ThreadingHTTPServer):
    def __init__(self, address):
        super().__init__(address, Handler)
        self.sessions = {}
        self.secret = secrets.token_bytes(32)
        self.lock = threading.Lock()

    def issue(self):
        sid = secrets.token_hex(16)
        # Random nonce guarantees distinct pairs even inside the same clock tick.
        stamp = datetime.now(timezone.utc).isoformat() + ':' + secrets.token_hex(8)
        csrf = secrets.token_urlsafe(24)
        signature = hmac.new(self.secret, f'{sid}:{stamp}'.encode(), hashlib.sha256).hexdigest()
        with self.lock:
            self.sessions[sid] = (csrf, stamp)
        return sid, dict(authenticity_token=csrf, timestamp=stamp, timestamp_secret=signature,
                         trace_id=secrets.token_hex(8), flow='demo-login')


class Handler(BaseHTTPRequestHandler):
    def log_message(self, *args):
        pass

    def reply(self, status, body, cookie=None, content_type='application/json'):
        data = body.encode()
        self.send_response(status)
        self.send_header('Content-Type', content_type)
        self.send_header('Content-Length', str(len(data)))
        self.send_header('Cache-Control', 'no-store')
        if cookie:
            self.send_header('Set-Cookie', f'lab_session={cookie}; HttpOnly; SameSite=Lax; Path=/')
        self.end_headers()
        self.wfile.write(data)

    def do_GET(self):
        if self.path != '/login':
            return self.reply(404, '{}')
        sid, fields = self.server.issue()
        inputs = ''.join(f'<input value="{escape(v, quote=True)}" name="{k}" type="hidden">'
                         for k, v in fields.items())
        self.reply(200, f'<form action="/login" method="post">{inputs}<button>Continue</button></form>',
                   sid, 'text/html; charset=utf-8')

    def do_POST(self):
        if self.path != '/login':
            return self.reply(404, '{}')
        length = int(self.headers.get('Content-Length', '0'))
        if length > 16384:
            return self.reply(413, '{}')
        fields = urllib.parse.parse_qs(self.rfile.read(length).decode(), keep_blank_values=True)
        from http.cookies import SimpleCookie
        cookie = SimpleCookie(self.headers.get('Cookie', ''))
        sid = cookie['lab_session'].value if 'lab_session' in cookie else ''
        with self.server.lock:
            expected = self.server.sessions.pop(sid, None)  # one-use session
        def val(key):
            values = fields.get(key, [])
            return values[0] if len(values) == 1 else ''
        reason = 'accepted'
        if expected is None:
            reason = 'missing_or_consumed_session'
        elif not hmac.compare_digest(val('authenticity_token'), expected[0]):
            reason = 'csrf_mismatch'
        elif val('timestamp') != expected[1]:
            reason = 'timestamp_mismatch'
        elif not hmac.compare_digest(val('timestamp_secret'), hmac.new(
                self.server.secret, f'{sid}:{val("timestamp")}'.encode(), hashlib.sha256).hexdigest()):
            reason = 'signature_mismatch'
        elif val('flow') != 'demo-login':
            reason = 'missing_or_wrong_flow'
        self.reply(200 if reason == 'accepted' else 403,
                   json.dumps(dict(authenticated=reason == 'accepted', reason=reason)))


def client():
    return urllib.request.build_opener(urllib.request.HTTPCookieProcessor(CookieJar()))


def capture(opener, base):
    with opener.open(base + '/login', timeout=5) as response:
        body = response.read().decode()
        return dict(body=body, headers=dict(response.headers), fields=Fields(body).values)


def submit(opener, base, fields):
    request = urllib.request.Request(base + '/login', urllib.parse.urlencode(fields).encode())
    try:
        response = opener.open(request, timeout=5)
    except urllib.error.HTTPError as error:
        response = error
    with response:
        return dict(status=response.status, **json.loads(response.read()))


# Frozen assistant-reviewed plan; no model API runs in this script.
PLAN = dict(authenticity_token='extract', timestamp='extract', timestamp_secret='extract',
            trace_id='omit', flow='retain_constant', lab_session='cookie_manager')
CASES = {
    'stale_recording': False, 'cookie_only': False, 'csrf_only': False,
    'mixed_pair': False, 'no_cookie': False, 'omit_static_flow': False,
    'correlated_without_trace': True,
}


def experiment(trials, output):
    if trials < 1:
        raise ValueError('trials must be positive')
    server = LabServer(('127.0.0.1', 0))
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    base = f'http://127.0.0.1:{server.server_port}'
    output.mkdir(parents=True, exist_ok=True)
    try:
        a, b = capture(client(), base), capture(client(), base)
        changed = [k for k in a['fields'] if a['fields'][k] != b['fields'][k]]
        evidence = dict(capture_a=a, capture_b=b, changed_html_fields=changed,
                        session_cookie_changed=a['headers']['Set-Cookie'] != b['headers']['Set-Cookie'])
        # Synthetic local secrets only; these are not external account captures.
        (output / 'captures.json').write_text(json.dumps(evidence, indent=2) + '\n')
        (output / 'assistant-plan.json').write_text(json.dumps(PLAN, indent=2) + '\n')
        results = []
        for case, expected in CASES.items():
            responses = []
            for _ in range(trials):
                old_client, new_client = client(), client()
                old, new = capture(old_client, base)['fields'], capture(new_client, base)['fields']
                payload = dict(old if case in ('stale_recording', 'cookie_only') else new)
                sender = old_client if case == 'stale_recording' else new_client
                if case == 'stale_recording':
                    sender = client()  # previous recorded cookie is no longer carried
                elif case == 'csrf_only':
                    payload = dict(old, authenticity_token=new['authenticity_token'])
                elif case == 'mixed_pair':
                    payload['timestamp_secret'] = old['timestamp_secret']
                elif case == 'no_cookie':
                    sender = client()
                elif case == 'omit_static_flow':
                    payload.pop('flow')
                elif case == 'correlated_without_trace':
                    payload.pop('trace_id')
                result = submit(sender, base, payload)
                assert (result['status'] == 200 and result['authenticated']) == expected, (case, result)
                responses.append(result)
            results.append(dict(case=case, attempts=trials,
                                accepted=sum(r['authenticated'] for r in responses),
                                statuses=dict(Counter(str(r['status']) for r in responses)),
                                reasons=dict(Counter(r['reason'] for r in responses))))
        report = dict(executed_at_utc=datetime.now(timezone.utc).isoformat(), trials_per_case=trials,
                      environment='Python stdlib; localhost; synthetic one-use sessions',
                      ai_execution='Assistant-reviewed frozen plan; no model API, timing or accuracy benchmark',
                      results=results)
        (output / 'replay-results.json').write_text(json.dumps(report, indent=2) + '\n')
        print(json.dumps(report, indent=2))
    finally:
        server.shutdown()
        server.server_close()
        thread.join()


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--serve', action='store_true')
    parser.add_argument('--port', type=int, default=8765)
    parser.add_argument('--trials', type=int, default=20)
    parser.add_argument('--output', type=Path, default=Path('results'))
    args = parser.parse_args()
    if args.serve:
        server = LabServer(('127.0.0.1', args.port))
        print(f'Local demo: http://127.0.0.1:{args.port}/login', flush=True)
        try:
            server.serve_forever()
        except KeyboardInterrupt:
            pass
        finally:
            server.server_close()
    else:
        experiment(args.trials, args.output)
