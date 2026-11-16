"""Build Excalidraw scenes from Python without dependencies.

Usage from a generator script:

    import sys
    sys.path.insert(0, "<skill directory>/scripts")
    from excalidraw_scene import Scene, COLORS

    s = Scene()
    a = s.box(40, 40, 180, 60, "注文を確定する", role="actor")
    b = s.box(300, 40, 180, 60, "在庫を引き当てる", role="system")
    s.arrow_between(a, b, label="送信する")
    s.save("order.excalidraw")

The output opens in excalidraw.com and renders with scripts/render.py.
"""

from __future__ import annotations

import json
import random
import unicodedata
from pathlib import Path
from typing import Any

# Stroke and fill per role. Keep one role per kind of thing across every
# diagram in the same document so readers can match colors between figures.
COLORS: dict[str, tuple[str, str]] = {
    "actor": ("#1971c2", "#e7f5ff"),  # the person or client who acts first
    "operator": ("#e8590c", "#fff4e6"),  # a second person or team (reviewer, admin)
    "system": ("#1e1e1e", "#ffffff"),  # application processing
    "queue": ("#1098ad", "#e3fafc"),  # queues, caches, and other middleware
    "store": ("#2f9e44", "#d3f9d8"),  # storage and successful results
    "problem": ("#c92a2a", "#ffe3e3"),  # the problem, deletion, failure
    "schedule": ("#7048e8", "#f3f0ff"),  # schedulers and periodic triggers
    "note": ("#868e96", "transparent"),  # lane titles, elapsed time, side notes
}

FONT_NORMAL = 2  # Helvetica. Japanese falls back to the system font.


def text_width(s: str, size: float) -> float:
    """Estimate the rendered width of one line."""
    width = 0.0
    for ch in s:
        wide = unicodedata.east_asian_width(ch) in ("W", "F")
        width += size * (1.0 if wide else 0.58)
    return width


