#!/usr/bin/env python3
"""Bộ sinh thể hiện Weighted Set Cover định dạng OR-Library (Member B).

Chi phí cột là số nguyên trong [cost_low, cost_high] (mặc định [1, 100]).
Mỗi hàng i phủ cột j với xác suất density; nếu một hàng không có cột nào phủ
thì chọn ngẫu nhiên 1 cột để bảo đảm mọi hàng đều khả thi.
"""

import argparse
import pathlib
import random
import sys


ROOT = pathlib.Path(__file__).resolve().parents[1]
DEFAULT_OUT_DIR = ROOT / "data" / "tusinh"

PRESETS = [
    ("nho_10x20_s101.txt", 10, 20, 0.30, 101),
    ("nho_15x25_s102.txt", 15, 25, 0.25, 102),
    ("nho_20x28_s103.txt", 20, 28, 0.20, 103),
    ("nho_25x30_s104.txt", 25, 30, 0.20, 104),
    ("vua_100x400_s201.txt", 100, 400, 0.05, 201),
    ("vua_150x600_s202.txt", 150, 600, 0.04, 202),
    ("vua_200x1000_s203.txt", 200, 1000, 0.03, 203),
]


def generate_scp_text(
    m: int,
    n: int,
    density: float,
    seed: int,
    cost_low: int = 1,
    cost_high: int = 100,
) -> str:
    rng = random.Random(seed)
    costs = [rng.randint(cost_low, cost_high) for _ in range(n)]
    rows: list[set[int]] = []
    seen_cols: set[int] = set()
    for _ in range(m):
        cols = [j + 1 for j in range(n) if rng.random() < density]
        if not cols:
            cols = [rng.randint(1, n)]
        seen_cols.update(cols)
        rows.append(set(cols))
    for j in range(1, n + 1):
        if j not in seen_cols:
            rows[rng.randrange(m)].add(j)

    lines = [f"{m} {n}", " ".join(map(str, costs))]
    for r in rows:
        sr = sorted(r)
        lines.append(str(len(sr)))
        lines.append(" ".join(map(str, sr)))
    return "\n".join(lines) + "\n"


def parse_args():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--presets", action="store_true", help="Sinh lại toàn bộ 7 thể hiện mặc định trong data/tusinh")
    parser.add_argument("-m", "--rows", type=int, help="Số hàng (nút giao)")
    parser.add_argument("-n", "--cols", type=int, help="Số cột (vị trí camera)")
    parser.add_argument("-d", "--density", type=float, default=0.05, help="Mật độ phủ mỗi phần tử")
    parser.add_argument("-s", "--seed", type=int, default=101, help="Seed sinh dữ liệu")
    parser.add_argument("--cost-low", type=int, default=1)
    parser.add_argument("--cost-high", type=int, default=100)
    parser.add_argument("-o", "--output", type=pathlib.Path, help="Đường dẫn tệp xuất")
    return parser.parse_args()


def main():
    args = parse_args()
    if args.presets:
        DEFAULT_OUT_DIR.mkdir(parents=True, exist_ok=True)
        for name, m, n, d, seed in PRESETS:
            out_path = DEFAULT_OUT_DIR / name
            out_path.write_text(generate_scp_text(m, n, d, seed, args.cost_low, args.cost_high), encoding="utf-8")
            print(f"Đã sinh: {out_path} (m={m}, n={n}, d={d}, seed={seed})")
        return

    if args.rows is None or args.cols is None or args.output is None:
        print("Cần truyền --presets hoặc đủ -m, -n, -o (xem --help)", file=sys.stderr)
        sys.exit(1)

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        generate_scp_text(args.rows, args.cols, args.density, args.seed, args.cost_low, args.cost_high),
        encoding="utf-8",
    )
    print(f"Đã sinh: {args.output} (m={args.rows}, n={args.cols}, d={args.density}, seed={args.seed})")


if __name__ == "__main__":
    main()
