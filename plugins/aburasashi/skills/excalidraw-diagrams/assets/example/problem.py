"""Example: a problem shown as the scene where it does not occur and the scene where it does.

    python3 problem.py problem.excalidraw
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts"))
from excalidraw_scene import COLORS, Scene  # noqa: E402

s = Scene()


def scene_row(y, title, action, kept_old, result, result_role):
    s.text(30, y, title, size=17)
    s.person(40, y + 40, "出品者")
    a = s.box(150, y + 50, 250, 64, action, role="actor")
    # The storage area as a dashed group.
    s.rect(470, y + 30, 260, 130, stroke=COLORS["store"][0], bg=COLORS["store"][1],
           style="dashed")
    s.text(690, y + 132, "ストレージ", size=13, color=COLORS["store"][0])
    if kept_old:
        s.file_chip(490, y + 100, "前の画像", role="problem")
    s.file_chip(590, y + 60, "新しい画像")
    s.arrow(a["x"] + a["width"] + 2, a["y"] + 32, [[0, 0], [186, -6]],
            stroke=COLORS["store"][0])
    s.text(410, y + 50, "保存する", size=13, color=COLORS["store"][0])
    s.box(780, y + 62, 200, 46, result, role=result_role)


scene_row(10, "① 初めて画像を登録したとき", "商品画像を登録する", False, "問題なし", "store")
s.arrow(60, 205, [[0, 0], [0, 40]], stroke=COLORS["operator"][0])
s.text(78, 214, "あとで画像を差し替える", size=14, color=COLORS["operator"][0])
scene_row(260, "② 画像を差し替えたとき", "商品画像を差し替える", True,
          "前の画像が不要なのに残る", "problem")

s.save(sys.argv[1] if len(sys.argv) > 1 else "problem.excalidraw")