class Scene:
    def __init__(self, seed: int = 7) -> None:
        self._rng = random.Random(seed)
        self.elements: list[dict[str, Any]] = []

    # ---- primitives -----------------------------------------------------

    def _id(self) -> str:
        return "e%08x" % self._rng.getrandbits(32)

    def _base(self, kind: str, x: float, y: float, w: float, h: float, *,
              stroke: str = "#1e1e1e", bg: str = "transparent", width: int = 2,
              style: str = "solid", roundness: dict | None = None) -> dict[str, Any]:
        return {
            "id": self._id(), "type": kind, "x": x, "y": y, "width": w, "height": h,
            "angle": 0, "strokeColor": stroke, "backgroundColor": bg,
            "fillStyle": "solid", "strokeWidth": width, "strokeStyle": style,
            "roughness": 1, "opacity": 100, "groupIds": [], "frameId": None,
            "roundness": roundness, "seed": self._rng.getrandbits(31), "version": 1,
            "versionNonce": self._rng.getrandbits(31), "isDeleted": False,
            "boundElements": [], "updated": 1, "link": None, "locked": False,
        }

    def text(self, x: float, y: float, s: str, *, size: int = 16, color: str = "#1e1e1e",
             align: str = "left", width: float | None = None,
             container: str | None = None, valign: str = "top") -> dict[str, Any]:
        lines = s.split("\n")
        w = width or max(text_width(line, size) for line in lines)
        el = self._base("text", x, y, w, len(lines) * size * 1.35, stroke=color)
        el.update(text=s, originalText=s, fontSize=size, fontFamily=FONT_NORMAL,
                  textAlign=align, verticalAlign=valign, containerId=container,
                  lineHeight=1.35, autoResize=True, baseline=size)
        self.elements.append(el)
        return el

    def rect(self, x: float, y: float, w: float, h: float, *, stroke: str = "#1e1e1e",
             bg: str = "transparent", width: int = 2, style: str = "solid",
             rounded: bool = True) -> dict[str, Any]:
        el = self._base("rectangle", x, y, w, h, stroke=stroke, bg=bg, width=width,
                        style=style, roundness={"type": 3} if rounded else None)
        self.elements.append(el)
        return el

    def ellipse(self, x: float, y: float, w: float, h: float, *, stroke: str = "#1e1e1e",
                bg: str = "transparent", width: int = 2) -> dict[str, Any]:
        el = self._base("ellipse", x, y, w, h, stroke=stroke, bg=bg, width=width)
        self.elements.append(el)
        return el

    def line(self, x: float, y: float, points: list[list[float]], *, arrow: bool = False,
             stroke: str = "#1e1e1e", width: int = 2, style: str = "solid") -> dict[str, Any]:
        xs = [p[0] for p in points]
        ys = [p[1] for p in points]
        el = self._base("arrow" if arrow else "line", x, y, max(xs) - min(xs),
                        max(ys) - min(ys), stroke=stroke, width=width, style=style,
                        roundness={"type": 2})
        el.update(points=points, lastCommittedPoint=None, startBinding=None,
                  endBinding=None, startArrowhead=None,
                  endArrowhead="arrow" if arrow else None)
        if arrow:
            el["elbowed"] = False
        self.elements.append(el)
        return el

    def arrow(self, x: float, y: float, points: list[list[float]], **kw: Any) -> dict[str, Any]:
        return self.line(x, y, points, arrow=True, **kw)

    # ---- composites -----------------------------------------------------

    def box(self, x: float, y: float, w: float, h: float, label: str, *, role: str = "system",
            size: int = 16, style: str = "solid") -> dict[str, Any]:
        """A rounded box with a centered label. `role` picks the colors."""
        stroke, bg = COLORS[role]
        r = self.rect(x, y, w, h, stroke=stroke, bg=bg, style=style)
        t = self.text(x, y, label, size=size, align="center", width=w,
                      container=r["id"], valign="middle")
        t["y"] = y + (h - t["height"]) / 2
        r["boundElements"].append({"type": "text", "id": t["id"]})
        return r

    def arrow_between(self, a: dict, b: dict, *, label: str | None = None,
                      role: str = "system", style: str = "solid", size: int = 14) -> dict:
        """A straight arrow from the right edge of `a` to the left edge of `b`."""
        x1, y1 = a["x"] + a["width"] + 2, a["y"] + a["height"] / 2
        x2, y2 = b["x"] - 4, b["y"] + b["height"] / 2
        stroke = COLORS[role][0]
        el = self.arrow(x1, y1, [[0, 0], [x2 - x1, y2 - y1]], stroke=stroke, style=style)
        if label:
            self.text(x1 + 6, min(y1, y2) - size * 1.6, label, size=size, color=stroke)
        return el

    def lane_title(self, x: float, y: float, title: str) -> dict[str, Any]:
        """A gray caption above one lane, such as the normal flow or the fallback."""
        return self.text(x, y, title, size=14, color=COLORS["note"][0])

    def separator(self, x: float, y: float, length: float) -> dict[str, Any]:
        return self.line(x, y, [[0, 0], [length, 0]], stroke="#dee2e6", width=1,
                         style="dashed")

    def elapsed(self, x: float, y: float, length: float, label: str) -> None:
        """A vertical dashed arrow that stands for time passing."""
        gray = COLORS["note"][0]
        self.arrow(x, y, [[0, 0], [0, length]], stroke=gray, style="dashed")
        self.text(x + 14, y + length / 2 - 18, label, size=14, color=gray)

    def person(self, x: float, y: float, label: str, *, role: str = "actor") -> None:
        stroke, _ = COLORS[role]
        self.ellipse(x + 18, y, 28, 28, stroke=stroke, bg=stroke + "33")
        self.line(x + 32, y + 28, [[0, 0], [0, 34]], stroke=stroke)
        self.line(x + 14, y + 40, [[0, 0], [36, 0]], stroke=stroke)
        self.line(x + 32, y + 62, [[0, 0], [-14, 24]], stroke=stroke)
        self.line(x + 32, y + 62, [[0, 0], [14, 24]], stroke=stroke)
        self.text(x - 18, y + 92, label, size=15, color=stroke, align="center", width=100)

    def screen(self, x: float, y: float, label: str, *, button: str | None = None) -> None:
        """A small browser window with an image area and an optional button."""
        self.rect(x, y, 170, 112, bg="#ffffff")
        self.line(x, y + 18, [[0, 0], [170, 0]], stroke="#868e96", width=1)
        for i in range(3):
            self.ellipse(x + 8 + i * 10, y + 6, 6, 6, stroke="#868e96", width=1)
        self.rect(x + 16, y + 28, 70, 52, stroke="#1971c2", bg="#d0ebff", width=1,
                  rounded=False)
        self.line(x + 18, y + 76, [[0, 0], [20, -22], [34, -8], [48, -26], [66, 0]],
                  stroke="#1971c2", width=1)
        if button:
            r = self.rect(x + 96, y + 80, 66, 22, stroke="#1971c2", bg="#e7f5ff", width=1)
            t = self.text(x + 96, y + 83, button, size=11, align="center", width=66,
                          container=r["id"], valign="middle")
            r["boundElements"].append({"type": "text", "id": t["id"]})
        self.text(x - 20, y + 120, label, size=14, align="center", width=210)

    def cylinder(self, x: float, y: float, label: str, *, role: str = "store",
                 w: float = 90, h: float = 60) -> dict[str, Any]:
        """A database or object storage. Returns the body rectangle for arrows."""
        stroke, bg = COLORS[role]
        self.ellipse(x, y, w, 20, stroke=stroke, bg=bg)
        body = self.rect(x, y + 10, w, h - 20, stroke=stroke, bg=bg, rounded=False)
        self.ellipse(x, y + h - 20, w, 20, stroke=stroke, bg=bg)
        self.text(x - 20, y + h + 6, label, size=14, color=stroke, align="center",
                  width=w + 40)
        return body

    def file_chip(self, x: float, y: float, label: str, *, role: str = "store") -> None:
        """A small picture icon with a caption, for an uploaded file or image."""
        stroke, bg = COLORS[role]
        self.rect(x, y, 34, 26, stroke=stroke, bg=bg, width=1, rounded=False)
        self.line(x + 2, y + 23, [[0, 0], [9, -10], [15, -4], [22, -13], [30, 0]],
                  stroke=stroke, width=1)
        self.text(x + 42, y + 4, label, size=14, color=stroke)

    def trash(self, x: float, y: float) -> None:
        stroke, bg = COLORS["problem"]
        self.line(x, y + 6, [[0, 0], [30, 0]], stroke=stroke)
        self.line(x + 10, y, [[0, 0], [10, 0]], stroke=stroke)
        self.rect(x + 3, y + 8, 24, 26, stroke=stroke, bg=bg, rounded=False)
        for i in range(3):
            self.line(x + 9 + i * 6, y + 13, [[0, 0], [0, 16]], stroke=stroke, width=1)

    # ---- output ---------------------------------------------------------

    def bounds(self) -> tuple[float, float]:
        right = max(e["x"] + e["width"] for e in self.elements)
        bottom = max(e["y"] + e["height"] for e in self.elements)
        return right, bottom

    def save(self, path: str | Path) -> None:
        doc = {
            "type": "excalidraw", "version": 2, "source": "https://excalidraw.com",
            "elements": self.elements,
            "appState": {"viewBackgroundColor": "#ffffff", "gridSize": None},
            "files": {},
        }
        Path(path).write_text(json.dumps(doc, ensure_ascii=False, indent=1),
                              encoding="utf-8")
