#!/usr/bin/env python3
"""Contract tests for the local configurator (install/setup_server.py).

Covers: page serving + token injection, CSRF token rejection, structural
validation, artifact writing (content, modes, secret hygiene), the
getting-started guide, and the Spotlight env naming contract. Live key
validation is skipped (--skip-key-validation) — its routing is unit-tested
directly against validate_keys with a stubbed prober.
"""

import json
import os
import re
import subprocess
import sys
import tempfile
import time
import unittest
import urllib.error
import urllib.request
from unittest import mock

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "install"))
import setup_server as srv  # noqa: E402
import engine_bridge as engine  # noqa: E402

BASE = {
    "sovereignty": "cloud", "localModel": "gemma31b",
    "vault": "~/Documents/Mycroft", "spotlightVaultPath": "~/Documents/Spotlight",
    "installGoose": True, "installObsidian": True, "installFirecrawl": True,
    "ftEnabled": True, "agentmailEnabled": False, "apifyEnabled": False,
    "fireworks": True, "spotlight": True, "scoutpost": True,
    "spotDevBrowser": True,
    "fireworksKey": "fw-test", "firecrawlKey": "fc-test",
    "apifyToken": "", "agentmailKey": "", "scoutpostKey": "scout-test",
    "osintNavigatorKey": "ont-test", "junkipediaKey": "",
}
SECRETS = ["fw-test", "fc-test", "scout-test", "ont-test"]


