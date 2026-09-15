#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.10"
# dependencies = ["playwright==1.62.0"]
# ///
"""Record a headed Chrome journey from note.com to the bottom of a page.

Run: uv run scripts/e2e/note-keyword.py
Requires uv, Google Chrome and Playwright's video encoder. If the encoder is
missing: uv run --with playwright==1.62.0 playwright install ffmpeg

The home page's 注目キーワード contains topics, not articles. By default,
open its third topic, then the first article in 人気の記事一覧. The destination
is selected from the live UI; titles and URLs are not hard-coded.
Artifacts are saved in a new temporary directory. Recording ends when the test
context closes. Personal Chrome tabs and login sessions are not used.
"""

import argparse
import json
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import unquote, urlparse

from playwright.sync_api import expect, sync_playwright


VIEWPORT = {"width": 1440, "height": 1000}
SCROLL_METRICS = """() => ({
  y: scrollY, viewport: innerHeight,
  height: document.scrollingElement.scrollHeight,
  gap: document.scrollingElement.scrollHeight - innerHeight - scrollY
})"""


def now():
    return datetime.now(timezone.utc).isoformat()


def document_url(url):
    parsed = urlparse(url)
    return parsed.scheme, parsed.netloc, unquote(parsed.path).rstrip("/")


def section_links(page, heading, href_part):
    """Use the closest heading ancestor that also contains the matching cards."""
    title = page.get_by_role("heading", name=heading, exact=True)
    expect(title).to_be_visible()
    href_parts = (href_part,) if isinstance(href_part, str) else href_part
    predicate = " or ".join(f"contains(@href, '{part}')" for part in href_parts)
    section = title.locator(f"xpath=ancestor::*[.//a[{predicate}]][1]")
    links = section.locator(", ".join(f'a[href*="{part}"]' for part in href_parts))
    expect(links.first).to_be_attached()
    return title, links


def select_card(links, position):
    candidates = links.evaluate_all("""links => links.map((a, index) => {
      const r = a.getBoundingClientRect();
      return {index, href:a.href, target:a.target,
        title:a.getAttribute('aria-label') || a.title || a.innerText ||
          a.parentElement.innerText,
        top:r.top + scrollY, left:r.left,
        visible:r.width > 0 && r.height > 0 &&
          getComputedStyle(a).visibility !== 'hidden'};
    }).filter(a => a.visible).sort((a,b) => a.top-b.top || a.left-b.left)""")
    # Some cards expose both thumbnail and title links to the same article.
    unique = []
    seen = set()
    for item in candidates:
        if item["href"] not in seen:
            unique.append(item)
            seen.add(item["href"])
    assert len(unique) >= position, f"Only {len(unique)} cards; need {position}"
    selected = unique[position - 1]
    return links.nth(selected["index"]), selected, unique


def click_card(page, link, selected):
    # Only follow the actual note article/topic link seen in the inspected UI.
    target = urlparse(selected["href"])
    assert target.scheme == "https" and target.hostname in {"note.com", "note.jp"}
    assert any(part in target.path for part in ("/hashtag/", "/tag/", "/n/"))
    if selected["target"] == "_blank":
        with page.expect_popup() as popup:
            link.click()
        page = popup.value
    else:
        link.click()
    page.wait_for_url(
        lambda url: unquote(urlparse(url).path).rstrip("/") ==
        unquote(target.path).rstrip("/"),
        wait_until="domcontentloaded",
    )
    expect(page.locator("body")).to_be_visible()
    expect(page.locator("body")).not_to_have_text("")
    assert page.title(), "Destination has no title"
    return page


