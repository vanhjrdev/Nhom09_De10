#!/usr/bin/env python3
"""Script chạy toàn bộ thực nghiệm (Member D) cho đề tài Nhóm 09 - Đề 10.

Chạy các thuật toán (GREEDY, HC_FI, HC_BI, TS, SA, GA, GA_LS, GRASP, EXACT),
kiểm tra tính hợp lệ từng nghiệm bằng src/kiemtra.py, lưu nghiệm, log hội tụ
và xuất kết quả thô ra results/raw/<thuat_toan>.csv.
"""

import argparse
import csv
import pathlib
import subprocess
import sys
import time


for stream in (sys.stdout, sys.stderr):
    if hasattr(stream, "reconfigure"):
        stream.reconfigure(encoding="utf-8")


ROOT = pathlib.Path(__file__).resolve().parents[1]
DEFAULT_DATA_DIRS = [ROOT / "data" / "tusinh", ROOT / "data" / "chuan"]
DEFAULT_OUTPUT = ROOT / "results"

ALL_ALGORITHMS = ["GREEDY", "HC_FI", "HC_BI", "TS", "SA", "GA", "GA_LS", "GRASP"]
RAW_HEADER = [
    "instance",
    "n",
    "algorithm",
    "params",
    "seed",
    "run",
    "best_value",
    "time_s",
    "time_to_best_s",
    "evaluations",
    "feasible",
]