class UnitChecks(unittest.TestCase):
    def test_engine_bridge_keeps_secret_values_off_argv(self):
        bridge = engine.EngineBridge.__new__(engine.EngineBridge)
        bridge.product = "mycroft"
        bridge.binary = "/fake/bsig"
        replies = iter([
            {"event": "result", "data": {"normalized": {"required_secret_ids": ["OPENCODE_API_KEY"]}}},
            {"event": "result", "data": {"keys": []}},
            {"event": "result", "data": {}},
            {"event": "result", "data": {"plan_path": "/tmp/plan.json"}},
        ])
        calls = []
        def fake_run(argv, **kwargs):
            calls.append((argv, kwargs.get("input")))
            event = next(replies)
            return subprocess.CompletedProcess(argv, 0, (json.dumps(event) + "\n").encode(), b"")
        with mock.patch.object(engine.subprocess, "run", side_effect=fake_run):
            result = bridge.submit({"schema_version": "bsig-configure/v1"}, {"OPENCODE_API_KEY": "newsroom-secret"})
        self.assertTrue(result["ok"])
        self.assertTrue(any(argv[-3:] == ["keys", "set", "OPENCODE_API_KEY"] and body == b"newsroom-secret" for argv, body in calls))
        self.assertFalse(any("newsroom-secret" in " ".join(argv) for argv, _ in calls))

    def test_structural_validation(self):
        d = srv.normalize(BASE)
        self.assertEqual(srv.validate_choices(d), [])
        cases = [
            ({"firecrawlKey": ""}, "firecrawl_key"),
            ({"fireworksKey": ""}, "fireworks_key"),
            ({"scoutpostKey": ""}, "scoutpost_api_key"),
            ({"vault": " "}, "vault_path"),
            ({"spotlightVaultPath": ""}, "spotlight_vault_path"),
        ]
        for overrides, field in cases:
            errs = srv.validate_choices(srv.normalize({**BASE, **overrides}))
            self.assertTrue(any(e["field"] == field for e in errs), field)
        # Sovereign Crawl4AI + SearXNG needs no Firecrawl account.
        keyless = srv.normalize({**BASE, "installFirecrawl": False, "firecrawlKey": ""})
        self.assertEqual(srv.validate_choices(keyless), [])
        # local mode needs no provider keys
        local = srv.normalize({**BASE, "sovereignty": "local", "fireworksKey": ""})
        self.assertEqual(srv.validate_choices(local), [])
        # disabled scoutpost needs no key
        off = srv.normalize({**BASE, "scoutpost": False, "scoutpostKey": ""})
        self.assertEqual(srv.validate_choices(off), [])

    def test_key_validation_routing(self):
        d = srv.normalize(BASE)
        orig = srv.probe
        try:
            srv.probe = lambda url, headers: "rejected"
            errors, warnings = srv.validate_keys(d)
            fields = {e["field"] for e in errors}
            # strict providers reject; scoutpost is lenient (warn only)
            self.assertEqual(fields, {"firecrawl_key", "fireworks_key"})
            self.assertTrue(any("SCOUTPOST" in w for w in warnings))
            srv.probe = lambda url, headers: "unreachable"
            errors, warnings = srv.validate_keys(d)
            self.assertEqual(errors, [])
            self.assertTrue(warnings)
            srv.probe = lambda url, headers: "ok"
            self.assertEqual(srv.validate_keys(d), ([], []))
        finally:
            srv.probe = orig

    def test_env_lines(self):
        env = srv.build_env_lines(srv.normalize(BASE))
        self.assertIn('MYCROFT_VAULT_PATH="$HOME/Documents/Mycroft"', env)
        self.assertIn("GOOSE_PROVIDER=fireworks-glm52", env)
        self.assertIn("GOOSE_MODEL=accounts/fireworks/models/glm-5p2", env)
        self.assertIn("FIRECRAWL_API_KEY=fc-test", env)
        self.assertIn("OSINT_NAV_API_KEY=ont-test", env)
        self.assertIn("SPOTLIGHT_MONITORING_BACKEND=scoutpost", env)
        self.assertNotIn("OSINT_NAVIGATOR", env)
        self.assertNotIn("BROWSERUSE", env)

    def test_env_lines_local(self):
        d = srv.normalize({**BASE, "sovereignty": "local", "localModel": "qwen27b",
                           "fireworks": False, "scoutpost": False, "scoutpostKey": "",
                           "spotlight": False})
        env = srv.build_env_lines(d)
        self.assertIn("GOOSE_PROVIDER=local", env)
        self.assertIn("GOOSE_MODEL=tomvaillant/qwen3.6-27b-abliterated-journalist-GGUF:Q4_K_M", env)
        self.assertIn("MYCROFT_LOCAL_MODEL_FILE=qwen3.6-27b-abliterated-journalist-Q4_K_M.gguf", env)
        self.assertNotIn("SPOTLIGHT_DIR", env)
        self.assertNotIn("SCOUTPOST", env)

    def test_setup_config(self):
        cfg = srv.build_setup_config(srv.normalize(BASE))
        for needle in ["SOVEREIGNTY=cloud", "LOCAL_ONLY=0", "ENABLE_SPOTLIGHT=1",
                       "ENABLE_SCOUTPOST=1", "ENABLE_FIREWORKS=1", "SPOT_DEVBROWSER=1",
                       "HAS_OSINT_NAVIGATOR=1", "ENABLE_FT=1",
                       'VAULT_PATH="$HOME/Documents/Mycroft"',
                       'REQUIRED_DOCTOR_ENV="FIRECRAWL_API_KEY FIREWORKS_API_KEY SCOUTPOST_API_KEY OSINT_NAV_API_KEY"']:
            self.assertIn(needle, cfg)
        for secret in SECRETS:
            self.assertNotIn(secret, cfg)

    def test_skill_registry(self):
        reg = srv.build_skill_registry(srv.normalize(BASE))
        ids = {s["id"] for s in reg["skills"]}
        for expected in ["knowledge-primitives", "qmd", "obsidian", "obsidian-ingest",
                         "fact-check", "mycroft-maintenance", "web-acquisition", "scoutpost",
                         "spotlight", "spotlight-ingest", "spotlight-monitoring",
                         "spotlight-integrations"]:
            self.assertIn(expected, ids)
        no_spot = srv.build_skill_registry(srv.normalize({**BASE, "spotlight": False, "scoutpost": False}))
        self.assertNotIn("spotlight", {s["id"] for s in no_spot["skills"]})

    def test_getting_started(self):
        guide = srv.build_getting_started(srv.normalize(BASE))
        for needle in ["~/Documents/Mycroft", "Spotlight vault", "Fireworks",
                       "START_HERE.md", "CLI: ON", "mycroft doctor"]:
            self.assertIn(needle, guide)
        for secret in SECRETS:
            self.assertNotIn(secret, guide)
        local = srv.build_getting_started(srv.normalize({**BASE, "sovereignty": "local",
                                                         "spotlight": False, "scoutpost": False,
                                                         "installObsidian": False}))
        self.assertIn("Local-first", local)
        self.assertNotIn("Spotlight vault", local)
        self.assertNotIn("Two switches", local)