def scroll_to_bottom(page, max_steps):
    observations = []
    stable = 0
    previous_height = None
    page.mouse.move(VIEWPORT["width"] * 0.75, VIEWPORT["height"] * 0.75)
    for step in range(max_steps):
        before = page.evaluate(SCROLL_METRICS)
        page.mouse.wheel(0, round(before["viewport"] * 0.7))
        if before["gap"] > 2:
            page.wait_for_function("oldY => scrollY > oldY", arg=before["y"])
        # Deliberate pacing makes the recording readable and gives lazy content
        # a chance to grow. Actual success is checked from the document metrics.
        page.wait_for_timeout(600)
        current = page.evaluate(SCROLL_METRICS)
        observations.append({"step": step + 1, **current})
        if current["gap"] <= 2 and current["height"] == previous_height:
            stable += 1
        else:
            stable = 0
        previous_height = current["height"]
        if stable >= 4:
            assert current["y"] > 0, "Page never scrolled"
            return observations
    raise AssertionError(f"No stable page bottom after {max_steps} scroll steps")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--target", choices=["keyword-article", "keyword-page", "featured-article"],
                        default="keyword-article")
    parser.add_argument("--max-scroll-steps", type=int, default=120)
    args = parser.parse_args()
    if args.max_scroll_steps < 1:
        parser.error("--max-scroll-steps must be positive")
    output = Path(tempfile.mkdtemp(prefix="note-keyword-e2e-"))
    result = {"status": "FAIL", "started_at": now(), "target": args.target,
              "artifacts": str(output), "checkpoints": []}
    print(f"Artifacts: {output}", flush=True)

    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(channel="chrome", headless=False)
        context = browser.new_context(
            viewport=VIEWPORT, locale="ja-JP",
            record_video_dir=str(output / "videos"), record_video_size=VIEWPORT,
        )
        page = context.new_page()
        context.set_default_timeout(20_000)
        context.set_default_navigation_timeout(30_000)
        context.tracing.start(screenshots=True, snapshots=True, sources=True)
        result["browser"] = {"channel": "chrome", "version": browser.version}

        def checkpoint(name):
            result["checkpoints"].append({"id": name, "status": "PASS", "at": now()})
            print(f"PASS: {name}", flush=True)

        try:
            response = page.goto("https://note.com/", wait_until="domcontentloaded")
            assert response and response.ok, "Home page failed to load"
            heading = "今日の注目記事" if args.target == "featured-article" else "注目キーワード"
            href_part = "/n/" if args.target == "featured-article" else ("/hashtag/", "/tag/")
            title, links = section_links(page, heading, href_part)
            checkpoint("open-note-home")
            page.wait_for_timeout(1000)  # Hold the initial screen for the video.
            title.scroll_into_view_if_needed()
            link, selected, candidates = select_card(links, 3)
            result["home_selection"] = {"heading": heading, "position": 3,
                                        "selected": selected, "candidates": candidates}
            link.scroll_into_view_if_needed()
            link.hover()
            page.screenshot(path=str(output / "01-home-selection.png"))
            page.wait_for_timeout(1200)
            print(f"Third card: {selected['title']} — {selected['href']}", flush=True)
            page = click_card(page, link, selected)
            checkpoint("open-third-card")

            if args.target == "keyword-article":
                title, links = section_links(page, "人気の記事一覧", "/n/")
                title.scroll_into_view_if_needed()
                link, article, candidates = select_card(links, 1)
                result["article_selection"] = {"heading": "人気の記事一覧", "position": 1,
                                               "selected": article, "candidates": candidates}
                link.scroll_into_view_if_needed()
                link.hover()
                page.screenshot(path=str(output / "02-article-selection.png"))
                page.wait_for_timeout(1200)
                page = click_card(page, link, article)
                checkpoint("open-first-article")

            if args.target != "keyword-page":
                article_title = (result.get("article_selection") or result["home_selection"])["selected"]["title"]
                expect(page.get_by_role("heading", name=article_title, exact=True).first).to_be_visible()
                expect(page.locator("article").first).to_be_visible()
                assert "/n/" in urlparse(page.url).path, "Destination is not an article"
            page.keyboard.press("ControlOrMeta+Home")
            page.wait_for_function("() => scrollY <= 2")
            page.screenshot(path=str(output / "03-destination-top.png"))
            result["destination"] = {"url": page.url, "title": page.title()}
            page.wait_for_timeout(1500)
            result["scroll_observations"] = scroll_to_bottom(page, args.max_scroll_steps)
            page.wait_for_timeout(1200)  # Hold the final screen in the video.
            result["bottom"] = page.evaluate(SCROLL_METRICS)
            assert result["bottom"]["gap"] <= 2, "Page grew after reaching the bottom"
            # note removes the temporary ?gs= attribution after navigation.
            # Compare the document identity, not mutable analytics parameters.
            assert document_url(page.url) == document_url(result["destination"]["url"]), \
                "Scrolling changed the destination"
            result["destination"]["final_url"] = page.url
            page.screenshot(path=str(output / "04-destination-bottom.png"))
            checkpoint("scroll-to-stable-page-bottom")
            result["status"] = "PASS"
        except Exception as error:
            result["error"] = f"{type(error).__name__}: {error}"
            result["last_url"] = page.url
            if not page.is_closed():
                try:
                    page.screenshot(path=str(output / "failure.png"))
                except Exception:
                    pass
        finally:
            videos = [p.video for p in context.pages if p.video]
            for operation, finish in [
                ("trace", lambda: context.tracing.stop(path=str(output / "trace.zip"))),
                ("context", context.close),  # Finalizes the video before saving it.
            ]:
                try:
                    finish()
                except Exception as error:
                    result["status"] = "FAIL"
                    result.setdefault("artifact_errors", []).append(f"{operation}: {error}")
            result["videos"] = []
            for index, video in enumerate(videos, 1):
                try:
                    path = output / f"recording-{index:02}.webm"
                    video.save_as(str(path))
                    assert path.stat().st_size > 0, "Video is empty"
                    video.delete()  # Remove the duplicate encoder-named file.
                    result["videos"].append(str(path))
                except Exception as error:
                    result["status"] = "FAIL"
                    result.setdefault("artifact_errors", []).append(f"video: {error}")
            if not result["videos"]:
                result["status"] = "FAIL"
                result.setdefault("artifact_errors", []).append("No recording was saved")
            browser.close()
            result["finished_at"] = now()
            (output / "result.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n")
            summary = {key: result[key] for key in
                       ["status", "destination", "bottom", "videos", "error", "artifact_errors"]
                       if key in result}
            summary["result_file"] = str(output / "result.json")
            print(json.dumps(summary, ensure_ascii=False, indent=2), flush=True)
    return 0 if result["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
