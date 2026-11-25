#!/usr/bin/env python3
"""Vẽ biểu đồ hội tụ, boxplot và so sánh gap (SVG thuần Python chuẩn) vào results/figures/."""

import argparse
import csv
import html
import math
import pathlib
import sys
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


def svg_header(w: int, h: int, title: str) -> list[str]:
    return [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" style="background:#ffffff;font-family:Segoe UI,Arial,sans-serif">',
        f'  <text x="{w // 2}" y="28" text-anchor="middle" font-size="16" font-weight="bold" fill="#0f172a">{html.escape(title)}</text>',
    ]


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

    W, H = 760, 440
    L, R, T, B = 75, 130, 50, 55
    pw, ph = W - L - R, H - T - B

    def sx(t: float) -> float:
        return L + (t / max_t) * pw

    def sy(v: float) -> float:
        return T + (1.0 - (v - y_min) / (y_max - y_min)) * ph

    lines = svg_header(W, H, f"Đường hội tụ trung vị — {inst}")
    # Grid & axes
    for i in range(6):
        yv = y_min + (y_max - y_min) * i / 5
        yy = sy(yv)
        lines.append(f'  <line x1="{L}" y1="{yy:.1f}" x2="{L+pw}" y2="{yy:.1f}" stroke="#e2e8f0" stroke-width="1"/>')
        lines.append(f'  <text x="{L-8}" y="{yy+4:.1f}" text-anchor="end" font-size="11" fill="#475569">{yv:.1f}</text>')
    for i in range(6):
        tv = max_t * i / 5
        xx = sx(tv)
        lines.append(f'  <line x1="{xx:.1f}" y1="{T}" x2="{xx:.1f}" y2="{T+ph}" stroke="#f1f5f9" stroke-width="1"/>')
        lines.append(f'  <text x="{xx:.1f}" y="{T+ph+18}" text-anchor="middle" font-size="11" fill="#475569">{tv:.2f}s</text>')

    lines.append(f'  <rect x="{L}" y="{T}" width="{pw}" height="{ph}" fill="none" stroke="#94a3b8" stroke-width="1.2"/>')
    lines.append(f'  <text x="{L + pw // 2}" y="{H - 12}" text-anchor="middle" font-size="12" fill="#334155">Thời gian (giây)</text>')
    lines.append(f'  <text x="18" y="{T + ph // 2}" text-anchor="middle" font-size="12" fill="#334155" transform="rotate(-90 18 {T + ph // 2})">Chi phí tốt nhất (trung vị)</text>')

    for idx, algo in enumerate(curves):
        color = PALETTE.get(algo, "#334155")
        pts_str = " ".join(f"{sx(t):.1f},{sy(v):.1f}" for t, v in curves[algo])
        lines.append(f'  <polyline fill="none" stroke="{color}" stroke-width="2.2" points="{pts_str}"/>')
        ly = T + 18 + idx * 22
        lines.append(f'  <line x1="{L+pw+14}" y1="{ly}" x2="{L+pw+34}" y2="{ly}" stroke="{color}" stroke-width="2.5"/>')
        lines.append(f'  <text x="{L+pw+40}" y="{ly+4}" font-size="12" fill="#1e293b">{algo}</text>')

    lines.append("</svg>")
    out_path.write_text("\n".join(lines), encoding="utf-8")


