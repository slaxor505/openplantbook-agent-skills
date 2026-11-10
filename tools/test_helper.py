#!/usr/bin/env python3
"""Tests for the Open Plantbook helper script. Standard library only.

Usage, from the repository root:
    python3 tools/test_helper.py

The tests start throwaway servers on 127.0.0.1 and never contact Open Plantbook.
"""

from __future__ import annotations

import contextlib
import importlib.util
import io
import json
import os
import subprocess
import sys
import threading
import unittest
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from unittest import mock

sys.dont_write_bytecode = True  # keep __pycache__ out of the tree that tools/check.py scans

HELPER_PATH = Path(__file__).resolve().parent.parent / "skills" / "openplantbook" / "scripts" / "openplantbook_cli.py"


def load_helper():
    spec = importlib.util.spec_from_file_location("openplantbook_cli", HELPER_PATH)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class Server:
    """Tiny local HTTP server. `routes` maps a path to (status, headers, body)."""

    def __init__(self, routes):
        self.requests = []  # (path, Authorization header) for every request received
        outer = self

        class Handler(BaseHTTPRequestHandler):
            def do_GET(self):
                outer.requests.append((self.path, self.headers.get("Authorization")))
                status, headers, body = routes.get(self.path, (404, {}, b"{}"))
                self.send_response(status)
                for key, value in headers.items():
                    self.send_header(key, value)
                self.send_header("Content-Length", str(len(body)))
                self.end_headers()
                self.wfile.write(body)

            def log_message(self, *args):
                pass

        self._server = HTTPServer(("127.0.0.1", 0), Handler)
        self.base = f"http://127.0.0.1:{self._server.server_address[1]}"
        threading.Thread(target=self._server.serve_forever, daemon=True).start()

    def close(self):
        self._server.shutdown()
        self._server.server_close()


class RedirectTests(unittest.TestCase):
    """The Authorization header must never follow a redirect to another address."""

    def setUp(self):
        self.helper = load_helper()
        self.target = Server({"/stolen": (200, {}, b"{}")})
        self.addCleanup(self.target.close)

    def call(self, origin_base, path, **kwargs):
        with mock.patch.object(self.helper, "_api_base", return_value=origin_base):
            return self.helper._request_json("GET", path, headers={"Authorization": "Token test-value"}, **kwargs)

    def test_redirect_is_refused_and_header_not_forwarded(self):
        for code in (301, 302, 303, 307, 308):
            with self.subTest(code=code):
                origin = Server({"/start": (code, {"Location": f"{self.target.base}/stolen"}, b"")})
                self.addCleanup(origin.close)
                stderr = io.StringIO()
                with contextlib.redirect_stderr(stderr), self.assertRaises(SystemExit) as ctx:
                    self.call(origin.base, "/start")
                self.assertEqual(ctx.exception.code, 1)
                self.assertEqual(self.target.requests, [], "the redirect target must not receive any request")
                self.assertIn("redirect", stderr.getvalue().lower())

    def test_redirect_with_allow_http_error_still_not_followed(self):
        origin = Server({"/start": (302, {"Location": f"{self.target.base}/stolen"}, b"")})
        self.addCleanup(origin.close)
        status, _ = self.call(origin.base, "/start", allow_http_error=True, return_status=True)
        self.assertEqual(status, 302)
        self.assertEqual(self.target.requests, [])

    def test_normal_response_still_works(self):
        origin = Server({"/ok": (200, {}, json.dumps({"pid": "abelia chinensis"}).encode())})
        self.addCleanup(origin.close)
        self.assertEqual(self.call(origin.base, "/ok"), {"pid": "abelia chinensis"})
        self.assertEqual(origin.requests, [("/ok", "Token test-value")])


class OutputEncodingTests(unittest.TestCase):
    """Piped output on Windows uses a legacy code page. The helper must still print UTF-8."""

    SNIPPET = (
        "import importlib.util, sys\n"
        "spec = importlib.util.spec_from_file_location('h', sys.argv[1])\n"
        "h = importlib.util.module_from_spec(spec)\n"
        "spec.loader.exec_module(h)\n"
        "{setup}\n"
        "h._print_json({{'common_names': ['Монстера', 'مونستيرا']}})\n"
    )

    def run_snippet(self, setup):
        env = {key: value for key, value in os.environ.items() if key not in {"PYTHONUTF8", "PYTHONIOENCODING"}}
        env["PYTHONIOENCODING"] = "cp1252"  # what a piped stdout looks like on most Windows installs
        return subprocess.run(
            [sys.executable, "-B", "-c", self.SNIPPET.format(setup=setup), str(HELPER_PATH)],
            capture_output=True, env=env, timeout=30, check=False,
        )

    def test_control_legacy_code_page_really_fails(self):
        # Without the fix the print must fail. If this stops failing, the test below proves nothing.
        proc = self.run_snippet("pass")
        self.assertNotEqual(proc.returncode, 0)
        self.assertIn(b"UnicodeEncodeError", proc.stderr)

    def test_prints_utf8_on_legacy_code_page(self):
        proc = self.run_snippet("h._configure_output()")
        self.assertEqual(proc.returncode, 0, proc.stderr.decode("utf-8", "replace"))
        self.assertEqual(json.loads(proc.stdout.decode("utf-8")), {"common_names": ["Монстера", "مونستيرا"]})

    def test_main_configures_output_first(self):
        helper = load_helper()
        with mock.patch.object(helper, "_configure_output") as configure, \
                mock.patch.object(sys, "argv", ["openplantbook_cli.py", "--help"]), \
                contextlib.redirect_stdout(io.StringIO()), self.assertRaises(SystemExit):
            helper.main()
        configure.assert_called_once()


if __name__ == "__main__":
    unittest.main(verbosity=2)
