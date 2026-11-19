#!/usr/bin/env python3
"""Chạy thử ví dụ của đề; không thay thế thực nghiệm trên nhiều bộ dữ liệu."""
import csv
import pathlib
import subprocess
import sys
import time

root = pathlib.Path(__file__).resolve().parents[2]
out = root / 'results/member_c'
out.mkdir(parents=True, exist_ok=True)
solver = root / 'src/main_C.py'
checker = root / 'src/kiemtra.py'
rows = []
for algo in ('GA', 'GA_LS'):
    for seed in range(1, 11):
        stem = f'vidu_{algo}_s{seed}'
        sol, log = out / (stem + '.sol'), out / (stem + '_conv.csv')
        start = time.perf_counter()
        subprocess.run([sys.executable, str(solver), str(root / 'data/vidu/vidu.txt'), algo, str(sol), str(seed), '0.1', str(log)], check=True, capture_output=True, text=True)
        elapsed = time.perf_counter() - start
        check = subprocess.run([sys.executable, str(checker), str(root / 'data/vidu/vidu.txt'), str(sol)], check=True, capture_output=True, text=True).stdout.strip()
        if not check.startswith('HOP LE |'):
            raise RuntimeError(f'{stem}: {check}')
        cost = int(sol.read_text().split()[0])
        rows.append([algo, seed, 0.1, cost, elapsed, check])
with (out / 'summary.csv').open('w', newline='') as file:
    writer = csv.writer(file)
    writer.writerow(['algorithm', 'seed', 'budget_s', 'cost', 'elapsed_s', 'check'])
    writer.writerows(rows)
print('Đã kiểm tra', len(rows), 'lời giải; kết quả:', out / 'summary.csv')
