#!/usr/bin/env python3
"""Kiểm định thống kê phi tham số (Friedman & Wilcoxon signed-rank) từ results/raw/*.csv."""

import argparse
import csv
import math
import pathlib
import sys
from collections import defaultdict


def _mean(vals: list[float]) -> float:
    return sum(vals) / len(vals)


for stream in (sys.stdout, sys.stderr):
    if hasattr(stream, "reconfigure"):
        stream.reconfigure(encoding="utf-8")


ROOT = pathlib.Path(__file__).resolve().parents[1]
DEFAULT_RAW = ROOT / "results" / "raw"
DEFAULT_OUT = ROOT / "results"

META_ORDER = ["GREEDY", "HC_FI", "HC_BI", "TS", "SA", "GA", "GA_LS", "GRASP"]


def parse_args():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--raw-dir", type=pathlib.Path, default=DEFAULT_RAW)
    parser.add_argument("--output-dir", type=pathlib.Path, default=DEFAULT_OUT)
    parser.add_argument(
        "--algorithms",
        nargs="+",
        default=None,
        help="Danh sách thuật toán đưa vào kiểm định (mặc định: tất cả trừ EXACT)",
    )
    return parser.parse_args()


def resolve_path(p: pathlib.Path) -> pathlib.Path:
    return p if p.is_absolute() else ROOT / p


def _gamma_inc_upper_q(a: float, x: float) -> float:
    """Regularized upper incomplete gamma Q(a, x) = Gamma(a, x) / Gamma(a)."""
    if x <= 0:
        return 1.0
    if x < a + 1.0:
        # Series representation for P(a, x), then Q = 1 - P
        ap = a
        term = 1.0 / a
        total = term
        for _ in range(1, 500):
            ap += 1.0
            term *= x / ap
            total += term
            if abs(term) < abs(total) * 1e-12:
                break
        p = total * math.exp(-x + a * math.log(x) - math.lgamma(a))
        return max(0.0, min(1.0, 1.0 - p))
    # Continued fraction (Lentz's method) for Q(a, x)
    tiny = 1e-30
    b = x + 1.0 - a
    c = 1.0 / tiny
    d = 1.0 / b
    h = d
    for i in range(1, 500):
        an = -i * (i - a)
        b += 2.0
        d = an * d + b
        if abs(d) < tiny:
            d = tiny
        c = b + an / c
        if abs(c) < tiny:
            c = tiny
        d = 1.0 / d
        delta = d * c
        h *= delta
        if abs(delta - 1.0) < 1e-12:
            break
    q = math.exp(-x + a * math.log(x) - math.lgamma(a)) * h
    return max(0.0, min(1.0, q))


def chi2_sf(x: float, df: int) -> float:
    return _gamma_inc_upper_q(df / 2.0, x / 2.0)


def assign_ranks(values: list[float]) -> tuple[list[float], float]:
    """Gán hạng trung bình (average ranks) cho danh sách giá trị và trả về tie_sum = sum(t^3 - t)."""
    indexed = sorted(enumerate(values), key=lambda x: x[1])
    ranks = [0.0] * len(values)
    tie_sum = 0.0
    i = 0
    while i < len(indexed):
        j = i
        while j + 1 < len(indexed) and indexed[j + 1][1] == indexed[i][1]:
            j += 1
        avg_rank = (i + 1 + j + 1) / 2.0
        for k in range(i, j + 1):
            ranks[indexed[k][0]] = avg_rank
        t = j - i + 1
        if t > 1:
            tie_sum += t * t * t - t
        i = j + 1
    return ranks, tie_sum


def friedman_test(matrix: list[list[float]]) -> dict:
    """Kiểm định Friedman với N blocks (hàng) và k treatments (cột)."""
    N = len(matrix)
    k = len(matrix[0])
    rank_sums = [0.0] * k
    total_tie_sum = 0.0
    for row in matrix:
        ranks, tie_sum = assign_ranks(row)
        total_tie_sum += tie_sum
        for j in range(k):
            rank_sums[j] += ranks[j]

    mean_ranks = [rs / N for rs in rank_sums]
    ss_r = sum(rs * rs for rs in rank_sums)
    denom = N * k * (k + 1) - (total_tie_sum / (k - 1)) if k > 1 else 1.0
    chi2 = (12.0 * ss_r - 3.0 * N * N * k * (k + 1) * (k + 1)) / denom if denom > 0 else 0.0
    p_val = chi2_sf(chi2, k - 1) if k > 1 else 1.0
    return {
        "N": N,
        "k": k,
        "chi2": chi2,
        "df": k - 1,
        "p_value": p_val,
        "mean_ranks": mean_ranks,
    }


