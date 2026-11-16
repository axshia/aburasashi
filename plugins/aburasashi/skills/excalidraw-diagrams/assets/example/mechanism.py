"""Example: a mechanism with the normal flow and the fallback in separate lanes.

    python3 mechanism.py mechanism.excalidraw
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts"))
from excalidraw_scene import COLORS, Scene  # noqa: E402

s = Scene()
red = COLORS["problem"][0]
green = COLORS["store"][0]

s.lane_title(30, 0, "通常のフロー")
# Name the first box after the event the reader knows, not the technical layer.
a = s.box(30, 30, 170, 64, "注文のキャンセル")
b = s.box(250, 30, 170, 64, "通知ジョブを\nキューイング")
c = s.box(470, 30, 150, 64, "ジョブキュー\n（DB）", role="queue")
d = s.box(670, 30, 150, 64, "ジョブのワーカー")
s.arrow_between(a, b)
s.arrow_between(b, c)
s.arrow_between(c, d)
s.arrow(745, 96, [[0, 0], [0, 40], [-200, 40], [-200, 2]], stroke=red, style="dashed")
s.text(560, 142, "送信に失敗したらリトライ", size=14, color=red)

mail = s.cylinder(950, 110, "メールを送信")
s.arrow(822, 62, [[0, 0], [124, 70]], stroke=green)
s.text(850, 60, "送信する", size=14, color=green)

s.separator(20, 190, 900)

s.lane_title(30, 210, "リトライしても残った分の再送")
e = s.box(30, 240, 190, 64, "スケジューラ\n（1 時間ごと）", role="schedule")
f = s.box(270, 240, 220, 64, "再送バッチ")
s.arrow_between(e, f, role="schedule")
s.arrow(492, 272, [[0, 0], [454, -112]], stroke=green)
s.text(640, 246, "未送信の分を送信する", size=14, color=green)

s.save(sys.argv[1] if len(sys.argv) > 1 else "mechanism.excalidraw")
