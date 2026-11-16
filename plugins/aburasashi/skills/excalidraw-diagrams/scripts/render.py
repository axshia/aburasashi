#!/usr/bin/env python3
"""Render .excalidraw files to PNG with headless Chromium.

    uv run --with playwright==1.62.0 python scripts/render.py a.excalidraw [b.excalidraw ...]

Each PNG is written next to its scene (a.png). The page loads the Excalidraw
library from esm.sh, so network access is required. It uses Playwright's Chromium, or Google Chrome when that
is missing.
"""

from __future__ import annotations

import argparse
import base64
import functools
import http.server
import shutil
import sys
import tempfile
import threading
from pathlib import Path

HERE = Path(__file__).resolve().parent


class QuietHandler(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *args: object) -> None:
        pass


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("scenes", nargs="+", type=Path)
    parser.add_argument("--scale", type=int, default=2, help="export scale (default 2)")
    parser.add_argument("--timeout", type=int, default=60000, help="milliseconds per scene")
    args = parser.parse_args()

    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        print("playwright is not installed; run with `uv run --with playwright==1.62.0`",
              file=sys.stderr)
        return 2

    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        shutil.copy(HERE / "render.html", root / "render.html")
        handler = functools.partial(QuietHandler, directory=tmp)
        server = http.server.ThreadingHTTPServer(("127.0.0.1", 0), handler)
        threading.Thread(target=server.serve_forever, daemon=True).start()
        port = server.server_address[1]
        failed = 0
        try:
            with sync_playwright() as p:
                try:
                    browser = p.chromium.launch()
                except Exception:
                    # Fall back to an installed Google Chrome when Playwright's
                    # bundled Chromium is missing.
                    browser = p.chromium.launch(channel="chrome")
                page = browser.new_page()
                for scene in args.scenes:
                    name = f"scene-{scene.stem}.excalidraw"
                    shutil.copy(scene, root / name)
                    page.goto(f"http://127.0.0.1:{port}/render.html?file={name}"
                              f"&scale={args.scale}")
                    page.wait_for_function(
                        "document.title === 'done' || document.title.startsWith('error')",
                        timeout=args.timeout)
                    if page.title() != "done":
                        print(f"{scene}: {page.title()}", file=sys.stderr)
                        failed += 1
                        continue
                    data = page.evaluate("window.__png").split(",", 1)[1]
                    out = scene.with_suffix(".png")
                    out.write_bytes(base64.b64decode(data))
                    print(out)
                browser.close()
        finally:
            server.shutdown()
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