class ServerChecks(unittest.TestCase):
    PORT = 8841

    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.mkdtemp()
        cls.fake_bsig = os.path.join(cls.tmp, "bsig")
        with open(cls.fake_bsig, "w", encoding="utf-8") as handle:
            handle.write("""#!/usr/bin/env python3
import json, sys
args = sys.argv[1:]
if args[:2] == ["configure", "describe"]:
    data = {"descriptor": {"schema_version": "bsig-configure-descriptor/v1", "product": "mycroft", "fields": []}}
elif args[:2] == ["configure", "validate"]:
    json.load(sys.stdin); data = {"normalized": {"required_secret_ids": []}}
elif args[:2] == ["keys", "list"]:
    data = {"keys": []}
elif args[:2] == ["configure", "plan"]:
    json.load(sys.stdin); data = {"plan_path": "/tmp/mycroft-install.json"}
else:
    sys.exit(4)
print(json.dumps({"event": "result", "data": data}))
""")
        os.chmod(cls.fake_bsig, 0o755)
        env = {**os.environ, "BSIG_BINARY": cls.fake_bsig}
        cls.proc = subprocess.Popen(
            [sys.executable, os.path.join(ROOT, "install", "setup_server.py"),
             "--profile-dir", cls.tmp, "--repo-dir", ROOT,
             "--port", str(cls.PORT), "--no-browser", "--skip-key-validation"],
            stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, env=env)
        cls.token = None
        deadline = time.time() + 10
        while time.time() < deadline:
            line = cls.proc.stdout.readline()
            if not line:
                break
            match = re.search(r"http://127\.0\.0\.1:(\d+)/\?t=([A-Za-z0-9_-]+)", line)
            if match:
                cls.PORT = int(match.group(1)); cls.token = match.group(2); break
        if not cls.token:
            raise RuntimeError("configurator never printed its token URL")
        deadline = time.time() + 10
        while time.time() < deadline:
            try:
                cls.page = urllib.request.urlopen(f"http://127.0.0.1:{cls.PORT}/?t={cls.token}", timeout=2).read().decode()
                break
            except Exception:
                time.sleep(0.2)
        else:
            raise RuntimeError("server did not start")

    @classmethod
    def tearDownClass(cls):
        cls.proc.terminate()
        cls.proc.wait(timeout=5)
        cls.proc.stdout.close()

    def post(self, path, payload):
        req = urllib.request.Request(
            f"http://127.0.0.1:{self.PORT}{path}",
            data=json.dumps(payload).encode(),
            headers={"Content-Type": "application/json"})
        return json.loads(urllib.request.urlopen(req, timeout=15).read())

    def test_flow(self):
        # 1. page is the configurator with token + platform injected
        self.assertIn("Configure your", self.page)
        self.assertNotIn("__SETUP_TOKEN__", self.page)
        self.assertNotIn("__PLATFORM__", self.page)
        self.assertIn("spotDevBrowser", self.page)
        self.assertIn("OSINT_NAV_API_KEY", self.page)
        self.assertIn("Optional fallback", self.page)
        self.assertNotIn('id="installFirecrawl" checked', self.page)

        # 2. bad token is rejected on both active POST endpoints
        for path in ("/engine-submit", "/pick-folder"):
            with self.assertRaises(urllib.error.HTTPError) as ctx:
                self.post(path, {**BASE, "token": "wrong"})
            self.assertEqual(ctx.exception.code, 403)

        # 3. the legacy writer endpoint is retired
        with self.assertRaises(urllib.error.HTTPError) as ctx:
            self.post("/submit", {**BASE, "token": self.token, "vault": ""})
        self.assertEqual(ctx.exception.code, 410)

        # 4. Engine submit writes only the sealed-plan marker and exits 0
        resp = self.post("/engine-submit", {
            "token": self.token,
            "request": {"schema_version": "bsig-configure/v1"},
            "secrets": {},
        })
        self.assertTrue(resp["ok"])
        self.assertEqual(self.proc.wait(timeout=10), 0)
        marker = os.path.join(self.tmp, "engine-plan.ready")
        self.assertEqual(os.stat(marker).st_mode & 0o777, 0o600)
        with open(marker, encoding="utf-8") as handle:
            self.assertEqual(json.load(handle)["plan_path"], "/tmp/mycroft-install.json")
        self.assertEqual(set(os.listdir(self.tmp)), {"bsig", "engine-plan.ready"})


if __name__ == "__main__":
    unittest.main(verbosity=1)
