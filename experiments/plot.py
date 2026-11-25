#!/usr/bin/env python3
"""Vẽ biểu đồ hội tụ, boxplot và so sánh gap (PNG thuần Python chuẩn) vào results/figures/."""

import argparse
import csv
import math
import pathlib
import shutil
import struct
import sys
import zlib
from collections import defaultdict


def _mean(vals: list[float]) -> float:
    return sum(vals) / len(vals)


def _median(vals: list[float]) -> float:
    s = sorted(vals)
    n = len(s)
    mid = n // 2
    return s[mid] if n % 2 == 1 else (s[mid - 1] + s[mid]) / 2.0


for stream in (sys.stdout, sys.stderr):
    if hasattr(stream, "reconfigure"):
        stream.reconfigure(encoding="utf-8")


ROOT = pathlib.Path(__file__).resolve().parents[1]
DEFAULT_RESULTS = ROOT / "results"

PALETTE = {
    "GREEDY": "#64748b",
    "HC_FI": "#0ea5e9",
    "HC_BI": "#0284c7",
    "TS": "#f59e0b",
    "SA": "#ef4444",
    "GA": "#8b5cf6",
    "GA_LS": "#10b981",
    "GRASP": "#ec4899",
}
ALGO_ORDER = ["GREEDY", "HC_FI", "HC_BI", "TS", "SA", "GA", "GA_LS", "GRASP"]

# 5x7 bitmap font for ASCII characters 32..126 (row-major, 5 bits per row)
FONT_5X7: dict[str, tuple[int, ...]] = {
    " ": (0, 0, 0, 0, 0, 0, 0),
    "!": (4, 4, 4, 4, 4, 0, 4),
    "%": (25, 25, 2, 4, 8, 19, 19),
    "(": (2, 4, 8, 8, 8, 4, 2),
    ")": (8, 4, 2, 2, 2, 4, 8),
    "+": (0, 4, 4, 31, 4, 4, 0),
    ",": (0, 0, 0, 0, 0, 4, 8),
    "-": (0, 0, 0, 31, 0, 0, 0),
    ".": (0, 0, 0, 0, 0, 12, 12),
    "/": (1, 1, 2, 4, 8, 16, 16),
    "0": (14, 17, 19, 21, 25, 17, 14),
    "1": (4, 12, 4, 4, 4, 4, 14),
    "2": (14, 17, 1, 2, 4, 8, 31),
    "3": (31, 2, 4, 2, 1, 17, 14),
    "4": (2, 6, 10, 18, 31, 2, 2),
    "5": (31, 16, 30, 1, 1, 17, 14),
    "6": (6, 8, 16, 30, 17, 17, 14),
    "7": (31, 1, 2, 4, 8, 8, 8),
    "8": (14, 17, 17, 14, 17, 17, 14),
    "9": (14, 17, 17, 15, 1, 2, 12),
    ":": (0, 12, 12, 0, 12, 12, 0),
    "=": (0, 0, 31, 0, 31, 0, 0),
    "A": (14, 17, 17, 31, 17, 17, 17),
    "B": (30, 17, 17, 30, 17, 17, 30),
    "C": (14, 17, 16, 16, 16, 17, 14),
    "D": (28, 18, 17, 17, 17, 18, 28),
    "E": (31, 16, 16, 30, 16, 16, 31),
    "F": (31, 16, 16, 30, 16, 16, 16),
    "G": (14, 17, 16, 23, 17, 17, 15),
    "H": (17, 17, 17, 31, 17, 17, 17),
    "I": (14, 4, 4, 4, 4, 4, 14),
    "J": (7, 2, 2, 2, 2, 18, 12),
    "K": (17, 18, 20, 24, 20, 18, 17),
    "L": (16, 16, 16, 16, 16, 16, 31),
    "M": (17, 27, 21, 21, 17, 17, 17),
    "N": (17, 25, 21, 19, 17, 17, 17),
    "O": (14, 17, 17, 17, 17, 17, 14),
    "P": (30, 17, 17, 30, 16, 16, 16),
    "Q": (14, 17, 17, 17, 21, 18, 13),
    "R": (30, 17, 17, 30, 20, 18, 17),
    "S": (15, 16, 16, 14, 1, 1, 30),
    "T": (31, 4, 4, 4, 4, 4, 4),
    "U": (17, 17, 17, 17, 17, 17, 14),
    "V": (17, 17, 17, 17, 17, 10, 4),
    "W": (17, 17, 17, 21, 21, 27, 17),
    "X": (17, 17, 10, 4, 10, 17, 17),
    "Y": (17, 17, 10, 4, 4, 4, 4),
    "Z": (31, 1, 2, 4, 8, 16, 31),
    "_": (0, 0, 0, 0, 0, 0, 31),
    "a": (0, 0, 14, 1, 15, 17, 15),
    "b": (16, 16, 22, 25, 17, 17, 30),
    "c": (0, 0, 14, 16, 16, 17, 14),
    "d": (1, 1, 13, 19, 17, 17, 15),
    "e": (0, 0, 14, 17, 31, 16, 14),
    "f": (6, 9, 8, 28, 8, 8, 8),
    "g": (0, 0, 15, 17, 15, 1, 14),
    "h": (16, 16, 22, 25, 17, 17, 17),
    "i": (4, 0, 12, 4, 4, 4, 14),
    "j": (2, 0, 6, 2, 2, 18, 12),
    "k": (16, 16, 18, 20, 24, 20, 18),
    "l": (12, 4, 4, 4, 4, 4, 14),
    "m": (0, 0, 26, 21, 21, 17, 17),
    "n": (0, 0, 22, 25, 17, 17, 17),
    "o": (0, 0, 14, 17, 17, 17, 14),
    "p": (0, 0, 30, 17, 30, 16, 16),
    "q": (0, 0, 15, 17, 15, 1, 1),
    "r": (0, 0, 22, 25, 16, 16, 16),
    "s": (0, 0, 14, 16, 14, 1, 30),
    "t": (8, 8, 28, 8, 8, 9, 6),
    "u": (0, 0, 17, 17, 17, 19, 13),
    "v": (0, 0, 17, 17, 17, 10, 4),
    "w": (0, 0, 17, 17, 21, 21, 10),
    "x": (0, 0, 17, 10, 4, 10, 17),
    "y": (0, 0, 17, 17, 15, 1, 14),
    "z": (0, 0, 31, 2, 4, 8, 31),
}


