import sys
import time
import math
import random
from scp_core import SCPInstance, save_solution

class ExactSolver:
    def __init__(self, inst: SCPInstance, time_limit_sec: float = 600.0):
        self.inst = inst
        self.time_limit_sec = time_limit_sec
        self.best_cost = float('inf')
        self.best_cols = []
        self.dominated = [False] * (inst.n + 1)
        self.forced_cols = []
        self.start_time = 0.0
        self.timeout = False

    def preprocess(self, cov_cnt: list[int]) -> int:
        for j1 in range(1, self.inst.n + 1):
            if self.dominated[j1]:
                continue
            if not self.inst.col_rows[j1]:
                self.dominated[j1] = True
                continue
            for j2 in range(1, self.inst.n + 1):
                if j1 == j2 or self.dominated[j2]:
                    continue
                if (self.inst.cost[j2] <= self.inst.cost[j1] and
                        len(self.inst.col_rows[j2]) >= len(self.inst.col_rows[j1]) and
                        self.inst.col_rows[j1].issubset(self.inst.col_rows[j2])):
                    self.dominated[j1] = True
                    break

        base_cost = 0
        changed = True
        while changed:
            changed = False
            for i in range(1, self.inst.m + 1):
                if cov_cnt[i] == 0:
                    valid_cols = [c for c in self.inst.row_cols[i] if not self.dominated[c]]
                    if len(valid_cols) == 1:
                        c = valid_cols[0]
                        self.forced_cols.append(c)
                        self.dominated[c] = True  # Da chon nen khong xet lai trong DFS
                        base_cost += self.inst.cost[c]
                        for r in self.inst.col_rows[c]:
                            cov_cnt[r] += 1
                        changed = True
        return base_cost

    def lower_bound(self, cov_cnt: list[int]) -> int:
        lb = 0.0
        for i in range(1, self.inst.m + 1):
            if cov_cnt[i] == 0:
                min_unit = float('inf')
                for c in self.inst.row_cols[i]:
                    if not self.dominated[c]:
                        unit = self.inst.cost[c] / len(self.inst.col_rows[c])
                        if unit < min_unit:
                            min_unit = unit
                if min_unit == float('inf'):
                    return 10**18
                lb += min_unit
        return math.ceil(lb - 1e-9)

    def dfs(self, cur_cost: int, covered_rows: int, cov_cnt: list[int], cur_cols: list[int]):
        if self.timeout:
            return
        if time.perf_counter() - self.start_time > self.time_limit_sec:
            self.timeout = True
            return

        if cur_cost >= self.best_cost:
            return

        if covered_rows == self.inst.m:
            self.best_cost = cur_cost
            self.best_cols = list(cur_cols)
            return

        if cur_cost + self.lower_bound(cov_cnt) >= self.best_cost:
            return

        # MRV: Chon hang chua phu co it lua chon nhat
        target_row = -1
        min_options = 10**9
        for i in range(1, self.inst.m + 1):
            if cov_cnt[i] == 0:
                opts = sum(1 for c in self.inst.row_cols[i] if not self.dominated[c])
                if opts == 0:
                    return
                if opts < min_options:
                    min_options = opts
                    target_row = i

        candidates = [c for c in self.inst.row_cols[target_row] if not self.dominated[c]]
        candidates.sort(key=lambda c: self.inst.cost[c])

        for c in candidates:
            if cur_cost + self.inst.cost[c] >= self.best_cost:
                continue

            newly_covered = 0
            for r in self.inst.col_rows[c]:
                if cov_cnt[r] == 0:
                    newly_covered += 1
                cov_cnt[r] += 1
            cur_cols.append(c)

            self.dfs(cur_cost + self.inst.cost[c], covered_rows + newly_covered, cov_cnt, cur_cols)

            cur_cols.pop()
            for r in self.inst.col_rows[c]:
                cov_cnt[r] -= 1

    def solve(self):
        self.start_time = time.perf_counter()
        cov_cnt = [0] * (self.inst.m + 1)
        base_cost = self.preprocess(cov_cnt)
        initial_covered = sum(1 for i in range(1, self.inst.m + 1) if cov_cnt[i] > 0)
        self.dfs(base_cost, initial_covered, cov_cnt, list(self.forced_cols))
        return int(self.best_cost), self.best_cols

