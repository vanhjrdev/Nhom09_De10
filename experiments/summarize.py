#!/usr/bin/env python3
"""Tổng hợp kết quả thực nghiệm từ results/raw/*.csv ra summary.csv và summary.md."""

import argparse
import csv
import math
import pathlib
import sys
from collections import defaultdict


def _mean(vals: list[float]) -> float:
    return sum(vals) / len(vals)


def _stdev(vals: list[float]) -> float:
    if len(vals) < 2:
        return 0.0
    m = _mean(vals)
    return math.sqrt(sum((x - m) ** 2 for x in vals) / (len(vals) - 1))


def _median(vals: list[float]) -> float:
    s = sorted(vals)
    n = len(s)
    mid = n // 2
    return s[mid] if n % 2 == 1 else (s[mid - 1] + s[mid]) / 2.0


for stream in (sys.stdout, sys.stderr):
    if hasattr(stream, "reconfigure"):
        stream.reconfigure(encoding="utf-8")


ROOT = pathlib.Path(__file__).resolve().parents[1]
DEFAULT_RAW = ROOT / "results" / "raw"
DEFAULT_OUT = ROOT / "results"

KNOWN_OPT = {
    "vidu": (16, "OPT"),
    "nho_10x20_s101": (65, "OPT"),
    "nho_15x25_s102": (136, "OPT"),
    "nho_20x28_s103": (212, "OPT"),
    "nho_25x30_s104": (133, "OPT"),
    "scp41": (429, "OPT"),
}

ALGO_ORDER = ["EXACT", "GREEDY", "HC_FI", "HC_BI", "TS", "SA", "GA", "GA_LS", "GRASP"]


def parse_args():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--raw-dir", type=pathlib.Path, default=DEFAULT_RAW)
    parser.add_argument("--output-dir", type=pathlib.Path, default=DEFAULT_OUT)
    return parser.parse_args()


def resolve_path(p: pathlib.Path) -> pathlib.Path:
    return p if p.is_absolute() else ROOT / p


def load_raw_rows(raw_dir: pathlib.Path) -> list[dict]:
    rows: list[dict] = []
    for csv_file in sorted(raw_dir.glob("*.csv")):
        with csv_file.open(newline="", encoding="utf-8") as f:
            for row in csv.DictReader(f):
                rows.append(row)
    return rows


def main():
    args = parse_args()
    raw_dir = resolve_path(args.raw_dir)
    out_dir = resolve_path(args.output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    rows = load_raw_rows(raw_dir)
    if not rows:
        raise SystemExit(f"Không tìm thấy dữ liệu trong {raw_dir}")

    grouped: dict[tuple[str, str], list[dict]] = defaultdict(list)
    inst_n: dict[str, int] = {}
    inst_best_feasible: dict[str, float] = defaultdict(lambda: math.inf)
    exact_vals: dict[str, int] = {}

    for r in rows:
        inst = r["instance"]
        algo = r["algorithm"]
        n = int(r["n"])
        inst_n[inst] = n
        grouped[(inst, algo)].append(r)
        if int(r["feasible"]) == 1:
            val = float(r["best_value"])
            if val < inst_best_feasible[inst]:
                inst_best_feasible[inst] = val
            if algo == "EXACT":
                exact_vals[inst] = int(val)

    instances = sorted(inst_n.keys(), key=lambda k: (inst_n[k], k))
    algos_present = sorted(
        {algo for _, algo in grouped.keys()},
        key=lambda a: (ALGO_ORDER.index(a) if a in ALGO_ORDER else 999, a),
    )

    summary_rows: list[dict] = []
    for inst in instances:
        if inst in exact_vals:
            ref_val, ref_type = exact_vals[inst], "OPT"
        elif inst in KNOWN_OPT:
            ref_val, ref_type = KNOWN_OPT[inst]
        else:
            ref_val, ref_type = int(inst_best_feasible[inst]), "BKS_nhom"

        for algo in algos_present:
            group = grouped.get((inst, algo))
            if not group:
                continue
            feas = [r for r in group if int(r["feasible"]) == 1]
            vals = [float(r["best_value"]) for r in feas]
            times = [float(r["time_s"]) for r in feas]
            t_bests = [float(r["time_to_best_s"]) for r in feas]

            if vals:
                best_v = min(vals)
                mean_v = _mean(vals)
                std_v = _stdev(vals)
                med_v = _median(vals)
                gap_best = (best_v - ref_val) / ref_val * 100.0 if ref_val > 0 else 0.0
                gap_mean = (mean_v - ref_val) / ref_val * 100.0 if ref_val > 0 else 0.0
                opt_rate = (
                    sum(1 for v in vals if v <= ref_val) / len(vals) * 100.0
                    if ref_type == "OPT"
                    else None
                )
                mean_t = _mean(times)
                mean_tb = _mean(t_bests)
            else:
                best_v = mean_v = std_v = med_v = gap_best = gap_mean = mean_t = mean_tb = math.nan
                opt_rate = None

            summary_rows.append(
                {
                    "instance": inst,
                    "n": inst_n[inst],
                    "ref_value": ref_val,
                    "ref_type": ref_type,
                    "algorithm": algo,
                    "runs": len(group),
                    "feasible_runs": len(feas),
                    "best": int(best_v) if not math.isnan(best_v) else "",
                    "mean": f"{mean_v:.2f}" if not math.isnan(mean_v) else "",
                    "std": f"{std_v:.2f}" if not math.isnan(std_v) else "",
                    "median": f"{med_v:.2f}" if not math.isnan(med_v) else "",
                    "gap_best_pct": f"{gap_best:.2f}" if not math.isnan(gap_best) else "",
                    "gap_mean_pct": f"{gap_mean:.2f}" if not math.isnan(gap_mean) else "",
                    "opt_rate_pct": f"{opt_rate:.1f}" if opt_rate is not None else "",
                    "mean_time_s": f"{mean_t:.4f}" if not math.isnan(mean_t) else "",
                    "mean_time_to_best_s": f"{mean_tb:.4f}" if not math.isnan(mean_tb) else "",
                }
            )

    csv_out = out_dir / "summary.csv"
    fieldnames = list(summary_rows[0].keys())
    with csv_out.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(summary_rows)

    md_out = out_dir / "summary.md"
    lines = [
        "# Bảng tổng hợp kết quả thực nghiệm",
        "",
        "| Instance | n | Ref (Loại) | Thuật toán | Best | Mean ± Std | Gap Best (%) | Gap Mean (%) | Tỉ lệ OPT (%) | Time TB (s) |",
        "|---|---:|---|---|---:|---:|---:|---:|---:|---:|",
    ]
    for r in summary_rows:
        opt_str = f"{r['opt_rate_pct']}%" if r["opt_rate_pct"] != "" else "—"
        lines.append(
            f"| {r['instance']} | {r['n']} | {r['ref_value']} ({r['ref_type']}) | {r['algorithm']} "
            f"| {r['best']} | {r['mean']} ± {r['std']} | {r['gap_best_pct']}% | {r['gap_mean_pct']}% "
            f"| {opt_str} | {r['mean_time_s']} |"
        )
    md_out.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print(f"Đã ghi: {csv_out}")
    print(f"Đã ghi: {md_out}")


if __name__ == "__main__":
    main()