def _hex_rgb(hex_color: str) -> tuple[int, int, int]:
    h = hex_color.lstrip("#")
    return int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)


class Canvas:
    """Simple pure-Python RGB canvas with PNG export."""

    def __init__(self, w: int, h: int, bg: str = "#ffffff"):
        self.w = w
        self.h = h
        r, g, b = _hex_rgb(bg)
        self.buf = bytearray([r, g, b] * (w * h))

    def set_px(self, x: int, y: int, rgb: tuple[int, int, int], alpha: float = 1.0):
        if x < 0 or x >= self.w or y < 0 or y >= self.h:
            return
        idx = (y * self.w + x) * 3
        if alpha >= 1.0:
            self.buf[idx] = rgb[0]
            self.buf[idx + 1] = rgb[1]
            self.buf[idx + 2] = rgb[2]
        elif alpha > 0.0:
            inv = 1.0 - alpha
            self.buf[idx] = int(self.buf[idx] * inv + rgb[0] * alpha)
            self.buf[idx + 1] = int(self.buf[idx + 1] * inv + rgb[1] * alpha)
            self.buf[idx + 2] = int(self.buf[idx + 2] * inv + rgb[2] * alpha)

    def fill_rect(self, x: float, y: float, w: float, h: float, color: str, alpha: float = 1.0):
        rgb = _hex_rgb(color)
        x0 = max(0, int(round(x)))
        y0 = max(0, int(round(y)))
        x1 = min(self.w, int(round(x + w)))
        y1 = min(self.h, int(round(y + h)))
        for py in range(y0, y1):
            for px in range(x0, x1):
                self.set_px(px, py, rgb, alpha)

    def stroke_rect(self, x: float, y: float, w: float, h: float, color: str, thickness: int = 1):
        self.draw_line(x, y, x + w, y, color, thickness)
        self.draw_line(x, y + h, x + w, y + h, color, thickness)
        self.draw_line(x, y, x, y + h, color, thickness)
        self.draw_line(x + w, y, x + w, y + h, color, thickness)

    def draw_line(self, x0: float, y0: float, x1: float, y1: float, color: str, thickness: int = 1):
        rgb = _hex_rgb(color)
        dx = x1 - x0
        dy = y1 - y0
        steps = max(1, int(math.ceil(max(abs(dx), abs(dy)) * 1.5)))
        r0 = -(thickness // 2)
        r1 = r0 + thickness
        for i in range(steps + 1):
            t = i / steps
            cx = int(round(x0 + dx * t))
            cy = int(round(y0 + dy * t))
            for oy in range(r0, r1):
                for ox in range(r0, r1):
                    self.set_px(cx + ox, cy + oy, rgb)

    def draw_text(
        self,
        x: float,
        y: float,
        text: str,
        color: str = "#0f172a",
        scale: int = 2,
        align: str = "left",
        vertical: bool = False,
    ):
        rgb = _hex_rgb(color)
        adv = 6 * scale
        tw = len(text) * adv - scale if text else 0
        th = 7 * scale
        if vertical:
            start_x = int(round(x - th / 2))
            start_y = int(round(y + tw / 2)) if align == "center" else int(round(y))
            for ch in text:
                glyph = FONT_5X7.get(ch, FONT_5X7[" "])
                for row in range(7):
                    bits = glyph[row]
                    for col in range(5):
                        if bits & (1 << (4 - col)):
                            for sy in range(scale):
                                for sx in range(scale):
                                    px = start_x + row * scale + sy
                                    py = start_y - (col * scale + sx)
                                    self.set_px(px, py, rgb)
                start_y -= adv
            return

        if align == "center":
            start_x = int(round(x - tw / 2))
        elif align == "right":
            start_x = int(round(x - tw))
        else:
            start_x = int(round(x))
        start_y = int(round(y))

        for ch in text:
            glyph = FONT_5X7.get(ch, FONT_5X7[" "])
            for row in range(7):
                bits = glyph[row]
                for col in range(5):
                    if bits & (1 << (4 - col)):
                        for sy in range(scale):
                            for sx in range(scale):
                                self.set_px(start_x + col * scale + sx, start_y + row * scale + sy, rgb)
            start_x += adv

    def save_png(self, out_path: pathlib.Path):
        raw = bytearray()
        stride = self.w * 3
        for y in range(self.h):
            raw.append(0)  # filter type 0
            start = y * stride
            raw.extend(self.buf[start : start + stride])
        compressed = zlib.compress(bytes(raw), level=6)

        def chunk(tag: bytes, data: bytes) -> bytes:
            return struct.pack(">I", len(data)) + tag + data + struct.pack(">I", zlib.crc32(tag + data) & 0xFFFFFFFF)

        ihdr = struct.pack(">IIBBBBB", self.w, self.h, 8, 2, 0, 0, 0)
        png = b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", ihdr) + chunk(b"IDAT", compressed) + chunk(b"IEND", b"")
        out_path.write_bytes(png)


def parse_args():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--results-dir", type=pathlib.Path, default=DEFAULT_RESULTS)
    parser.add_argument("--conv-algos", nargs="+", default=["TS", "SA", "GA", "GA_LS", "GRASP"])
    return parser.parse_args()


def resolve_path(p: pathlib.Path) -> pathlib.Path:
    return p if p.is_absolute() else ROOT / p


def quantiles(vals: list[float]) -> tuple[float, float, float, float, float]:
    s = sorted(vals)
    n = len(s)
    if n == 1:
        return s[0], s[0], s[0], s[0], s[0]
    med = _median(s)
    mid = n // 2
    lower = s[:mid] if n % 2 == 0 else s[: mid + 1]
    upper = s[mid:]
    q1 = _median(lower)
    q3 = _median(upper)
    return s[0], q1, med, q3, s[-1]


def draw_convergence(inst: str, conv_dir: pathlib.Path, out_path: pathlib.Path, algos: list[str]):
    series: dict[str, list[list[tuple[float, float]]]] = defaultdict(list)
    max_t = 0.0
    for algo in algos:
        for p in sorted(conv_dir.glob(f"{inst}_{algo}_s*_conv.csv")):
            pts: list[tuple[float, float]] = []
            with p.open(newline="", encoding="utf-8") as f:
                for r in csv.DictReader(f):
                    t_s = float(r["time_s"])
                    b = float(r["best"])
                    pts.append((t_s, b))
                    if t_s > max_t:
                        max_t = t_s
            if pts:
                pts.sort(key=lambda x: x[0])
                series[algo].append(pts)

    if not series:
        return
    if max_t <= 0:
        max_t = 1.0

    grid_n = 40
    t_grid = [max_t * i / grid_n for i in range(grid_n + 1)]
    curves: dict[str, list[tuple[float, float]]] = {}
    y_min, y_max = math.inf, -math.inf

    for algo, runs in series.items():
        curve: list[tuple[float, float]] = []
        for tg in t_grid:
            vals = []
            for pts in runs:
                cur = pts[0][1]
                for ts, b in pts:
                    if ts <= tg + 1e-9:
                        cur = b
                    else:
                        break
                vals.append(cur)
            med = _median(vals)
            curve.append((tg, med))
            y_min = min(y_min, med)
            y_max = max(y_max, med)
        curves[algo] = curve

    if y_min == y_max:
        y_min -= 1.0
        y_max += 1.0
    pad = (y_max - y_min) * 0.08
    y_min -= pad
    y_max += pad

    W, H = 960, 540
    L, R, T, B = 100, 175, 65, 70
    pw, ph = W - L - R, H - T - B

    def sx(t: float) -> float:
        return L + (t / max_t) * pw

    def sy(v: float) -> float:
        return T + (1.0 - (v - y_min) / (y_max - y_min)) * ph

    c = Canvas(W, H)
    c.draw_text(W // 2, 20, f"Median Convergence - {inst}", color="#0f172a", scale=2, align="center")

    for i in range(6):
        yv = y_min + (y_max - y_min) * i / 5
        yy = sy(yv)
        c.draw_line(L, yy, L + pw, yy, "#e2e8f0", 1)
        c.draw_text(L - 10, yy - 6, f"{yv:.1f}", color="#475569", scale=2, align="right")

    for i in range(6):
        tv = max_t * i / 5
        xx = sx(tv)
        c.draw_line(xx, T, xx, T + ph, "#f1f5f9", 1)
        c.draw_text(xx, T + ph + 14, f"{tv:.2f}s", color="#475569", scale=2, align="center")

    c.stroke_rect(L, T, pw, ph, "#94a3b8", 2)
    c.draw_text(L + pw // 2, H - 24, "Time (s)", color="#334155", scale=2, align="center")
    c.draw_text(22, T + ph // 2, "Best Cost (median)", color="#334155", scale=2, align="center", vertical=True)

    for idx, algo in enumerate(curves):
        color = PALETTE.get(algo, "#334155")
        pts = curves[algo]
        for k in range(len(pts) - 1):
            c.draw_line(sx(pts[k][0]), sy(pts[k][1]), sx(pts[k + 1][0]), sy(pts[k + 1][1]), color, 3)
        ly = T + 24 + idx * 30
        c.draw_line(L + pw + 18, ly + 6, L + pw + 48, ly + 6, color, 3)
        c.draw_text(L + pw + 58, ly, algo, color="#1e293b", scale=2, align="left")

    c.save_png(out_path)


def _draw_boxplot_panel(c: Canvas, inst: str, by_algo: dict[str, list[float]], x0: int, y0: int, pw: int, ph: int, show_title: bool = True):
    algos = [a for a in ALGO_ORDER if a in by_algo and by_algo[a]]
    if not algos:
        return
    all_vals = [v for a in algos for v in by_algo[a]]
    y_min, y_max = min(all_vals), max(all_vals)
    if y_min == y_max:
        y_min -= 1.0
        y_max += 1.0
    pad = (y_max - y_min) * 0.1
    y_min -= pad
    y_max += pad

    def sy(v: float) -> float:
        return y0 + (1.0 - (v - y_min) / (y_max - y_min)) * ph

    if show_title:
        c.draw_text(x0 + pw // 2, y0 - 30, inst, color="#0f172a", scale=2, align="center")

    for i in range(6):
        yv = y_min + (y_max - y_min) * i / 5
        yy = sy(yv)
        c.draw_line(x0, yy, x0 + pw, yy, "#e2e8f0", 1)
        c.draw_text(x0 - 8, yy - 6, f"{yv:.1f}", color="#475569", scale=2, align="right")

    c.stroke_rect(x0, y0, pw, ph, "#94a3b8", 2)
    step = pw / len(algos)
    box_w = min(46.0, step * 0.55)

    for idx, algo in enumerate(algos):
        vmin, q1, med, q3, vmax = quantiles(by_algo[algo])
        cx = x0 + step * (idx + 0.5)
        color = PALETTE.get(algo, "#334155")
        y_min_p, y_q1, y_med, y_q3, y_max_p = sy(vmin), sy(q1), sy(med), sy(q3), sy(vmax)

        c.draw_line(cx, y_max_p, cx, y_min_p, color, 2)
        c.draw_line(cx - box_w * 0.25, y_max_p, cx + box_w * 0.25, y_max_p, color, 2)
        c.draw_line(cx - box_w * 0.25, y_min_p, cx + box_w * 0.25, y_min_p, color, 2)
        box_h = max(3.0, y_q1 - y_q3)
        c.fill_rect(cx - box_w / 2, y_q3, box_w, box_h, color, alpha=0.25)
        c.stroke_rect(cx - box_w / 2, y_q3, box_w, box_h, color, 2)
        c.draw_line(cx - box_w / 2, y_med, cx + box_w / 2, y_med, "#0f172a", 3)
        c.draw_text(cx, y0 + ph + 14, algo, color="#1e293b", scale=1 if len(algos) > 6 and pw < 450 else 2, align="center")


def draw_boxplot(inst: str, by_algo: dict[str, list[float]], out_path: pathlib.Path):
    algos = [a for a in ALGO_ORDER if a in by_algo and by_algo[a]]
    if not algos:
        return
    W, H = 960, 520
    L, R, T, B = 100, 35, 65, 70
    c = Canvas(W, H)
    c.draw_text(W // 2, 20, f"Cost Distribution (10 seeds) - {inst}", color="#0f172a", scale=2, align="center")
    _draw_boxplot_panel(c, inst, by_algo, L, T, W - L - R, H - T - B, show_title=False)
    c.save_png(out_path)


def draw_boxplot_mid(by_inst_algo: dict[str, dict[str, list[float]]], out_path: pathlib.Path):
    mids = ["vua_100x400_s201", "vua_150x600_s202", "vua_200x1000_s203"]
    present = [m for m in mids if m in by_inst_algo]
    if not present:
        return
    W, H = 1400, 480
    c = Canvas(W, H)
    c.draw_text(W // 2, 16, "Cost Distribution on Mid Instances (10 seeds, 0.5s)", color="#0f172a", scale=2, align="center")
    n = len(present)
    panel_w = (W - 90 - (n - 1) * 70) // n
    ph = H - 140
    for i, inst in enumerate(present):
        x0 = 80 + i * (panel_w + 70)
        _draw_boxplot_panel(c, inst, by_inst_algo[inst], x0, 85, panel_w, ph, show_title=True)
    c.save_png(out_path)


def draw_gap_bar(summary_csv: pathlib.Path, out_path: pathlib.Path):
    if not summary_csv.exists():
        return
    gaps: dict[str, list[float]] = defaultdict(list)
    with summary_csv.open(newline="", encoding="utf-8") as f:
        for r in csv.DictReader(f):
            algo = r["algorithm"]
            if algo == "EXACT" or not r["gap_mean_pct"]:
                continue
            gaps[algo].append(float(r["gap_mean_pct"]))

    algos = [a for a in ALGO_ORDER if a in gaps]
    if not algos:
        return
    means = [_mean(gaps[a]) for a in algos]
    max_g = max(max(means), 1.0) * 1.18

    W, H = 960, 500
    L, R, T, B = 100, 35, 65, 70
    pw, ph = W - L - R, H - T - B
    c = Canvas(W, H)
    c.draw_text(W // 2, 20, "Mean Gap (%) vs Reference (lower is better)", color="#0f172a", scale=2, align="center")

    for i in range(6):
        yv = max_g * i / 5
        yy = T + (1.0 - yv / max_g) * ph
        c.draw_line(L, yy, L + pw, yy, "#e2e8f0", 1)
        c.draw_text(L - 10, yy - 6, f"{yv:.1f}%", color="#475569", scale=2, align="right")

    c.stroke_rect(L, T, pw, ph, "#94a3b8", 2)
    step = pw / len(algos)
    bar_w = min(64.0, step * 0.6)
    for idx, (algo, val) in enumerate(zip(algos, means)):
        cx = L + step * (idx + 0.5)
        bh = (val / max_g) * ph
        by = T + ph - bh
        color = PALETTE.get(algo, "#334155")
        c.fill_rect(cx - bar_w / 2, by, bar_w, bh, color, alpha=0.85)
        c.draw_text(cx, by - 20, f"{val:.2f}%", color="#0f172a", scale=2, align="center")
        c.draw_text(cx, T + ph + 14, algo, color="#1e293b", scale=2, align="center")

    c.save_png(out_path)


def main():
    args = parse_args()
    res_dir = resolve_path(args.results_dir)
    raw_dir = res_dir / "raw"
    conv_dir = res_dir / "conv"
    fig_dir = res_dir / "figures"
    fig_dir.mkdir(parents=True, exist_ok=True)

    # Xóa các tệp SVG cũ nếu còn tồn tại
    for old_svg in fig_dir.glob("*.svg"):
        old_svg.unlink()

    by_inst_algo: dict[str, dict[str, list[float]]] = defaultdict(lambda: defaultdict(list))
    for p in sorted(raw_dir.glob("*.csv")):
        with p.open(newline="", encoding="utf-8") as f:
            for r in csv.DictReader(f):
                if r["algorithm"] == "EXACT" or int(r["feasible"]) != 1:
                    continue
                by_inst_algo[r["instance"]][r["algorithm"]].append(float(r["best_value"]))

    count = 0
    for inst in sorted(by_inst_algo.keys()):
        draw_convergence(inst, conv_dir, fig_dir / f"conv_{inst}.png", args.conv_algos)
        draw_boxplot(inst, by_inst_algo[inst], fig_dir / f"boxplot_{inst}.png")
        count += 2

    draw_boxplot_mid(by_inst_algo, fig_dir / "boxplot_mid.png")
    draw_gap_bar(res_dir / "summary.csv", fig_dir / "gap_comparison.png")

    # Đồng bộ 4 hình chính vào report/figures/ cho LaTeX
    rep_fig_dir = ROOT / "report" / "figures"
    rep_fig_dir.mkdir(parents=True, exist_ok=True)
    mapping = {
        "conv_nho_25x30_s104.png": "conv_nho.png",
        "conv_vua_100x400_s201.png": "conv_vua1.png",
        "conv_vua_200x1000_s203.png": "conv_vua3.png",
        "boxplot_mid.png": "boxplot_mid.png",
    }
    for src_name, dst_name in mapping.items():
        src_p = fig_dir / src_name
        if src_p.exists():
            shutil.copy2(src_p, rep_fig_dir / dst_name)

    print(f"Đã tạo {count + 2} biểu đồ PNG trong {fig_dir} và đồng bộ vào {rep_fig_dir}")


if __name__ == "__main__":
    main()
