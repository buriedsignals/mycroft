#!/usr/bin/env python3
"""Exercise real entrypoints with isolated providers and a loopback search server."""
from __future__ import annotations

import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    with tempfile.TemporaryDirectory() as directory:
        tmp = Path(directory)
        bins = tmp / "bin"
        bins.mkdir()
        log = tmp / "providers.log"
        config = tmp / "selected.json"
        home = tmp / "home"
        home.mkdir()
        env = {key: value for key, value in os.environ.items() if key not in (
            "MYCROFT_CONFIG", "MYCROFT_PROFILE_DIR", "MYCROFT_DATA_DIR", "MYCROFT_DIR",
        )}
        env.update(HOME=str(home), XDG_CONFIG_HOME=str(home / ".config"),
                   XDG_DATA_HOME=str(home / ".local/share"), PATH=f"{bins}:/usr/bin:/bin",
                   MYCROFT_CONFIG=str(config), MYCROFT_DIR=str(ROOT),
                   MYCROFT_PROV_DIR=str(tmp / "evidence"), FIRECRAWL_API_KEY="test-key",
                   PROVIDER_LOG=str(log))
        # python3 is needed by doctor/provisioning even on hosts without /usr/bin/python3.
        (bins / "python3").symlink_to(sys.executable)
        provider = f'''#!{sys.executable}
import json, os, pathlib, sys
name = pathlib.Path(sys.argv[0]).name
with open(os.environ["PROVIDER_LOG"], "a") as out:
    out.write(name + " " + " ".join(sys.argv[1:]) + "\\n")
if name in ("crwl", "uvx"):
    if os.environ.get("LOCAL_FAIL") == "1":
        sys.exit(7)
    print("LOCAL CONTENT")
elif name == "firecrawl":
    if os.environ.get("CLOUD_FAIL") == "1":
        sys.exit(8)
    if sys.argv[1] == "search":
        print(json.dumps({{"data": {{"web": [{{"url": "https://example.org/cloud", "title": "Cloud result"}}]}}}}))
    else:
        print("CLOUD CONTENT")
elif name == "uv":
    print("crawl4ai 0.test")
else:
    sys.exit(0)
'''
        for name in ("firecrawl", "crwl", "uvx", "uv", "curl", "docker", "brew", "crawl4ai-setup", "pdftotext"):
            path = bins / name
            path.write_text(provider)
            path.chmod(0o755)

        requests = []
        class SearchHandler(BaseHTTPRequestHandler):
            def do_GET(self):
                requests.append(self.path)
                if env.get("LOCAL_FAIL") == "1":
                    self.send_error(503)
                    return
                body = json.dumps({"results": [{"url": "https://example.org/local", "title": "Local result"}]}).encode()
                self.send_response(200)
                self.end_headers()
                self.wfile.write(body)

            def log_message(self, *args):
                pass

        server = ThreadingHTTPServer(("127.0.0.1", 0), SearchHandler)
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        env["SEARXNG_URL"] = f"http://127.0.0.1:{server.server_port}"

        def policy(search="searxng", scrape="crawl4ai", firecrawl="disabled"):
            config.write_text(json.dumps({"acquisition": dict(search=search, scrape=scrape, firecrawl=firecrawl)}))

        def run(relative, *args):
            log.write_text("")
            requests.clear()
            executable = "bash" if relative.endswith(".sh") or relative.endswith("mycroft-doctor") else sys.executable
            result = subprocess.run([executable, str(ROOT / relative), *args], env=env, text=True, capture_output=True, timeout=15)
            return result, log.read_text()

        entrypoints = [
            ("tools/scrape.py", ["https://example.org/source"], "scrape"),
            ("tools/searxng-search.py", ["query", "--json", "--limit", "1"], "search"),
            ("scripts/mycroft-fetch", ["scrape", "https://example.org/source"], "scrape"),
            ("scripts/mycroft-fetch", ["search", "query", "--limit", "1"], "search"),
            ("integration/sift-c2pa/mycroft-fetch", ["--json", "scrape", "https://example.org/source"], "scrape"),
            ("integration/sift-c2pa/mycroft-fetch", ["--json", "search", "query", "--limit", "1"], "search"),
        ]
        try:
            for relative, args, operation in entrypoints:
                for mode in ("cloud", "local", "fallback", "disabled", "cloud-failure"):
                    cloud = mode in ("cloud", "cloud-failure")
                    policy("firecrawl" if cloud else "searxng", "firecrawl" if cloud else "crawl4ai",
                           "fallback" if mode != "disabled" else "disabled")
                    env["LOCAL_FAIL"] = "1" if mode in ("fallback", "disabled") else "0"
                    env["CLOUD_FAIL"] = "1" if mode == "cloud-failure" else "0"
                    result, calls = run(relative, *args)
                    assert (result.returncode == 0) == (mode not in ("disabled", "cloud-failure")), (relative, mode, result.stderr)
                    if cloud:
                        assert not requests and not any(name in calls for name in ("crwl", "uvx", "uv ")), calls
                    if mode in ("local", "disabled"):
                        assert "firecrawl" not in calls, calls
                    if not cloud and operation == "search":
                        assert requests, (relative, mode)
                    if not cloud and operation == "scrape":
                        assert "crwl" in calls, (relative, mode)
                    if mode in ("cloud", "fallback"):
                        assert f"firecrawl {operation}" in calls, calls
                    if result.returncode == 0 and "mycroft-fetch" in relative:
                        payload = json.loads(result.stdout)
                        record = payload.get("evidence", payload["provenance"])
                        expected = "firecrawl" if mode in ("cloud", "fallback") else ("crawl4ai" if operation == "scrape" else "searxng")
                        assert record["acquisition_method"] == expected
                        assert ("crwl" if expected == "crawl4ai" else expected) in record["command"]
                # Existing profiles can explicitly choose cloud search with local
                # scraping; source updates must not invalidate that recorded choice.
                policy("firecrawl", "crawl4ai", "fallback")
                env["LOCAL_FAIL"] = env["CLOUD_FAIL"] = "0"
                result, calls = run(relative, *args)
                assert result.returncode == 0 and not requests, (relative, result.stderr)
                if operation == "search":
                    assert "firecrawl search" in calls and "crwl" not in calls, calls
                else:
                    assert "crwl" in calls and "firecrawl" not in calls, calls
                for invalid in (None, "{", "[]", "{}", json.dumps({"acquisition": {"search": "unknown", "scrape": "crawl4ai", "firecrawl": "fallback"}})):
                    if invalid is None:
                        config.unlink()
                    else:
                        config.write_text(invalid)
                    result, calls = run(relative, *args)
                    assert result.returncode != 0 and not calls and not requests, (relative, invalid, calls)

            env["LOCAL_FAIL"] = env["CLOUD_FAIL"] = "0"
            policy("firecrawl", "firecrawl", "fallback")
            for relative in ("scripts/mycroft-doctor", "scripts/provision-sovereign.sh"):
                result, calls = run(relative)
                assert not requests and not any(name in calls for name in ("crwl", "uvx", "uv ", "docker", "curl", "crawl4ai-setup")), calls
                if relative.endswith(".sh"):
                    assert result.returncode == 0, result.stderr
                config.write_text("{")
                result, calls = run(relative)
                assert result.returncode != 0 and not calls and not requests, (relative, calls)
                policy("firecrawl", "firecrawl", "fallback")

            # Explicit config overrides profile; profile overrides XDG default.
            profile = tmp / "profile"
            profile.mkdir()
            (profile / "mycroft-config.json").write_text(config.read_text())
            env["MYCROFT_PROFILE_DIR"] = str(profile)
            policy()
            result, calls = run("tools/scrape.py", "https://example.org/source")
            assert result.returncode == 0 and "crwl" in calls and "firecrawl" not in calls
            del env["MYCROFT_CONFIG"]
            result, calls = run("tools/scrape.py", "https://example.org/source")
            assert result.returncode == 0 and "firecrawl" in calls and "crwl" not in calls
            (profile / "mycroft-config.json").unlink()
            result, calls = run("tools/scrape.py", "https://example.org/source")
            assert result.returncode != 0 and not calls
            del env["MYCROFT_PROFILE_DIR"]
            result, calls = run("tools/scrape.py", "https://example.org/source")
            assert result.returncode == 0 and "crwl" in calls and "firecrawl" not in calls
            default_config = home / ".config/goose/mycroft/mycroft-config.json"
            default_config.parent.mkdir(parents=True)
            result, calls = run("tools/scrape.py", "https://example.org/source")
            assert result.returncode != 0 and not calls
            default_config.write_text("{")
            result, calls = run("tools/scrape.py", "https://example.org/source")
            assert result.returncode != 0 and not calls
            policy("firecrawl", "firecrawl", "fallback")
            default_config.write_text(config.read_text())
            result, calls = run("tools/scrape.py", "https://example.org/source")
            assert result.returncode == 0 and "firecrawl" in calls and "crwl" not in calls
        finally:
            server.shutdown()
            server.server_close()
            thread.join()
    print("acquisition routing checks passed")


if __name__ == "__main__":
    main()
