#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.10"
# dependencies = ["playwright==1.62.0"]
# ///
"""Search Google and click its first non-ad web result.

Run: uv run scripts/e2e/google-search.py --keep-open --captcha-wait-seconds 300
Requires uv and Google Chrome. Artifacts go to a new temporary directory.
--keep-open leaves the tested window visible for up to 10 minutes.
Google CAPTCHA/consent blocks are reported without attempting to bypass them.
"""

import argparse
import json
import re
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import parse_qs, urlparse

from playwright.sync_api import TimeoutError as PlaywrightTimeout
from playwright.sync_api import expect, sync_playwright


class Blocked(Exception):
    pass


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--keep-open", action="store_true")
    parser.add_argument("--captcha-wait-seconds", type=int, default=0,
                        help="Wait for the user to solve CAPTCHA; 0 reports BLOCKED immediately")
    args = parser.parse_args()
    output = Path(tempfile.mkdtemp(prefix="google-search-e2e-"))
    result = {
        "status": "FAIL",
        "query": "test",
        "started_at": datetime.now(timezone.utc).isoformat(),
        "artifacts": str(output),
        "checkpoints": [],
    }
    print(f"Artifacts: {output}", flush=True)

    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(channel="chrome", headless=False)
        context = browser.new_context(viewport={"width": 1440, "height": 1000}, locale="ja-JP")
        page = context.new_page()
        page.set_default_timeout(20_000)
        page.set_default_navigation_timeout(30_000)
        result["browser"] = {"channel": "chrome", "version": browser.version}
        context.tracing.start(screenshots=True, snapshots=True, sources=True)

        try:
            page.goto("https://www.google.com/?hl=ja", wait_until="domcontentloaded")
            # Consent is handled only through a visible reject button, if offered.
            reject = page.get_by_role("button", name=re.compile(r"^(Reject all|すべて拒否)$"))
            if reject.is_visible():
                reject.click()
            search = page.locator('textarea[name="q"], input[name="q"]').filter(visible=True).first
            expect(search).to_be_visible()
            search.fill("test")
            expect(search).to_have_value("test")
            search.press("Enter")
            result["checkpoints"].append({"id": "submit-query", "status": "PASS"})
            page.wait_for_url(re.compile(r"/(search|sorry)([/?]|$)"))
            page.wait_for_load_state("domcontentloaded")
            if "/sorry" in urlparse(page.url).path:
                if args.captcha_wait_seconds <= 0:
                    raise Blocked("Google requested CAPTCHA / unusual-traffic verification.")
                print("WAITING_FOR_USER: Complete the CAPTCHA in the test Chrome window. The script will resume automatically.", flush=True)
                try:
                    page.wait_for_url(
                        re.compile(r"https://www\.google\.[^/]+/search\?"),
                        timeout=args.captcha_wait_seconds * 1000,
                        wait_until="domcontentloaded",
                    )
                except PlaywrightTimeout as error:
                    raise Blocked("Manual CAPTCHA verification was not completed within the time limit.") from error
            assert parse_qs(urlparse(page.url).query).get("q") == ["test"], "Wrong search query"

            links = page.locator("#rso a:has(h3)")
            expect(links.first).to_be_visible()
            # Inspect actual result links in visual order; fail if none can be
            # classified. Do not substitute a known URL or click an ad fallback.
            candidates = links.evaluate_all(r"""anchors => anchors.map((a, index) => {
              const heading = a.querySelector('h3');
              const rect = heading.getBoundingClientRect();
              const card = a.closest('.MjjYud') || a.parentElement;
              const adAncestor = a.closest(
                '#tads, #bottomads, [data-text-ad], [data-ad-slot], [data-ad], [data-commercial-unit]'
              );
              const adLabel = Array.from(card.querySelectorAll('span, [aria-label]')).some(el =>
                /^(スポンサー|スポンサー広告|広告|Sponsored|Ads?)$/i.test((el.textContent || '').trim()) ||
                /^(スポンサー|広告|Sponsored|Ads?)$/i.test(el.getAttribute('aria-label') || '')
              );
              return {index, title: heading.innerText, href: a.href, target: a.target,
                top: rect.top + scrollY, left: rect.left,
                visible: rect.width > 0 && rect.height > 0,
                ad: Boolean(adAncestor) || adLabel || /googleadservices|doubleclick|\/aclk\?/.test(a.href)};
            }).filter(item => item.visible && !item.ad && /^https?:/.test(item.href))
              .sort((a, b) => a.top - b.top || a.left - b.left)""")
            assert candidates, "No unambiguously non-ad web result found"
            selected = candidates[0]
            result["selected"] = selected
            result["search_url"] = page.url
            result["candidates"] = candidates
            result["checkpoints"].append({"id": "search", "status": "PASS"})
            link = links.nth(selected["index"])
            link.scroll_into_view_if_needed()
            page.screenshot(path=str(output / "01-search.png"))
            print(f"Selected: {selected['title']} — {selected['href']}", flush=True)

            if selected["target"] == "_blank":
                with page.expect_popup() as popup:
                    link.click()
                page = popup.value
                page.wait_for_load_state("domcontentloaded")
                response_status = None
            else:
                with page.expect_navigation(wait_until="domcontentloaded") as navigation:
                    link.click()
                response = navigation.value
                response_status = response.status if response else None
            expect(page.locator("body")).to_be_visible()
            expect(page.locator("body")).not_to_have_text("")
            final = urlparse(page.url)
            assert final.scheme in {"http", "https"}, "Destination did not load a web page"
            assert final.hostname != urlparse(result["search_url"]).hostname, "Still on Google"
            assert response_status is None or response_status < 400, f"HTTP {response_status}"
            result["destination"] = {"url": page.url, "title": page.title(), "http_status": response_status}
            assert result["destination"]["title"], "Destination has no title"
            page.screenshot(path=str(output / "02-destination.png"))
            result["checkpoints"].append({"id": "click-and-display", "status": "PASS"})
            result["status"] = "PASS"
        except Exception as error:
            result["status"] = "BLOCKED" if isinstance(error, Blocked) else "FAIL"
            result["error"] = str(error)
            current = urlparse(page.url)
            result["last_url"] = f"{current.scheme}://{current.netloc}{current.path}"
            if not page.is_closed():
                page.screenshot(path=str(output / "failure.png"))
        finally:
            context.tracing.stop(path=str(output / "trace.zip"))
            result["finished_at"] = datetime.now(timezone.utc).isoformat()
            (output / "result.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n")
            print(json.dumps(result, ensure_ascii=False, indent=2), flush=True)

        if args.keep_open:
            print("Verification finished. Close the test window when done (auto-close after 10 minutes).", flush=True)
            try:
                page.wait_for_event("close", timeout=600_000)
            except PlaywrightTimeout:
                pass
        browser.close()
    return 0 if result["status"] == "PASS" else 2 if result["status"] == "BLOCKED" else 1


if __name__ == "__main__":
    raise SystemExit(main())