def wilcoxon_signed_rank(x: list[float], y: list[float]) -> dict:
    """Kiểm định Wilcoxon signed-rank hai phía (ghép cặp x - y, loại bỏ hiệu = 0)."""
    diffs = [xi - yi for xi, yi in zip(x, y) if xi != yi]
    n = len(diffs)
    if n == 0:
        return {"n": 0, "w_plus": 0.0, "w_minus": 0.0, "z": 0.0, "p_value": 1.0}

    abs_diffs = [abs(d) for d in diffs]
    ranks, tie_sum = assign_ranks(abs_diffs)
    w_plus = sum(r for d, r in zip(diffs, ranks) if d > 0)
    w_minus = sum(r for d, r in zip(diffs, ranks) if d < 0)
    w = min(w_plus, w_minus)

    mean_w = n * (n + 1) / 4.0
    var_w = (n * (n + 1) * (2 * n + 1) - tie_sum / 2.0) / 24.0
    if var_w <= 0:
        return {"n": n, "w_plus": w_plus, "w_minus": w_minus, "z": 0.0, "p_value": 1.0}

    sd_w = math.sqrt(var_w)
    z = (w_plus - mean_w) / sd_w
    p_val = math.erfc(abs(z) / math.sqrt(2.0))
    return {"n": n, "w_plus": w_plus, "w_minus": w_minus, "z": z, "p_value": min(1.0, p_val)}


def holm_adjust(p_values: list[float]) -> list[float]:
    m = len(p_values)
    indexed = sorted(enumerate(p_values), key=lambda item: item[1])
    adjusted = [0.0] * m
    running_max = 0.0
    for rank, (orig_idx, p) in enumerate(indexed):
        val = min(1.0, p * (m - rank))
        running_max = max(running_max, val)
        adjusted[orig_idx] = running_max
    return adjusted


