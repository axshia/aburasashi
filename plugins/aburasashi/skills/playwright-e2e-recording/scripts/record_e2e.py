#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.10"
# dependencies = ["playwright==1.62.0"]
# ///
"""Run a trusted local scenario and save video plus a PR evidence handoff.

uv run record_e2e.py scenario.py --base-url https://example.com --mp4
Scenario API: NAME, CHECKPOINTS = [(id, expectation), ...], run(page, recording).
Use `with recording.step(id, page) as evidence:` around real UI assertions.
Exit codes: 0 PASS, 1 FAIL, 2 BLOCKED. This runner never publishes to GitHub.
"""

import argparse
from contextlib import contextmanager
from datetime import datetime, timezone
import hashlib
import importlib.util
import json
from pathlib import Path
import re
import shutil
import subprocess
import tempfile
import time
from urllib.parse import urlsplit, urlunsplit

from playwright.sync_api import sync_playwright


class Blocked(Exception):
    """The scenario needs user input or an unavailable prerequisite."""


def utc_now():
    return datetime.now(timezone.utc).isoformat()


def error_summary(error):
    # Playwright assertion errors may append the entire accessible page tree.
    # Keep the assertion/call log in the PR handoff; screenshots and opt-in
    # traces retain detailed failure context for local inspection.
    message = str(error).split("Aria snapshot:", 1)[0].strip()
    return f"{type(error).__name__}: {message[:3000]}"


def public_url(url):
    value = urlsplit(url)
    return urlunsplit((value.scheme, value.netloc.split("@")[-1], value.path, "", ""))


def command_output(argv):
    completed = subprocess.run(argv, capture_output=True, text=True, timeout=10)
    return completed.stdout.strip() if completed.returncode == 0 else None


def workspace_revision():
    try:
        head = command_output(["git", "rev-parse", "HEAD"])
        dirty = command_output(["git", "status", "--porcelain"])
        return {"head": head, "dirty": bool(dirty) if head else None}
    except (OSError, subprocess.TimeoutExpired):
        return {"head": None, "dirty": None}


def cell(value):
    return str(value).replace("&", "&amp;").replace("<", "&lt;").replace(
        ">", "&gt;").replace("|", "&#124;").replace("\n", " ").replace("`", "&#96;")