def parse_args():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--algorithms",
        nargs="+",
        default=ALL_ALGORITHMS,
        help="Danh sách thuật toán cần chạy (mặc định: tất cả trừ EXACT)",
    )
    parser.add_argument(
        "--include-exact",
        action="store_true",
        help="Chạy thêm EXACT cho các instance nhỏ (n <= --exact-max-n)",
    )
    parser.add_argument("--exact-max-n", type=int, default=30)
    parser.add_argument("--exact-budget", type=float, default=60.0)
    parser.add_argument("--budget", type=float, default=0.5, help="Ngân sách giây mỗi lần chạy")
    parser.add_argument("--seeds", type=int, nargs="+", default=list(range(1, 11)))
    parser.add_argument("--population", type=int, default=40, help="Tham số population cho GA/GA_LS")
    parser.add_argument("--mutation-rate", type=float, default=None, help="Tham số mutation_rate cho GA/GA_LS")
    parser.add_argument("--grasp-alpha", type=float, default=None, help="Tham số alpha cho GRASP")
    parser.add_argument("--output", type=pathlib.Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--append", action="store_true", help="Ghi nối vào results/raw/*.csv thay vì tạo mới")
    parser.add_argument(
        "instances",
        type=pathlib.Path,
        nargs="*",
        help="Danh sách file .txt; mặc định lấy trong data/tusinh và data/chuan",
    )
    return parser.parse_args()


def resolve_path(path: pathlib.Path) -> pathlib.Path:
    return path if path.is_absolute() else ROOT / path


def read_mn(instance: pathlib.Path) -> tuple[int, int]:
    tokens = instance.read_text(encoding="utf-8").split(maxsplit=2)
    if len(tokens) < 2:
        raise ValueError(f"Instance không hợp lệ: {instance}")
    return int(tokens[0]), int(tokens[1])


def discover_instances(cli_instances: list[pathlib.Path]) -> list[pathlib.Path]:
    if cli_instances:
        return [resolve_path(p) for p in cli_instances]
    found: list[pathlib.Path] = []
    for d in DEFAULT_DATA_DIRS:
        if d.exists():
            found.extend(sorted(d.glob("*.txt")))
    # Loại bỏ các file không phải instance như LINKS.txt nếu có
    valid: list[pathlib.Path] = []
    for p in found:
        if p.name.upper() == "LINKS.TXT":
            continue
        valid.append(p)
    return valid


def build_command(
    algo: str,
    instance: pathlib.Path,
    n: int,
    solution: pathlib.Path,
    conv: pathlib.Path,
    seed: int,
    budget: float,
    args,
) -> tuple[list[str], str]:
    py = sys.executable
    src = ROOT / "src"
    if algo == "EXACT":
        cmd = [py, str(src / "main_A.py"), str(instance), "EXACT", str(solution), str(seed), str(budget)]
        params = f"budget_sec={budget}"
    elif algo == "SA":
        cmd = [py, str(src / "main_A.py"), str(instance), "SA", str(solution), str(seed), str(budget), str(conv)]
        params = f"T0=0.05*greedy;alpha=0.995;budget_sec={budget}"
    elif algo in ("GA", "GA_LS"):
        cmd = [
            py,
            str(src / "main_C.py"),
            str(instance),
            algo,
            str(solution),
            str(seed),
            str(budget),
            str(conv),
            str(args.population),
        ]
        mut = args.mutation_rate if args.mutation_rate is not None else 1.0 / n
        if args.mutation_rate is not None:
            cmd.append(str(args.mutation_rate))
        params = f"population={args.population};mutation_rate={mut:.6g};budget_sec={budget}"
    elif algo == "GREEDY":
        cmd = [py, str(src / "greedy.py"), str(instance), "GREEDY", str(solution), str(seed), str(budget), str(conv)]
        params = "chvatal+prune"
    elif algo in ("HC_FI", "HC_BI"):
        cmd = [py, str(src / "local_search.py"), str(instance), algo, str(solution), str(seed), str(budget), str(conv)]
        params = f"budget_sec={budget}"
    elif algo == "TS":
        cmd = [py, str(src / "tabu.py"), str(instance), "TS", str(solution), str(seed), str(budget), str(conv)]
        params = f"sample=40;budget_sec={budget}"
    elif algo == "GRASP":
        cmd = [py, str(src / "aco_or_grasp.py"), str(instance), "GRASP", str(solution), str(seed), str(budget), str(conv)]
        if args.grasp_alpha is not None:
            cmd.append(str(args.grasp_alpha))
            params = f"alpha={args.grasp_alpha};budget_sec={budget}"
        else:
            params = f"alpha=random(0.05,0.25);budget_sec={budget}"
    else:
        raise ValueError(f"Thuật toán không hỗ trợ: {algo}")
    return cmd, params


def read_conv_last(conv_path: pathlib.Path, fallback_time: float) -> tuple[float, int]:
    if not conv_path.exists():
        return fallback_time, 0
    with conv_path.open(newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    if not rows:
        return fallback_time, 0
    last = rows[-1]
    return float(last["time_s"]), int(last["evals"])


def verify_solution(instance: pathlib.Path, solution: pathlib.Path) -> tuple[bool, int]:
    checker = ROOT / "src" / "kiemtra.py"
    res = subprocess.run(
        [sys.executable, str(checker), str(instance), str(solution)],
        check=True,
        capture_output=True,
        text=True,
    )
    out = res.stdout.strip()
    if not out.startswith("HOP LE |"):
        return False, -1
    cost = int(solution.read_text(encoding="utf-8").split()[0])
    return True, cost


def main():
    args = parse_args()
    instances = discover_instances(args.instances)
    if not instances:
        raise SystemExit("Không tìm thấy file instance .txt nào.")

    output = resolve_path(args.output)
    sol_dir = output / "solutions"
    conv_dir = output / "conv"
    raw_dir = output / "raw"
    for d in (sol_dir, conv_dir, raw_dir):
        d.mkdir(parents=True, exist_ok=True)

    algos = [a.upper() for a in args.algorithms]
    if args.include_exact and "EXACT" not in algos:
        algos.insert(0, "EXACT")

    if not args.append:
        for algo in algos:
            rf = raw_dir / f"{algo}.csv"
            if rf.exists():
                rf.unlink()

    total_runs = 0
    t_all = time.perf_counter()

    for inst_path in instances:
        m, n = read_mn(inst_path)
        print(f"=== Instance: {inst_path.stem} (m={m}, n={n}) ===")
        for algo in algos:
            if algo == "EXACT":
                if n > args.exact_max_n:
                    print(f"  [EXACT] Bỏ qua (n={n} > {args.exact_max_n})")
                    continue
                seeds = [1]
                budget = args.exact_budget
            else:
                seeds = args.seeds
                budget = args.budget

            raw_file = raw_dir / f"{algo}.csv"
            write_header = not raw_file.exists()
            costs = []
            with raw_file.open("a", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                if write_header:
                    writer.writerow(RAW_HEADER)

                for run_idx, seed in enumerate(seeds, start=1):
                    stem = f"{inst_path.stem}_{algo}_s{seed}"
                    sol_path = sol_dir / f"{stem}.sol"
                    conv_path = conv_dir / f"{stem}_conv.csv"

                    cmd, params = build_command(algo, inst_path, n, sol_path, conv_path, seed, budget, args)
                    t0 = time.perf_counter()
                    subprocess.run(cmd, check=True, capture_output=True, text=True)
                    elapsed = time.perf_counter() - t0

                    feasible, cost = verify_solution(inst_path, sol_path)
                    if not feasible:
                        raise RuntimeError(f"Nghiệm không hợp lệ: {sol_path}")

                    t_best, evals = read_conv_last(conv_path, elapsed)
                    writer.writerow([
                        inst_path.stem,
                        n,
                        algo,
                        params,
                        seed,
                        run_idx,
                        cost,
                        f"{elapsed:.6f}",
                        f"{t_best:.6f}",
                        evals,
                        1 if feasible else 0,
                    ])
                    costs.append(cost)
                    total_runs += 1

            best_c = min(costs)
            mean_c = sum(costs) / len(costs)
            print(f"  [{algo:<6}] runs={len(costs):2d} | best={best_c:5d} | mean={mean_c:8.2f}")

    print(f"\nHoàn tất {total_runs} lần chạy trong {time.perf_counter() - t_all:.2f}s.")


if __name__ == "__main__":
    main()
