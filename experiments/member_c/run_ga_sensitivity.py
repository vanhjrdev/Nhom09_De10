#!/usr/bin/env python3
"""Do nhieu tham so GA / GA_LS (thanh vien C).

Quet mot tham so lan luot:
- population trong {10, 20, 40, 80, 160}, mutation_rate = 1/n (mac dinh)
- mutation_rate trong {0.5/n, 1/n, 2/n, 5/n, 10/n}, population = 40 (mac dinh)

Chung ca GA va GA_LS, kiem tra nghiem bang kiemtra.py, luu ket qua ra
results/member_c/ga_sensitivity.csv va results/member_c/ga_sensitivity.md.
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
DEFAULT_OUTPUT = ROOT / "results" / "member_c"
SOLVER = ROOT / "src" / "main_C.py"
CHECKER = ROOT / "src" / "kiemtra.py"

POPULATIONS = [10, 20, 40, 80, 160]
MUTATION_RATES = [0.5, 1.0, 2.0, 5.0, 10.0]  # nhan voi 1/n
SEEDS = [1, 2, 3, 4, 5]
BUDGET = 1.0


def parse_args():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--instances",
        type=pathlib.Path,
        nargs="*",
        default=[],
        help="Danh sach file instance; mac dinh chon 4 bo dien tai",
    )
    parser.add_argument(
        "--budget",
        type=float,
        default=BUDGET,
        help="Ngân sách giây mỗi lần chạy",
    )
    parser.add_argument(
        "--seeds",
        type=int,
        nargs="+",
        default=SEEDS,
        help="Danh sách seed",
    )
    parser.add_argument(
        "--output",
        type=pathlib.Path,
        default=DEFAULT_OUTPUT,
        help="Thư mục đầu ra",
    )
    return parser.parse_args()


def resolve_path(path: pathlib.Path) -> pathlib.Path:
    return path if path.is_absolute() else ROOT / path


def read_n(instance: pathlib.Path) -> int:
    tokens = instance.read_text(encoding="utf-8").split(maxsplit=2)
    if len(tokens) < 2:
        raise ValueError(f"Instance không hợp lệ: {instance}")
    return int(tokens[1])


def run_once(instance, algorithm, seed, budget, conv_csv, population, mutation_rate):
    """Chạy một lần solver, trả về (cost, time_s, feasible)."""
    stem = f"{instance.stem}_{algorithm}_pop{population}_mr{mutation_rate:.4g}_s{seed}"
    sol_path = pathlib.Path(str(conv_csv).replace("_conv.csv", f"_{stem}.sol"))
    # Dùng conv_csv làm log hội tụ (ghi đè an toàn vì mỗi cấu hình có tên riêng)
    conv_path = pathlib.Path(conv_csv)

    cmd = [
        sys.executable,
        str(SOLVER),
        str(instance),
        algorithm,
        str(sol_path),
        str(seed),
        str(budget),
        str(conv_path),
        str(population),
    ]
    if mutation_rate is not None:
        cmd.append(str(mutation_rate))

    subprocess.run(cmd, check=True, capture_output=True, text=True)

    checked = subprocess.run(
        [sys.executable, str(CHECKER), str(instance), str(sol_path)],
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()
    feasible = checked.startswith("HOP LE |")
    if not feasible:
        raise RuntimeError(f"{stem}: {checked}")

    cost = int(sol_path.read_text(encoding="utf-8").split()[0])

    # Thời gian chạy lấy từ dòng stdout của solver: "[GA] Cost: X | Time: Ys"
    # (run_once gọi solver riêng nên ta cần đo lại hoặc parse stdout.)
    # Ở đây ta đếm từ conv file làm ước lượng thời gian tốt nhất.
    best_time = 0.0
    if conv_path.exists():
        with conv_path.open(newline="", encoding="utf-8") as f:
            rows = list(csv.DictReader(f))
        if rows:
            best_time = float(rows[-1]["time_s"])

    return cost, best_time, feasible, sol_path


def main():
    args = parse_args()

    instances = [resolve_path(p) for p in args.instances]
    if not instances:
        instances = [
            ROOT / "data" / "tusinh" / "nho_10x20_s101.txt",
            ROOT / "data" / "tusinh" / "nho_25x30_s104.txt",
            ROOT / "data" / "tusinh" / "vua_100x400_s201.txt",
            ROOT / "data" / "chuan" / "scp41.txt",
        ]

    output = resolve_path(args.output)
    output.mkdir(parents=True, exist_ok=True)

    csv_path = output / "ga_sensitivity.csv"
    md_path = output / "ga_sensitivity.md"

    header = [
        "instance", "n", "algorithm", "parameter", "value",
        "seed", "best_value", "time_s", "feasible",
    ]

    with csv_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(header)

    md_lines = [
        "# Do nhieu tham so GA / GA_LS (thanh vien C)",
        "",
        f"- Ngân sách: {args.budget} giây/lần chạy",
        f"- Seeds: {', '.join(map(str, args.seeds))}",
        f"- Thuật toán: GA và GA_LS",
        "",
        "## Thiết kế",
        "- Quét một tham số mỗi lần, giữ tham số kia ở giá trị mặc định.",
        "- Mặc định: population = 40, mutation_rate = 1/n.",
        "",
    ]

    total = 0
    for instance in instances:
        n = read_n(instance)
        default_mr = 1.0 / n
        print(f"\n=== Instance: {instance.name} (n={n}) ===")

        # --- Quét population (mutation_rate = 1/n) ---
        for pop in POPULATIONS:
            for seed in args.seeds:
                for algo in ("GA", "GA_LS"):
                    conv_csv = output / f"{instance.stem}_{algo}_pop{pop}_conv.csv"
                    cost, t_best, feasible, _ = run_once(
                        instance, algo, seed, args.budget, conv_csv, pop, default_mr
                    )
                    with csv_path.open("a", newline="", encoding="utf-8") as f:
                        writer = csv.writer(f)
                        writer.writerow([
                            instance.stem, n, algo, "population", pop,
                            seed, cost, f"{t_best:.6f}", 1 if feasible else 0,
                        ])
                    total += 1
                    print(
                        f"  [{algo}] pop={pop:3d} mr=1/n seed={seed} -> cost={cost}"
                    )

        # --- Quét mutation_rate (population = 40) ---
        for factor in MUTATION_RATES:
            mr = factor * default_mr
            for seed in args.seeds:
                for algo in ("GA", "GA_LS"):
                    conv_csv = output / f"{instance.stem}_{algo}_mr{factor:g}_conv.csv"
                    cost, t_best, feasible, _ = run_once(
                        instance, algo, seed, args.budget, conv_csv, 40, mr
                    )
                    with csv_path.open("a", newline="", encoding="utf-8") as f:
                        writer = csv.writer(f)
                        writer.writerow([
                            instance.stem, n, algo, "mutation_rate", f"{factor}x1/n",
                            seed, cost, f"{t_best:.6f}", 1 if feasible else 0,
                        ])
                    total += 1
                    print(
                        f"  [{algo}] pop=40 mr={factor:g}x1/n seed={seed} -> cost={cost}"
                    )

    # Tóm tắt theo markdown (theo instance + parameter: best/mean/std)
    import statistics

    md_lines.append("## Kết quả tóm tắt (theo instance / tham số / thuật toán)")
    md_lines.append("")
    md_lines.append(
        "| Instance | Thuật toán | Tham số | Giá trị | Best | Mean ± Std | Feasible |"
    )
    md_lines.append(
        "|---|---|---|---|---|---|---|"
    )

    # Đọc lại csv để nhóm tóm tắt
    rows = []
    with csv_path.open(newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            rows.append(row)

    groups = {}
    for row in rows:
        key = (row["instance"], row["algorithm"], row["parameter"], row["value"])
        groups.setdefault(key, []).append(int(row["best_value"]))

    for key in sorted(groups):
        costs = groups[key]
        inst, algo, param, val = key
        best = min(costs)
        mean = sum(costs) / len(costs)
        std = statistics.pstdev(costs) if len(costs) > 1 else 0.0
        feas = all(int(r["feasible"]) == 1 for r in rows
                   if (r["instance"], r["algorithm"], r["parameter"], r["value"]) == key)
        md_lines.append(
            f"| {inst} | {algo} | {param} | {val} | {best} | {mean:.2f} ± {std:.2f} | {'100%' if feas else '<100%'} |"
        )

    md_lines.append("")
    md_lines.append(f"Tổng số lần chạy: {total}")
    md_lines.append(f"File chi tiết: {csv_path.name}")

    with md_path.open("w", encoding="utf-8") as f:
        f.write("\n".join(md_lines) + "\n")

    print(f"\nHoàn tất {total} lần chạy.")
    print(f"CSV chi tiết: {csv_path}")
    print(f"Tom tat: {md_path}")


if __name__ == "__main__":
    main()
