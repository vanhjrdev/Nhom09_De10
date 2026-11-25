#!/usr/bin/env python3
"""Thực nghiệm riêng của Thành viên B:
1) Đối sánh GREEDY, HC_FI, HC_BI, TS trên data/tusinh và data/chuan (seed 1..10).
2) Phân tích độ nhạy tham số TS (tenure, sample) trên tập tinh chỉnh riêng (seed sinh 901, 902).
"""

import argparse
import csv
import math
import pathlib
import random
import subprocess
import sys
import time


for stream in (sys.stdout, sys.stderr):
    if hasattr(stream, "reconfigure"):
        stream.reconfigure(encoding="utf-8")


ROOT = pathlib.Path(__file__).resolve().parents[2]
SRC = ROOT / "src"
sys.path.insert(0, str(SRC))

from gen_scp import generate_scp_text
from greedy import greedy_chvatal, load_instance
from local_search import hill_climb
from tabu import tabu_search


OPT_REF = {
    "nho_10x20_s101": 65,
    "nho_15x25_s102": 136,
    "nho_20x28_s103": 212,
    "nho_25x30_s104": 133,
    "scp41": 429,
    "scp51": 253,
    "scp61": 138,
}


def mean(xs: list[float]) -> float:
    return sum(xs) / len(xs)


def stdev(xs: list[float]) -> float:
    if len(xs) < 2:
        return 0.0
    m = mean(xs)
    return math.sqrt(sum((x - m) ** 2 for x in xs) / (len(xs) - 1))


def parse_args():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--budget", type=float, default=0.5, help="Ngân sách giây mỗi lần chạy đánh giá")
    parser.add_argument("--tune-budget", type=float, default=0.3, help="Ngân sách giây mỗi lần chạy tinh chỉnh TS")
    parser.add_argument("--seeds", type=int, nargs="+", default=list(range(1, 11)))
    return parser.parse_args()


def ensure_tuning_instances(tune_dir: pathlib.Path) -> list[pathlib.Path]:
    tune_dir.mkdir(parents=True, exist_ok=True)
    specs = [
        ("tune_100x400_s901.txt", 100, 400, 0.05, 901),
        ("tune_150x600_s902.txt", 150, 600, 0.04, 902),
    ]
    paths = []
    for name, m, n, d, seed in specs:
        p = tune_dir / name
        if not p.exists():
            p.write_text(generate_scp_text(m, n, d, seed), encoding="utf-8")
        paths.append(p)
    return paths


def verify_sol(inst_path: pathlib.Path, sol_path: pathlib.Path, val: int, cols: list[int]):
    sol_path.parent.mkdir(parents=True, exist_ok=True)
    sol_path.write_text(f"{val}\n{' '.join(str(j + 1) for j in sorted(cols))}\n", encoding="utf-8")
    res = subprocess.run(
        [sys.executable, str(SRC / "kiemtra.py"), str(inst_path), str(sol_path)],
        check=True,
        capture_output=True,
        text=True,
    )
    if not res.stdout.strip().startswith("HOP LE |"):
        raise RuntimeError(f"Nghiệm không hợp lệ {sol_path}: {res.stdout}")