class SASolver:
    def __init__(self, inst: SCPInstance, seed: int = 42):
        self.inst = inst
        self.rng = random.Random(seed)

    def build_initial(self):
        in_sol = [False] * (self.inst.n + 1)
        cov_cnt = [0] * (self.inst.m + 1)
        total_cost = 0
        uncovered = self.inst.m

        while uncovered > 0:
            best_c = -1
            best_ratio = float('inf')
            for j in range(1, self.inst.n + 1):
                if in_sol[j]:
                    continue
                new_cov = sum(1 for r in self.inst.col_rows[j] if cov_cnt[r] == 0)
                if new_cov > 0:
                    ratio = self.inst.cost[j] / new_cov
                    if ratio < best_ratio:
                        best_ratio = ratio
                        best_c = j
            in_sol[best_c] = True
            total_cost += self.inst.cost[best_c]
            for r in self.inst.col_rows[best_c]:
                if cov_cnt[r] == 0:
                    uncovered -= 1
                cov_cnt[r] += 1

        total_cost = self.remove_redundant(in_sol, cov_cnt, total_cost)
        return in_sol, cov_cnt, total_cost

    def remove_redundant(self, in_sol: list[bool], cov_cnt: list[int], total_cost: int) -> int:
        chosen = [j for j in range(1, self.inst.n + 1) if in_sol[j]]
        chosen.sort(key=lambda c: self.inst.cost[c], reverse=True)

        for c in chosen:
            if all(cov_cnt[r] >= 2 for r in self.inst.col_rows[c]):
                in_sol[c] = False
                total_cost -= self.inst.cost[c]
                for r in self.inst.col_rows[c]:
                    cov_cnt[r] -= 1
        return total_cost

    def repair(self, in_sol: list[bool], cov_cnt: list[int], total_cost: int) -> int:
        for i in range(1, self.inst.m + 1):
            if cov_cnt[i] == 0:
                best_c = -1
                best_score = float('inf')
                for c in self.inst.row_cols[i]:
                    gain = sum(1 for r in self.inst.col_rows[c] if cov_cnt[r] == 0)
                    score = self.inst.cost[c] / max(1, gain)
                    if score < best_score:
                        best_score = score
                        best_c = c
                in_sol[best_c] = True
                total_cost += self.inst.cost[best_c]
                for r in self.inst.col_rows[best_c]:
                    cov_cnt[r] += 1
        return total_cost

    def solve(self, budget_sec: float, conv_csv_file: str):
        t0 = time.perf_counter()
        cur_sol, cur_cov, cur_cost = self.build_initial()
        best_sol = list(cur_sol)
        best_cost = cur_cost

        T = max(1.0, best_cost * 0.05)
        alpha = 0.995
        steps_per_temp = max(20, self.inst.n // 5)

        iter_cnt = 0
        evals = 1

        with open(conv_csv_file, 'w', encoding='utf-8') as fconv:
            fconv.write("time_s,iter,evals,best\n")
            fconv.write(f"0.0000,0,1,{best_cost}\n")

            while True:
                if time.perf_counter() - t0 >= budget_sec:
                    break

                for _ in range(steps_per_temp):
                    iter_cnt += 1
                    next_sol = list(cur_sol)
                    next_cov = list(cur_cov)
                    next_cost = cur_cost

                    flip_cnt = 1 if self.rng.random() < 0.7 else 2
                    for _ in range(flip_cnt):
                        c = self.rng.randint(1, self.inst.n)
                        if next_sol[c]:
                            next_sol[c] = False
                            next_cost -= self.inst.cost[c]
                            for r in self.inst.col_rows[c]:
                                next_cov[r] -= 1
                        else:
                            next_sol[c] = True
                            next_cost += self.inst.cost[c]
                            for r in self.inst.col_rows[c]:
                                next_cov[r] += 1

                    next_cost = self.repair(next_sol, next_cov, next_cost)
                    next_cost = self.remove_redundant(next_sol, next_cov, next_cost)
                    evals += 1

                    delta = next_cost - cur_cost
                    if delta <= 0 or self.rng.random() < math.exp(-delta / T):
                        cur_sol = next_sol
                        cur_cov = next_cov
                        cur_cost = next_cost

                        if cur_cost < best_cost:
                            best_cost = cur_cost
                            best_sol = list(cur_sol)
                            now_s = time.perf_counter() - t0
                            fconv.write(f"{now_s:.4f},{iter_cnt},{evals},{best_cost}\n")

                T = max(0.01, T * alpha)

        res_cols = [j for j in range(1, self.inst.n + 1) if best_sol[j]]
        return best_cost, res_cols


def main():
    if len(sys.argv) < 4:
        print("Cach dung: python main_A.py <input_file> <EXACT|SA> <output_sol> [seed] [budget_sec] [conv_csv]")
        sys.exit(1)

    in_file = sys.argv[1]
    algo = sys.argv[2].upper()
    out_file = sys.argv[3]
    seed = int(sys.argv[4]) if len(sys.argv) >= 5 else 42
    budget = float(sys.argv[5]) if len(sys.argv) >= 6 else 10.0
    conv_file = sys.argv[6] if len(sys.argv) >= 7 else "conv.csv"

    inst = SCPInstance()
    if not inst.load_from_file(in_file):
        print(f"Loi doc file: {in_file}")
        sys.exit(1)

    t_start = time.perf_counter()
    if algo == "EXACT":
        solver = ExactSolver(inst, budget)
        cost, cols = solver.solve()
        elapsed = time.perf_counter() - t_start
        save_solution(out_file, cost, cols)
        status = " (TIMEOUT)" if solver.timeout else ""
        print(f"[EXACT] Cost: {cost} | Time: {elapsed:.4f}s{status}")
    elif algo == "SA":
        solver = SASolver(inst, seed)
        cost, cols = solver.solve(budget, conv_file)
        elapsed = time.perf_counter() - t_start
        save_solution(out_file, cost, cols)
        print(f"[SA] Cost: {cost} | Time: {elapsed:.4f}s")


if __name__ == "__main__":
    main()