def draw_boxplot(inst: str, by_algo: dict[str, list[float]], out_path: pathlib.Path):
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

    W, H = 760, 420
    L, R, T, B = 75, 30, 50, 55
    pw, ph = W - L - R, H - T - B

    def sy(v: float) -> float:
        return T + (1.0 - (v - y_min) / (y_max - y_min)) * ph

    lines = svg_header(W, H, f"Phân bố chi phí qua các seed — {inst}")
    for i in range(6):
        yv = y_min + (y_max - y_min) * i / 5
        yy = sy(yv)
        lines.append(f'  <line x1="{L}" y1="{yy:.1f}" x2="{L+pw}" y2="{yy:.1f}" stroke="#e2e8f0" stroke-width="1"/>')
        lines.append(f'  <text x="{L-8}" y="{yy+4:.1f}" text-anchor="end" font-size="11" fill="#475569">{yv:.1f}</text>')

    lines.append(f'  <rect x="{L}" y="{T}" width="{pw}" height="{ph}" fill="none" stroke="#94a3b8" stroke-width="1.2"/>')
    step = pw / len(algos)
    box_w = min(44.0, step * 0.55)

    for idx, algo in enumerate(algos):
        vmin, q1, med, q3, vmax = quantiles(by_algo[algo])
        cx = L + step * (idx + 0.5)
        color = PALETTE.get(algo, "#334155")
        y_min_p, y_q1, y_med, y_q3, y_max_p = sy(vmin), sy(q1), sy(med), sy(q3), sy(vmax)

        lines.append(f'  <line x1="{cx:.1f}" y1="{y_max_p:.1f}" x2="{cx:.1f}" y2="{y_min_p:.1f}" stroke="{color}" stroke-width="1.5"/>')
        lines.append(f'  <line x1="{cx-box_w*0.25:.1f}" y1="{y_max_p:.1f}" x2="{cx+box_w*0.25:.1f}" y2="{y_max_p:.1f}" stroke="{color}" stroke-width="1.5"/>')
        lines.append(f'  <line x1="{cx-box_w*0.25:.1f}" y1="{y_min_p:.1f}" x2="{cx+box_w*0.25:.1f}" y2="{y_min_p:.1f}" stroke="{color}" stroke-width="1.5"/>')
        box_h = max(2.0, y_q1 - y_q3)
        lines.append(f'  <rect x="{cx-box_w/2:.1f}" y="{y_q3:.1f}" width="{box_w:.1f}" height="{box_h:.1f}" fill="{color}" fill-opacity="0.25" stroke="{color}" stroke-width="1.8"/>')
        lines.append(f'  <line x1="{cx-box_w/2:.1f}" y1="{y_med:.1f}" x2="{cx+box_w/2:.1f}" y2="{y_med:.1f}" stroke="#0f172a" stroke-width="2.2"/>')
        lines.append(f'  <text x="{cx:.1f}" y="{T+ph+18}" text-anchor="middle" font-size="11" fill="#1e293b">{algo}</text>')

    lines.append("</svg>")
    out_path.write_text("\n".join(lines), encoding="utf-8")


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
    max_g = max(max(means), 1.0) * 1.15

    W, H = 760, 400
    L, R, T, B = 75, 30, 50, 55
    pw, ph = W - L - R, H - T - B
    lines = svg_header(W, H, "Gap trung bình (%) so với giá trị tham chiếu (nhỏ hơn là tốt hơn)")

    for i in range(6):
        yv = max_g * i / 5
        yy = T + (1.0 - yv / max_g) * ph
        lines.append(f'  <line x1="{L}" y1="{yy:.1f}" x2="{L+pw}" y2="{yy:.1f}" stroke="#e2e8f0" stroke-width="1"/>')
        lines.append(f'  <text x="{L-8}" y="{yy+4:.1f}" text-anchor="end" font-size="11" fill="#475569">{yv:.1f}%</text>')

    lines.append(f'  <rect x="{L}" y="{T}" width="{pw}" height="{ph}" fill="none" stroke="#94a3b8" stroke-width="1.2"/>')
    step = pw / len(algos)
    bar_w = min(48.0, step * 0.6)
    for idx, (algo, val) in enumerate(zip(algos, means)):
        cx = L + step * (idx + 0.5)
        bh = (val / max_g) * ph
        by = T + ph - bh
        color = PALETTE.get(algo, "#334155")
        lines.append(f'  <rect x="{cx-bar_w/2:.1f}" y="{by:.1f}" width="{bar_w:.1f}" height="{bh:.1f}" fill="{color}" fill-opacity="0.85"/>')
        lines.append(f'  <text x="{cx:.1f}" y="{by-6:.1f}" text-anchor="middle" font-size="11" fill="#0f172a">{val:.2f}%</text>')
        lines.append(f'  <text x="{cx:.1f}" y="{T+ph+18}" text-anchor="middle" font-size="11" fill="#1e293b">{algo}</text>')

    lines.append("</svg>")
    out_path.write_text("\n".join(lines), encoding="utf-8")


def main():
    args = parse_args()
    res_dir = resolve_path(args.results_dir)
    raw_dir = res_dir / "raw"
    conv_dir = res_dir / "conv"
    fig_dir = res_dir / "figures"
    fig_dir.mkdir(parents=True, exist_ok=True)

    by_inst_algo: dict[str, dict[str, list[float]]] = defaultdict(lambda: defaultdict(list))
    for p in sorted(raw_dir.glob("*.csv")):
        with p.open(newline="", encoding="utf-8") as f:
            for r in csv.DictReader(f):
                if r["algorithm"] == "EXACT" or int(r["feasible"]) != 1:
                    continue
                by_inst_algo[r["instance"]][r["algorithm"]].append(float(r["best_value"]))

    count = 0
    for inst in sorted(by_inst_algo.keys()):
        draw_convergence(inst, conv_dir, fig_dir / f"conv_{inst}.svg", args.conv_algos)
        draw_boxplot(inst, by_inst_algo[inst], fig_dir / f"boxplot_{inst}.svg")
        count += 2

    draw_gap_bar(res_dir / "summary.csv", fig_dir / "gap_comparison.svg")
    print(f"Đã tạo {count + 1} biểu đồ SVG trong {fig_dir}")


if __name__ == "__main__":
    main()
