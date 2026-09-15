#!/usr/bin/env python3
"""Local browser integration checks for the recorded E2E helper.

uv run --with playwright==1.62.0 python scripts/test-recorded-e2e.py
Requires Chrome and the Playwright video encoder; ffmpeg enables the MP4 check.
"""

import hashlib
import importlib.util
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import threading
import unittest


RUNNER = Path(__file__).resolve().parents[1] / "plugins/aburasashi/skills/playwright-e2e-recording/scripts/record_e2e.py"


class Pages(BaseHTTPRequestHandler):
    def do_GET(self):
        heading = "Popup" if self.path == "/popup" else "Home"
        body = (f"<!doctype html><title>{heading}</title><h1>{heading}</h1>"
                '<a href="/popup" target="_blank">Open popup</a>'
                '<div style="height:2200px">Scrollable content</div><footer>End of page</footer>').encode()
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, *_):
        pass


class RecordedE2E(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.output = Path(tempfile.mkdtemp(prefix="recorded-e2e-checks-"))
        cls.server = ThreadingHTTPServer(("127.0.0.1", 0), Pages)
        cls.thread = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.thread.start()
        cls.base_url = f"http://127.0.0.1:{cls.server.server_port}"
        print(f"Integration artifacts: {cls.output}", flush=True)

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.server.server_close()
        cls.thread.join()

    def execute(self, name, source, expected_code, mp4=False):
        scenario = self.output / f"{name}.py"
        scenario.write_text("from playwright.sync_api import expect\nNAME = " + repr(name) + "\n" + source)
        command = [sys.executable, str(RUNNER), str(scenario), "--base-url", self.base_url,
                   "--headless", "--output-root", str(self.output)]
        if mp4:
            command += ["--mp4"]
        process = subprocess.run(command, capture_output=True, text=True, timeout=90)
        self.assertEqual(process.returncode, expected_code, process.stdout + process.stderr)
        paths = json.loads(process.stdout.strip().splitlines()[-1])
        result_file = Path(paths["result"])
        result = json.loads(result_file.read_text())
        self.assertEqual(result["schema_version"], 1)
        self.assertFalse(result["artifact_errors"], result["artifact_errors"])
        self.assertEqual(result["review"]["publication"], "NOT_PUBLISHED")
        self.assertEqual(result["review"]["visual"], "NOT_REVIEWED")
        self.assertIsNone(result["target"]["deployment_revision"])
        for artifact in result["artifacts"]:
            self.assertFalse(Path(artifact["path"]).is_absolute())
            data = (result_file.parent / artifact["path"]).read_bytes()
            self.assertGreater(len(data), 0)
            self.assertEqual(hashlib.sha256(data).hexdigest(), artifact["sha256"])
        self.assertTrue(any(a["kind"] == "video" for a in result["artifacts"]))
        body = Path(paths["pr_evidence"]).read_text()
        self.assertIn(result["run_id"], body)
        self.assertIn(f"Result: {result['status']}", body)
        return result

    def test_success_preserves_closed_popup_and_mp4(self):
        mp4 = shutil.which("ffmpeg") is not None
        result = self.execute("success-popup", '''
CHECKPOINTS = [("home", "Home is visible"), ("popup", "Popup is visible"), ("bottom", "Footer is visible")]
def run(page, recording):
    with recording.step("home", page):
        page.goto(recording.base_url)
        expect(page.get_by_role("heading", name="Home")).to_be_visible()
    with page.expect_popup() as opening:
        page.get_by_role("link", name="Open popup").click()
    popup = opening.value
    with recording.step("popup", popup):
        expect(popup.get_by_role("heading", name="Popup")).to_be_visible()
        popup.wait_for_timeout(500)
    popup.close()
    with recording.step("bottom", page):
        page.locator("footer").scroll_into_view_if_needed()
        expect(page.locator("footer")).to_be_in_viewport()
        assert page.evaluate("scrollY > 0")
''', 0, mp4=mp4)
        self.assertEqual(result["status"], "PASS")
        self.assertEqual([r["status"] for r in result["checkpoints"]], ["PASS"] * 3)
        videos = [a for a in result["artifacts"] if a["kind"] == "video"]
        self.assertEqual({a["page_id"] for a in videos}, {"page-01", "page-02"})
        if mp4:
            self.assertEqual(len([a for a in videos if a["path"].endswith(".mp4")]), 2)
            self.assertTrue(all(a["decode"] == "PASS" for a in videos if a["path"].endswith(".webm")))

    def test_failure_keeps_movie_and_stops_later_checks(self):
        result = self.execute("assertion-failure", '''
CHECKPOINTS = [("home", "Home is visible"), ("mismatch", "Missing title is visible"), ("later", "Must not run")]
def run(page, recording):
    with recording.step("home", page):
        page.goto(recording.base_url)
        expect(page.get_by_role("heading")).to_have_text("Home")
    with recording.step("mismatch", page):
        expect(page.get_by_role("heading")).to_have_text("Missing title", timeout=250)
    with recording.step("later", page):
        raise AssertionError("This step should not run")
''', 1)
        self.assertEqual([r["status"] for r in result["checkpoints"]], ["PASS", "FAIL", "NOT_RUN"])
        self.assertTrue(any(a.get("checkpoint") == "mismatch" for a in result["artifacts"]))

    def test_blocked_is_distinct_from_success(self):
        result = self.execute("manual-prerequisite", '''
CHECKPOINTS = [("home", "Required prerequisite is available"), ("later", "Must not run")]
def run(page, recording):
    with recording.step("home", page):
        page.goto(recording.base_url)
        page.wait_for_timeout(300)
        recording.block("Fixture requires manual input")
''', 2)
        self.assertEqual(result["status"], "BLOCKED")
        self.assertEqual([r["status"] for r in result["checkpoints"]], ["BLOCKED", "NOT_RUN"])

    def test_early_return_cannot_pass(self):
        result = self.execute("incomplete", '''
CHECKPOINTS = [("home", "Home is visible"), ("missing", "Unexecuted assertion")]
def run(page, recording):
    with recording.step("home", page):
        page.goto(recording.base_url)
        expect(page.get_by_role("heading")).to_have_text("Home")
        page.wait_for_timeout(300)
''', 1)
        self.assertEqual(result["status"], "FAIL")
        self.assertEqual([r["status"] for r in result["checkpoints"]], ["PASS", "NOT_RUN"])

    def test_note_topic_selection_supports_both_observed_routes(self):
        from playwright.sync_api import sync_playwright

        spec = importlib.util.spec_from_file_location("note_example", RUNNER.parent.parent / "assets/note_keyword.py")
        example = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(example)
        with sync_playwright() as playwright:
            browser = playwright.chromium.launch(channel="chrome", headless=True)
            try:
                page = browser.new_page()
                for route in ("/hashtag/", "/tag/"):
                    page.set_content('<base href="https://note.com"><aside><a href="/tag/sidebar">Sidebar</a></aside>'
                        '<section><h2>注目キーワード</h2>' + ''.join(
                            f'<a style="display:inline-block;width:100px" href="{route}{index}">Topic {index}</a>'
                            for index in (1, 2, 3, 4)) + '</section>')
                    _, links = example.section_links(page, "注目キーワード", ("/hashtag/", "/tag/"))
                    _, selected, candidates = example.select_card(links, 3)
                    self.assertEqual(selected["href"], f"https://note.com{route}3")
                    self.assertEqual(len(candidates), 4)
            finally:
                browser.close()


if __name__ == "__main__":
    unittest.main(verbosity=2)
