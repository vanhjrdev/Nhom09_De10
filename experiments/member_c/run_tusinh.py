#!/usr/bin/env python3
"""Chạy GA và GA_LS trên dữ liệu tự sinh để kiểm tra phần thành viên C.

Đây là runner riêng của thành viên C. Script thực nghiệm chung, biểu đồ và kiểm định
thống kê vẫn thuộc phần của thành viên D.
"""

import argparse
import csv
import pathlib
import re
import subprocess
import sys


for stream in (sys.stdout, sys.stderr):
    if hasattr(stream, "reconfigure"):
        stream.reconfigure(encoding="utf-8")


ROOT = pathlib.Path(__file__).resolve().parents[2]
DEFAULT_DATA = ROOT / "data" / "tusinh"
DEFAULT_OUTPUT = ROOT / "results"


def parse_args():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--budget", type=float, default=1.0, help="Ngân sách giây mỗi lần chạy")
    parser.add_argument("--seeds", type=int, nargs="+", default=list(range(1, 11)))
    parser.add_argument("--population", type=int, default=40)
    parser.add_argument("--mutation-rate", type=float)
    parser.add_argument("--output", type=pathlib.Path, default=DEFAULT_OUTPUT)
    parser.add_argument(
        "instances",
        type=pathlib.Path,
        nargs="*",
        help="Danh sách instance; mặc định chạy mọi file .txt trong data/tusinh",
    )
    return parser.parse_args()


def resolve_path(path: pathlib.Path) -> pathlib.Path:
    return path if path.is_absolute() else ROOT / path


def read_n(instance: pathlib.Path) -> int:
    tokens = instance.read_text(encoding="utf-8").split(maxsplit=2)
    if len(tokens) < 2:
        raise ValueError(f"Instance không hợp lệ: {instance}")
    return int(tokens[1])


def main():
    args = parse_args()
    if args.budget <= 0 or args.population < 2:
        raise SystemExit("budget phải dương và population phải từ 2 trở lên")
    if args.mutation_rate is not None and not 0 <= args.mutation_rate <= 1:
        raise SystemExit("mutation-rate phải thuộc [0, 1]")

    instances = [resolve_path(path) for path in args.instances]
    if not instances:
        instances = sorted(DEFAULT_DATA.glob("*.txt"))
    if not instances:
        raise SystemExit("Không tìm thấy instance .txt")

    output = resolve_path(args.output)
    solutions = output / "solutions"
    convergence = output / "conv"
    raw_dir = output / "raw"
    solutions.mkdir(parents=True, exist_ok=True)
    convergence.mkdir(parents=True, exist_ok=True)
    raw_dir.mkdir(parents=True, exist_ok=True)

    solver = ROOT / "src" / "main_C.py"
    checker = ROOT / "src" / "kiemtra.py"

    for instance in instances:
        n = read_n(instance)
        for algorithm in ("GA", "GA_LS"):
            for seed in args.seeds:
                stem = f"{instance.stem}_{algorithm}_s{seed}"
                solution = solutions / f"{stem}.sol"
                conv = convergence / f"{stem}_conv.csv"
                command = [
                    sys.executable,
                    str(solver),
                    str(instance),
                    algorithm,
                    str(solution),
                    str(seed),
                    str(args.budget),
                    str(conv),
                    str(args.population),
                ]
                if args.mutation_rate is not None:
                    command.append(str(args.mutation_rate))

                completed = subprocess.run(command, check=True, capture_output=True, text=True)
                elapsed_match = re.search(r"\| Time: ([0-9.]+)s", completed.stdout)
                if elapsed_match is None:
                    raise RuntimeError(f"Không đọc được thời gian chạy: {completed.stdout.strip()}")
                elapsed = float(elapsed_match.group(1))
                checked = subprocess.run(
                    [sys.executable, str(checker), str(instance), str(solution)],
                    check=True,
                    capture_output=True,
                    text=True,
                ).stdout.strip()
                feasible = checked.startswith("HOP LE |")
                if not feasible:
                    raise RuntimeError(f"{stem}: {checked}")

                cost = int(solution.read_text(encoding="utf-8").split()[0])
                with conv.open(newline="", encoding="utf-8") as file:
                    history = list(csv.DictReader(file))
                if not history:
                    raise RuntimeError(f"Log hội tụ rỗng: {conv}")
                last = history[-1]
                mutation = args.mutation_rate if args.mutation_rate is not None else 1 / n
                params = f"population={args.population};mutation_rate={mutation:.12g};budget_sec={args.budget}"
                row = [
                    instance.stem,
                    n,
                    algorithm,
                    params,
                    seed,
                    seed,
                    cost,
                    f"{elapsed:.6f}",
                    last["time_s"],
                    last["evals"],
                    1,
                ]
                raw_file = raw_dir / f"{algorithm}.csv"
                write_header = not raw_file.exists()
                with raw_file.open("a", newline="", encoding="utf-8") as file:
                    writer = csv.writer(file)
                    if write_header:
                        writer.writerow(
                            [
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
                        )
                    writer.writerow(row)
                print(f"{stem}: cost={cost}, feasible=1")

    print("Đã kiểm tra các lần chạy; kết quả:")
    for algorithm in ("GA", "GA_LS"):
        print(f"  {algorithm}: {raw_dir / f'{algorithm}.csv'}")


if __name__ == "__main__":
    main()