def run_eval_b(instances: list[pathlib.Path], seeds: list[int], budget: float, out_dir: pathlib.Path):
    sol_dir = out_dir / "solutions"
    rows = []
    for inst_path in instances:
        inst = load_instance(str(inst_path))
        name = inst_path.stem
        algos = ["GREEDY", "HC_FI", "HC_BI", "TS"]
        inst_vals: dict[str, list[float]] = {a: [] for a in algos}
        inst_times: dict[str, list[float]] = {a: [] for a in algos}

        for seed in seeds:
            # GREEDY
            t0 = time.time()
            st = greedy_chvatal(inst)
            el = time.time() - t0
            verify_sol(inst_path, sol_dir / f"{name}_GREEDY_s{seed}.sol", st.value, st.chosen())
            inst_vals["GREEDY"].append(st.value)
            inst_times["GREEDY"].append(el)

            # HC_FI, HC_BI
            for algo, bi in (("HC_FI", False), ("HC_BI", True)):
                rng = random.Random(seed)
                t0 = time.time()
                st = greedy_chvatal(inst)
                log = [(0.0, 0, 0, st.value)]
                hill_climb(st, rng, t0 + budget, bi, log, t0)
                el = time.time() - t0
                verify_sol(inst_path, sol_dir / f"{name}_{algo}_s{seed}.sol", st.value, st.chosen())
                inst_vals[algo].append(st.value)
                inst_times[algo].append(el)

            # TS
            rng = random.Random(seed)
            t0 = time.time()
            val, cols, _, _, _, _ = tabu_search(inst, rng, budget, t0)
            el = time.time() - t0
            verify_sol(inst_path, sol_dir / f"{name}_TS_s{seed}.sol", val, cols)
            inst_vals["TS"].append(val)
            inst_times["TS"].append(el)

        ref = OPT_REF.get(name, int(min(min(vs) for vs in inst_vals.values())))
        ref_type = "OPT" if name in OPT_REF else "BKS_B"
        for algo in algos:
            vs = inst_vals[algo]
            ts = inst_times[algo]
            best_v = min(vs)
            mean_v = mean(vs)
            rows.append(
                {
                    "instance": name,
                    "m": inst[0],
                    "n": inst[1],
                    "ref": ref,
                    "ref_type": ref_type,
                    "algorithm": algo,
                    "best": int(best_v),
                    "mean": f"{mean_v:.2f}",
                    "std": f"{stdev(vs):.2f}",
                    "gap_best_pct": f"{(best_v - ref) / ref * 100:.2f}",
                    "gap_mean_pct": f"{(mean_v - ref) / ref * 100:.2f}",
                    "mean_time_s": f"{mean(ts):.4f}",
                }
            )
        print(
            f"[{name}] GREEDY={min(inst_vals['GREEDY'])} | HC_FI={mean(inst_vals['HC_FI']):.2f} "
            f"| HC_BI={mean(inst_vals['HC_BI']):.2f} | TS={mean(inst_vals['TS']):.2f}"
        )

    csv_path = out_dir / "eval_member_b.csv"
    with csv_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)
    print(f"Đã ghi: {csv_path}")


def run_ts_sensitivity(tune_instances: list[pathlib.Path], seeds: list[int], budget: float, out_dir: pathlib.Path):
    configs = [
        ("tenure=3;sample=40", 3, 40),
        ("tenure=5;sample=40", 5, 40),
        ("tenure=10;sample=40", 10, 40),
        ("tenure=15;sample=40", 15, 40),
        ("tenure=auto;sample=40", None, 40),
        ("tenure=auto;sample=10", None, 10),
        ("tenure=auto;sample=20", None, 20),
        ("tenure=auto;sample=80", None, 80),
    ]
    rows = []
    for inst_path in tune_instances:
        inst = load_instance(str(inst_path))
        name = inst_path.stem
        for label, tenure, sample in configs:
            vals = []
            evals_list = []
            t_bests = []
            for seed in seeds:
                rng = random.Random(seed)
                t0 = time.time()
                val, cols, _, t_best, ev, _ = tabu_search(inst, rng, budget, t0, tenure=tenure, sample=sample)
                sol_path = out_dir / "tuning_solutions" / f"{name}_{label.replace(';', '_')}_s{seed}.sol"
                verify_sol(inst_path, sol_path, val, cols)
                vals.append(val)
                evals_list.append(ev)
                t_bests.append(t_best)
            rows.append(
                {
                    "instance": name,
                    "config": label,
                    "tenure": "auto" if tenure is None else tenure,
                    "sample": sample,
                    "best": int(min(vals)),
                    "mean": f"{mean(vals):.2f}",
                    "std": f"{stdev(vals):.2f}",
                    "mean_evals": f"{mean(evals_list):.1f}",
                    "mean_time_to_best_s": f"{mean(t_bests):.4f}",
                }
            )
            print(f"  [Tune {name}] {label:<22} -> best={min(vals)} | mean={mean(vals):.2f} ± {stdev(vals):.2f}")

    csv_path = out_dir / "ts_sensitivity.csv"
    with csv_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)
    print(f"Đã ghi: {csv_path}")


def main():
    args = parse_args()
    out_dir = ROOT / "results" / "member_b"
    out_dir.mkdir(parents=True, exist_ok=True)

    eval_instances = sorted((ROOT / "data" / "tusinh").glob("*.txt")) + sorted((ROOT / "data" / "chuan").glob("*.txt"))
    eval_instances = [p for p in eval_instances if p.name.upper() != "LINKS.TXT"]
    run_eval_b(eval_instances, args.seeds, args.budget, out_dir)

    tune_instances = ensure_tuning_instances(ROOT / "experiments" / "member_b" / "tuning_data")
    run_ts_sensitivity(tune_instances, args.seeds, args.tune_budget, out_dir)


if __name__ == "__main__":
    main()