def main():
    args = parse_args()
    raw_dir = resolve_path(args.raw_dir)
    out_dir = resolve_path(args.output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    # Đọc dữ liệu thô
    data: dict[tuple[str, str, int], float] = {}
    by_inst_algo: dict[tuple[str, str], list[float]] = defaultdict(list)
    instances_set: set[str] = set()
    algos_set: set[str] = set()

    for csv_file in sorted(raw_dir.glob("*.csv")):
        with csv_file.open(newline="", encoding="utf-8") as f:
            for r in csv.DictReader(f):
                algo = r["algorithm"]
                if algo == "EXACT":
                    continue
                if int(r["feasible"]) != 1:
                    continue
                inst = r["instance"]
                seed = int(r["seed"])
                val = float(r["best_value"])
                data[(inst, algo, seed)] = val
                by_inst_algo[(inst, algo)].append(val)
                instances_set.add(inst)
                algos_set.add(algo)

    if args.algorithms:
        algos = [a.upper() for a in args.algorithms if a.upper() in algos_set]
    else:
        algos = sorted(algos_set, key=lambda a: (META_ORDER.index(a) if a in META_ORDER else 999, a))

    instances = sorted(instances_set)
    # Chỉ giữ các instance có đủ tất cả thuật toán cho Friedman
    full_instances = [inst for inst in instances if all((inst, a) in by_inst_algo for a in algos)]
    if len(full_instances) < 2 or len(algos) < 2:
        raise SystemExit("Không đủ dữ liệu (cần ít nhất 2 instance và 2 thuật toán).")

    matrix = [[_mean(by_inst_algo[(inst, a)]) for a in algos] for inst in full_instances]
    friedman = friedman_test(matrix)

    # Pairwise Wilcoxon trên từng cặp (instance, seed)
    pair_rows: list[dict] = []
    for i in range(len(algos)):
        for j in range(i + 1, len(algos)):
            a1, a2 = algos[i], algos[j]
            keys = sorted({(inst, s) for (inst, al, s) in data if al == a1 and (inst, a2, s) in data})
            if not keys:
                continue
            x = [data[(inst, a1, s)] for inst, s in keys]
            y = [data[(inst, a2, s)] for inst, s in keys]
            res = wilcoxon_signed_rank(x, y)
            pair_rows.append(
                {
                    "algo_1": a1,
                    "algo_2": a2,
                    "pairs_n": res["n"],
                    "mean_1": _mean(x),
                    "mean_2": _mean(y),
                    "w_plus": res["w_plus"],
                    "w_minus": res["w_minus"],
                    "z": res["z"],
                    "p_value": res["p_value"],
                }
            )

    if pair_rows:
        adj = holm_adjust([r["p_value"] for r in pair_rows])
        for r, p_adj in zip(pair_rows, adj):
            r["p_holm"] = p_adj
            r["significant_0_05"] = "Yes" if p_adj < 0.05 else "No"

    # Xuất CSV
    csv_out = out_dir / "statistics.csv"
    with csv_out.open("w", newline="", encoding="utf-8") as f:
        fieldnames = [
            "algo_1",
            "algo_2",
            "pairs_n",
            "mean_1",
            "mean_2",
            "w_plus",
            "w_minus",
            "z",
            "p_value",
            "p_holm",
            "significant_0_05",
        ]
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for r in pair_rows:
            writer.writerow(
                {
                    **r,
                    "mean_1": f"{r['mean_1']:.4f}",
                    "mean_2": f"{r['mean_2']:.4f}",
                    "w_plus": f"{r['w_plus']:.1f}",
                    "w_minus": f"{r['w_minus']:.1f}",
                    "z": f"{r['z']:.4f}",
                    "p_value": f"{r['p_value']:.6g}",
                    "p_holm": f"{r['p_holm']:.6g}",
                }
            )

    # Xuất Markdown
    md_lines = [
        "# Kiểm định thống kê (Friedman & Wilcoxon signed-rank)",
        "",
        "## 1. Kiểm định Friedman (trên giá trị trung bình từng instance)",
        f"- Số thể hiện (blocks): **{friedman['N']}**",
        f"- Số thuật toán: **{friedman['k']}** ({', '.join(algos)})",
        f"- Thống kê $\\chi^2_F = {friedman['chi2']:.4f}$ (df = {friedman['df']}), $p$-value = **{friedman['p_value']:.6g}**",
        f"- Kết luận ($\\alpha = 0.05$): **{'Có khác biệt có ý nghĩa thống kê giữa các thuật toán' if friedman['p_value'] < 0.05 else 'Chưa đủ cơ sở bác bỏ H0'}**.",
        "",
        "### Hạng trung bình Friedman (nhỏ hơn là tốt hơn)",
        "| Thuật toán | Hạng trung bình |",
        "|---|---:|",
    ]
    for a, mr in sorted(zip(algos, friedman["mean_ranks"]), key=lambda x: x[1]):
        md_lines.append(f"| {a} | {mr:.3f} |")

    md_lines.extend(
        [
            "",
            "## 2. Kiểm định Wilcoxon signed-rank từng cặp (ghép cặp theo instance & seed)",
            "",
            "| Cặp so sánh | n (khác 0) | Mean 1 | Mean 2 | W+ | W- | z | p-value | p-Holm | Ý nghĩa (0.05) |",
            "|---|---:|---:|---:|---:|---:|---:|---:|---:|---|",
        ]
    )
    for r in pair_rows:
        md_lines.append(
            f"| {r['algo_1']} vs {r['algo_2']} | {r['pairs_n']} | {r['mean_1']:.2f} | {r['mean_2']:.2f} "
            f"| {r['w_plus']:.1f} | {r['w_minus']:.1f} | {r['z']:.3f} | {r['p_value']:.4g} | {r['p_holm']:.4g} | {r['significant_0_05']} |"
        )

    md_out = out_dir / "statistics.md"
    md_out.write_text("\n".join(md_lines) + "\n", encoding="utf-8")
    print(f"Đã ghi: {csv_out}")
    print(f"Đã ghi: {md_out}")


if __name__ == "__main__":
    main()
