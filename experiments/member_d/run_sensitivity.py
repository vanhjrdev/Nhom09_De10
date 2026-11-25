#!/usr/bin/env python3
"""Phân tích độ nhạy tham số cho GRASP (alpha) và SA (t0_factor, cool_alpha)
trên tập tinh chỉnh riêng (tune_100x400_s901, tune_150x600_s902).
"""

import argparse
import csv
import math
import pathlib
import sys
import tempfile


for stream in (sys.stdout, sys.stderr):
    if hasattr(stream, "reconfigure"):
        stream.reconfigure(encoding="utf-8")


ROOT = pathlib.Path(__file__).resolve().parents[2]
SRC = ROOT / "src"
sys.path.insert(0, str(SRC))

from aco_or_grasp import GRASPSolver
from main_A import SASolver
from scp_core import SCPInstance


def mean(xs: list[float]) -> float:
    return sum(xs) / len(xs)


def stdev(xs: list[float]) -> float:
    if len(xs) < 2:
        return 0.0
    m = mean(xs)
    return math.sqrt(sum((x - m) ** 2 for x in xs) / (len(xs) - 1))


def parse_args():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--budget", type=float, default=0.3)
    p.add_argument("--seeds", type=int, nargs="+", default=list(range(1, 11)))
    return p.parse_args()


def main():
    args = parse_args()
    tune_dir = ROOT / "experiments" / "member_b" / "tuning_data"
    instances = sorted(tune_dir.glob("*.txt"))
    if not instances:
        raise SystemExit("Không tìm thấy tập tinh chỉnh trong experiments/member_b/tuning_data")

    grasp_configs = [
        ("alpha=0.00 (pure greedy)", 0.0),
        ("alpha=0.05", 0.05),
        ("alpha=0.10", 0.10),
        ("alpha=0.20", 0.20),
        ("alpha=0.30", 0.30),
        ("alpha=U(0.02,0.12) [default]", None),
    ]
    grasp_rows = []
    for inst_path in instances:
        inst = SCPInstance()
        inst.load_from_file(str(inst_path))
        for label, alpha in grasp_configs:
            vals = []
            for seed in args.seeds:
                cost, _ = GRASPSolver(inst, seed=seed, alpha=alpha).solve(budget_sec=args.budget, conv_file=None)
                vals.append(cost)
            grasp_rows.append(
                {
                    "instance": inst_path.stem,
                    "config": label,
                    "best": int(min(vals)),
                    "mean": f"{mean(vals):.2f}",
                    "std": f"{stdev(vals):.2f}",
                }
            )
            print(f"[GRASP {inst_path.stem}] {label:<28} -> best={min(vals)} | mean={mean(vals):.2f} ± {stdev(vals):.2f}")

    out_d = ROOT / "results" / "member_d"
    out_d.mkdir(parents=True, exist_ok=True)
    grasp_csv = out_d / "grasp_sensitivity.csv"
    with grasp_csv.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["instance", "config", "best", "mean", "std"])
        w.writeheader()
        w.writerows(grasp_rows)
    print(f"Đã ghi: {grasp_csv}")

    sa_configs = [
        ("t0=0.02;cool=0.995", 0.02, 0.995),
        ("t0=0.05;cool=0.995 [default]", 0.05, 0.995),
        ("t0=0.10;cool=0.995", 0.10, 0.995),
        ("t0=0.20;cool=0.995", 0.20, 0.995),
        ("t0=0.05;cool=0.980", 0.05, 0.980),
        ("t0=0.05;cool=0.990", 0.05, 0.990),
        ("t0=0.05;cool=0.999", 0.05, 0.999),
    ]
    sa_rows = []
    with tempfile.TemporaryDirectory() as tmp:
        tmp_conv = str(pathlib.Path(tmp) / "sa_conv.csv")
        for inst_path in instances:
            inst = SCPInstance()
            inst.load_from_file(str(inst_path))
            for label, t0_f, cool_a in sa_configs:
                vals = []
                for seed in args.seeds:
                    cost, _ = SASolver(inst, seed=seed).solve(
                        budget_sec=args.budget,
                        conv_csv_file=tmp_conv,
                        t0_factor=t0_f,
                        cool_alpha=cool_a,
                    )
                    vals.append(cost)
                sa_rows.append(
                    {
                        "instance": inst_path.stem,
                        "config": label,
                        "best": int(min(vals)),
                        "mean": f"{mean(vals):.2f}",
                        "std": f"{stdev(vals):.2f}",
                    }
                )
                print(f"[SA    {inst_path.stem}] {label:<28} -> best={min(vals)} | mean={mean(vals):.2f} ± {stdev(vals):.2f}")

    sa_csv = out_d / "sa_sensitivity.csv"
    with sa_csv.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["instance", "config", "best", "mean", "std"])
        w.writeheader()
        w.writerows(sa_rows)
    print(f"Đã ghi: {sa_csv}")


if __name__ == "__main__":
    main()