class Recording:
    def __init__(self, output, module, args):
        self.output, self.base_url = output, args.base_url
        self.started = time.monotonic()
        self.pages = []
        self.result = {
            "schema_version": 1, "run_id": output.name, "scenario": module.NAME,
            "status": "FAIL", "started_at": utc_now(),
            "target": {"url": public_url(args.base_url), "deployment_revision": None},
            "workspace": workspace_revision(),
            "persona": args.persona, "surface": args.surface,
            "browser": {"engine": "chromium", "channel": args.channel,
                        "headless": args.headless, "viewport": {"width": args.width, "height": args.height}},
            "checkpoints": [{"id": key, "expected": expected, "status": "NOT_RUN"}
                            for key, expected in module.CHECKPOINTS],
            "artifacts": [], "artifact_errors": [],
            "review": {"visual": "NOT_REVIEWED", "publication": "NOT_PUBLISHED"},
        }

    def seconds(self):
        return round(time.monotonic() - self.started, 3)

    def register_page(self, page):
        if not any(item["page"] is page for item in self.pages):
            self.pages.append({"page": page, "id": f"page-{len(self.pages) + 1:02}",
                               "created_seconds": self.seconds(), "video": page.video})

    def artifact(self, path, kind, **metadata):
        assert path.is_file() and path.stat().st_size, f"Missing or empty artifact: {path.name}"
        item = {"path": path.relative_to(self.output).as_posix(), "kind": kind,
                "bytes": path.stat().st_size,
                "sha256": hashlib.sha256(path.read_bytes()).hexdigest(), **metadata}
        self.result["artifacts"].append(item)
        return item

    @contextmanager
    def step(self, key, page):
        rows = self.result["checkpoints"]
        pending = next((row for row in rows if row["status"] != "PASS"), None)
        if not pending or pending["id"] != key or pending["status"] != "NOT_RUN":
            raise AssertionError(f"Checkpoint {key} is duplicated or out of order")
        self.register_page(page)
        page_id = next(item["id"] for item in self.pages if item["page"] is page)
        row = pending
        row.update(status="RUNNING", start_seconds=self.seconds(), page_id=page_id)
        try:
            yield row
            row["status"] = "PASS"
        except BaseException as error:
            row["status"] = "BLOCKED" if isinstance(error, (Blocked, KeyboardInterrupt)) else "FAIL"
            row["error"] = error_summary(error)
            raise
        finally:
            row["end_seconds"] = self.seconds()
            if not page.is_closed():
                row["url"] = public_url(page.url)
                try:
                    path = self.output / f"{key}-{row['status'].lower()}.png"
                    page.screenshot(path=str(path))
                    self.artifact(path, "screenshot", checkpoint=key, page_id=page_id)
                    row["screenshot"] = path.name
                except Exception as error:
                    self.result["artifact_errors"].append(f"{key} screenshot: {error}")
                    if row["status"] == "PASS":
                        row["status"] = "FAIL"
                        raise
            else:
                row["capture"] = "PAGE_CLOSED"
                if row["status"] == "PASS":
                    row["status"] = "FAIL"
                    raise AssertionError(f"{key}: page closed before checkpoint capture")
            print(f"{row['status']}: {key}", flush=True)

    def block(self, reason):
        raise Blocked(reason)

    def finalize_videos(self, mp4):
        for entry in self.pages:
            try:
                video = entry["video"]
                assert video, f"No video handle for {entry['id']}"
                path = self.output / f"{entry['id']}.webm"
                video.save_as(str(path))
                item = self.artifact(path, "video", page_id=entry["id"],
                                     page_created_seconds=entry["created_seconds"])
                video.delete()
                if shutil.which("ffmpeg"):
                    subprocess.run(["ffmpeg", "-v", "error", "-i", str(path), "-f", "null", "-"],
                                   check=True, capture_output=True, timeout=60)
                    item["decode"] = "PASS"
                else:
                    item["decode"] = "NOT_CHECKED"
                if shutil.which("ffprobe"):
                    probe = subprocess.run(["ffprobe", "-v", "error", "-show_entries",
                        "format=duration:stream=width,height", "-of", "json", str(path)],
                        check=True, capture_output=True, text=True, timeout=10)
                    info = json.loads(probe.stdout)
                    item["duration_seconds"] = float(info["format"]["duration"])
                    assert item["duration_seconds"] > 0, "Video has no duration"
                    item["width"], item["height"] = info["streams"][0]["width"], info["streams"][0]["height"]
                if mp4:
                    converted = path.with_suffix(".mp4")
                    subprocess.run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-i", str(path),
                        "-c:v", "libx264", "-preset", "fast", "-crf", "20", "-pix_fmt", "yuv420p",
                        "-movflags", "+faststart", "-an", str(converted)],
                        check=True, capture_output=True, timeout=60)
                    self.artifact(converted, "video", page_id=entry["id"], derived_from=path.name)
            except Exception as error:
                self.result["artifact_errors"].append(f"{entry['id']} video: {type(error).__name__}: {error}")
        if not any(a["kind"] == "video" for a in self.result["artifacts"]):
            self.result["artifact_errors"].append("No video saved")

    def write_handoff(self):
        result = self.result
        result["finished_at"] = utc_now()
        (self.output / "result.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n")
        lines = [f"## E2E: {cell(result['scenario'])}", "",
                 f"- Result: {result['status']} / run `{result['run_id']}`",
                 f"- Target: {cell(result['target']['url'])}",
                 f"- Workspace revision: `{result['workspace']['head'] or 'unknown'}` / dirty: {result['workspace']['dirty']}",
                 "- Deployed revision: unverified",
                 f"- Browser: {cell(result['browser']['channel'])} {cell(result['browser'].get('version', 'unknown'))}",
                 f"- Persona / surface: {cell(result['persona'])} / {cell(result['surface'])}",
                 "- Media review: NOT_REVIEWED / publication: NOT_PUBLISHED", "",
                 "| Checkpoint | Expected | Result | Run seconds | Screenshot |",
                 "| --- | --- | --- | --- | --- |"]
        for row in result["checkpoints"]:
            screenshot = f"![{row['id']}](./{row['screenshot']})" if row.get("screenshot") else "—"
            timing = f"{row.get('start_seconds', '—')}–{row.get('end_seconds', '—')}"
            lines.append(f"| {row['id']} | {cell(row['expected'])} | {row['status']} | {timing} | {screenshot} |")
        for entry in self.pages:
            videos = [a for a in result["artifacts"] if a["kind"] == "video" and a["page_id"] == entry["id"]]
            if videos:
                chosen = next((a for a in videos if a["path"].endswith(".mp4")), videos[0])
                lines += ["", f"### {entry['id']}", "", f"![](./{chosen['path']})"]
        if result.get("error"):
            lines += ["", f"Failure / blocker: {cell(result['error'])}"]
        for error in result["artifact_errors"]:
            lines += ["", f"Artifact error: {cell(error)}"]
        (self.output / "pr-evidence.md").write_text("\n".join(lines) + "\n")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("scenario", type=Path)
    parser.add_argument("--base-url", required=True)
    parser.add_argument("--output-root", type=Path)
    parser.add_argument("--channel", choices=["chrome", "chromium"], default="chrome")
    parser.add_argument("--headless", action="store_true")
    parser.add_argument("--width", type=int, default=1440)
    parser.add_argument("--height", type=int, default=1000)
    parser.add_argument("--persona", default="guest")
    parser.add_argument("--surface", default="desktop")
    parser.add_argument("--mp4", action="store_true")
    parser.add_argument("--trace", action="store_true")
    args = parser.parse_args()
    target = urlsplit(args.base_url)
    if target.scheme not in {"http", "https"} or not target.hostname or target.username or target.password:
        parser.error("--base-url must be an HTTP(S) URL without credentials")
    if args.width <= 0 or args.height <= 0 or args.width % 2 or args.height % 2:
        parser.error("Viewport width and height must be positive even numbers")
    if args.mp4 and not shutil.which("ffmpeg"):
        parser.error("--mp4 requires ffmpeg; omit the option to keep WebM")
    spec = importlib.util.spec_from_file_location("e2e_scenario", args.scenario.resolve())
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    ids = [key for key, expected in module.CHECKPOINTS]
    if not ids or len(set(ids)) != len(ids) or any(not re.fullmatch(r"[a-zA-Z0-9_-]+", key) for key in ids):
        parser.error("CHECKPOINTS needs unique filename-safe IDs")
    if not isinstance(module.NAME, str) or not module.NAME.strip() or not callable(module.run):
        parser.error("Scenario needs NAME and run(page, recording)")
    if args.output_root:
        args.output_root.mkdir(parents=True, exist_ok=True)
    output = Path(tempfile.mkdtemp(prefix="e2e-", dir=args.output_root)).resolve()
    recording = Recording(output, module, args)
    shutil.copy2(args.scenario, output / "scenario.py")
    recording.artifact(output / "scenario.py", "scenario")
    print(f"Artifacts: {output}", flush=True)
    browser = context = None
    trace_started = False
    with sync_playwright() as playwright:
        try:
            browser = playwright.chromium.launch(channel=args.channel, headless=args.headless)
            recording.result["browser"]["version"] = browser.version
            viewport = {"width": args.width, "height": args.height}
            context = browser.new_context(viewport=viewport, locale="ja-JP",
                base_url=args.base_url, record_video_dir=str(output / "raw-video"), record_video_size=viewport)
            context.on("page", recording.register_page)
            context.set_default_timeout(20_000)
            context.set_default_navigation_timeout(30_000)
            if args.trace:
                context.tracing.start(screenshots=True, snapshots=True, sources=True)
                trace_started = True
            page = context.new_page()
            module.run(page, recording)
            assert all(row["status"] == "PASS" for row in recording.result["checkpoints"]), \
                "Scenario returned without passing every checkpoint"
            recording.result["status"] = "PASS"
        except (Exception, KeyboardInterrupt) as error:
            recording.result["status"] = "BLOCKED" if isinstance(error, (Blocked, KeyboardInterrupt)) else "FAIL"
            recording.result["error"] = error_summary(error)
        finally:
            if context:
                if trace_started:
                    try:
                        trace = output / "trace.zip"
                        context.tracing.stop(path=str(trace))
                        recording.artifact(trace, "trace")
                    except Exception as error:
                        recording.result["artifact_errors"].append(f"trace: {error}")
                try:
                    context.close()  # Required before video.path/save_as, including on failure.
                except Exception as error:
                    recording.result["artifact_errors"].append(f"context close: {error}")
            recording.finalize_videos(args.mp4)
            if browser:
                try:
                    browser.close()
                except Exception as error:
                    recording.result["artifact_errors"].append(f"browser close: {error}")
            if recording.result["artifact_errors"] and recording.result["status"] == "PASS":
                recording.result["status"] = "FAIL"
            recording.write_handoff()
    print(json.dumps({"status": recording.result["status"], "result": str(output / "result.json"),
                      "pr_evidence": str(output / "pr-evidence.md")}), flush=True)
    return {"PASS": 0, "FAIL": 1, "BLOCKED": 2}[recording.result["status"]]


if __name__ == "__main__":
    raise SystemExit(main())
