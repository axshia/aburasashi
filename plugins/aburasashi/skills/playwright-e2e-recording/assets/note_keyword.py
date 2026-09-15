"""Public, read-only example: note.com -> third topic -> first article -> bottom.

Run through ../scripts/record_e2e.py with --base-url https://note.com.
The UI and ordering can change; inspect them before adapting this scenario.
"""
from urllib.parse import unquote, urlparse
from playwright.sync_api import expect

NAME = "note.com: third featured topic, first article, page bottom"
CHECKPOINTS = [
    ("open-home", "The featured keywords section is displayed"),
    ("open-third-topic", "The third topic and its popular article list are displayed"),
    ("open-first-article", "The first article from that list is displayed"),
    ("scroll-to-bottom", "The same article reaches a stable page bottom"),
]
SCROLL_METRICS = """() => ({
  y: scrollY, viewport: innerHeight,
  height: document.scrollingElement.scrollHeight,
  gap: document.scrollingElement.scrollHeight - innerHeight - scrollY
})"""

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

def popular_article_links(page):
    """Locate the article list in both observed note topic layouts."""
    legacy = page.get_by_role("heading", name="人気の記事一覧", exact=True)
    popular = page.get_by_role("group", name="ソート切り替え", exact=True).get_by_role(
        "link", name="人気", exact=True)
    expect(legacy.or_(popular).first).to_be_visible()
    if legacy.is_visible():
        return section_links(page, "人気の記事一覧", "/n/")
    destination = popular.evaluate("element => element.href")
    if page.url.split("#")[0] != destination:
        popular.click()
        page.wait_for_url(destination, wait_until="domcontentloaded")
    section = popular.locator("xpath=ancestor::section[.//a[contains(@href, '/n/')]][1]")
    links = section.locator('a[href*="/n/"]')
    expect(links.first).to_be_attached()
    return popular, links


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
    page.mouse.move(page.viewport_size["width"] * 0.75, page.viewport_size["height"] * 0.75)
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


def run(page, recording):
    with recording.step("open-home", page) as evidence:
        response = page.goto(recording.base_url, wait_until="domcontentloaded")
        assert response and response.ok
        heading, links = section_links(page, "注目キーワード", ("/hashtag/", "/tag/"))
        heading.scroll_into_view_if_needed()
        link, topic, candidates = select_card(links, 3)
        link.hover()
        evidence["observed"] = {"position": 3, "selected": topic,
                                "ordered_topics": candidates}
        page.wait_for_timeout(1500)
    with recording.step("open-third-topic", page) as evidence:
        page = click_card(page, link, topic)
        heading, links = popular_article_links(page)
        heading.scroll_into_view_if_needed()
        link, article, _ = select_card(links, 1)
        link.hover()
        evidence["observed"] = {"position": 1, "selected": article}
        page.wait_for_timeout(1500)
    with recording.step("open-first-article", page) as evidence:
        page = click_card(page, link, article)
        expect(page.get_by_role("heading", name=article["title"], exact=True).first).to_be_visible()
        expect(page.locator("article").first).to_be_visible()
        assert "/n/" in urlparse(page.url).path
        page.keyboard.press("ControlOrMeta+Home")
        page.wait_for_function("() => scrollY <= 2")
        article_url = document_url(page.url)
        evidence["observed"] = {"title": page.title(), "article_path": urlparse(page.url).path}
        page.wait_for_timeout(1500)
    with recording.step("scroll-to-bottom", page) as evidence:
        observations = scroll_to_bottom(page, 120)
        page.wait_for_timeout(1200)
        metrics = page.evaluate(SCROLL_METRICS)
        assert metrics["gap"] <= 2
        assert document_url(page.url) == article_url
        evidence["observed"] = {"bottom": metrics, "scroll_observations": observations}
