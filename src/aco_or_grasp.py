import math
import random
import sys
import time
from pathlib import Path

from scp_core import SCPInstance, save_solution


class GRASPSolver:
    """Greedy Randomized Adaptive Search Procedure (GRASP) for Weighted Set Cover."""

    def __init__(self, instance: SCPInstance, seed: int = 42, alpha: float | None = None):
        self.inst = instance
        self.rng = random.Random(seed)
        self.alpha = alpha
        self.evaluations = 0

    def _prune(self, chosen: list[bool], cover: list[int], cost: int) -> int:
        selected = [j for j in range(1, self.inst.n + 1) if chosen[j]]
        self.rng.shuffle(selected)
        selected.sort(key=lambda j: self.inst.cost[j], reverse=True)
        for j in selected:
            if all(cover[r] >= 2 for r in self.inst.col_rows[j]):
                chosen[j] = False
                cost -= self.inst.cost[j]
                for r in self.inst.col_rows[j]:
                    cover[r] -= 1
        return cost

    def _construct(self, alpha: float) -> tuple[list[bool], list[int], int]:
        n, m = self.inst.n, self.inst.m
        chosen = [False] * (n + 1)
        cover = [0] * (m + 1)
        gain = [len(self.inst.col_rows[j]) for j in range(n + 1)]
        active = [j for j in range(1, n + 1) if gain[j] > 0]
        uncovered = m
        cost = 0

        while uncovered > 0:
            scores: list[tuple[float, int]] = []
            next_active: list[int] = []
            min_s = math.inf
            max_s = -math.inf

            for j in active:
                if chosen[j]:
                    continue
                g = gain[j]
                if g > 0:
                    next_active.append(j)
                    s = self.inst.cost[j] / g
                    scores.append((s, j))
                    if s < min_s:
                        min_s = s
                    if s > max_s:
                        max_s = s

            active = next_active
            if not scores:
                raise ValueError("Instance khong kha thi: co hang khong duoc phu")

            if alpha <= 0.0:
                rcl = [j for s, j in scores if s <= min_s + 1e-12]
            else:
                limit = min_s + alpha * (max_s - min_s) + 1e-12
                rcl = [j for s, j in scores if s <= limit]
            pick = self.rng.choice(rcl)

            chosen[pick] = True
            cost += self.inst.cost[pick]
            for r in self.inst.col_rows[pick]:
                if cover[r] == 0:
                    uncovered -= 1
                    for col in self.inst.row_cols[r]:
                        gain[col] -= 1
                cover[r] += 1

        cost = self._prune(chosen, cover, cost)
        self.evaluations += 1
        return chosen, cover, cost

    def _local_search(
        self, chosen: list[bool], cover: list[int], cost: int, deadline: float
    ) -> tuple[list[bool], list[int], int]:
        improved = True
        while improved and time.perf_counter() < deadline:
            improved = False
            selected = [j for j in range(1, self.inst.n + 1) if chosen[j]]
            self.rng.shuffle(selected)

            # Phase 1: 1-to-1 swap for columns with unique covered rows
            for j in selected:
                if time.perf_counter() >= deadline:
                    break
                if not chosen[j]:
                    continue
                only = [r for r in self.inst.col_rows[j] if cover[r] == 1]
                if not only:
                    continue
                need = set(only)
                best_k = -1
                best_ck = self.inst.cost[j]
                for k in self.inst.row_cols[only[0]]:
                    if chosen[k] or k == j:
                        continue
                    self.evaluations += 1
                    if self.inst.cost[k] < best_ck and need.issubset(self.inst.col_rows[k]):
                        best_k = k
                        best_ck = self.inst.cost[k]
                if best_k != -1:
                    chosen[j] = False
                    cost -= self.inst.cost[j]
                    for r in self.inst.col_rows[j]:
                        cover[r] -= 1
                    chosen[best_k] = True
                    cost += self.inst.cost[best_k]
                    for r in self.inst.col_rows[best_k]:
                        cover[r] += 1
                    cost = self._prune(chosen, cover, cost)
                    improved = True
                    break

            if improved:
                continue

            # Phase 2: destroy-1 + greedy repair (prioritize higher-cost columns)
            candidates = sorted(
                (j for j in selected if chosen[j]),
                key=lambda j: self.inst.cost[j],
                reverse=True,
            )
            if len(candidates) > 30:
                candidates = candidates[:30]

            for j in candidates:
                if time.perf_counter() >= deadline:
                    break
                saved_chosen = list(chosen)
                saved_cover = list(cover)
                saved_cost = cost

                chosen[j] = False
                cost -= self.inst.cost[j]
                uncovered_rows = []
                for r in self.inst.col_rows[j]:
                    cover[r] -= 1
                    if cover[r] == 0:
                        uncovered_rows.append(r)

                while uncovered_rows:
                    r0 = uncovered_rows[0]
                    if cover[r0] > 0:
                        uncovered_rows.pop(0)
                        continue
                    best_col = -1
                    best_ratio = math.inf
                    for c in self.inst.row_cols[r0]:
                        if c == j or chosen[c]:
                            continue
                        g = sum(1 for rr in self.inst.col_rows[c] if cover[rr] == 0)
                        if g > 0:
                            ratio = self.inst.cost[c] / g
                            if ratio < best_ratio or (
                                ratio == best_ratio and self.rng.getrandbits(1)
                            ):
                                best_ratio = ratio
                                best_col = c
                    if best_col == -1:
                        cost = saved_cost + 1
                        break
                    chosen[best_col] = True
                    cost += self.inst.cost[best_col]
                    for rr in self.inst.col_rows[best_col]:
                        cover[rr] += 1
                    uncovered_rows = [rr for rr in uncovered_rows if cover[rr] == 0]

                if cost < saved_cost:
                    cost = self._prune(chosen, cover, cost)
                self.evaluations += 1

                if cost < saved_cost:
                    improved = True
                    break
                chosen = saved_chosen
                cover = saved_cover
                cost = saved_cost

        return chosen, cover, cost

    def solve(self, budget_sec: float = 10.0, conv_file: str | None = None) -> tuple[int, list[int]]:
        t0 = time.perf_counter()
        deadline = t0 + budget_sec
        best_cost = math.inf
        best_cols: list[int] = []
        history: list[tuple[float, int, int, int]] = []

        iteration = 0
        while iteration == 0 or time.perf_counter() < deadline:
            iteration += 1
            if self.alpha is not None:
                alpha = self.alpha
            elif iteration == 1:
                alpha = 0.0
            else:
                alpha = self.rng.uniform(0.02, 0.12)

            chosen, cover, cost = self._construct(alpha)
            if time.perf_counter() < deadline:
                chosen, cover, cost = self._local_search(chosen, cover, cost, deadline)

            if cost < best_cost:
                best_cost = cost
                best_cols = [j for j in range(1, self.inst.n + 1) if chosen[j]]
                now_s = time.perf_counter() - t0
                history.append((now_s, iteration, self.evaluations, int(best_cost)))

            if time.perf_counter() >= deadline:
                break

        if conv_file:
            conv_path = Path(conv_file)
            if conv_path.parent:
                conv_path.parent.mkdir(parents=True, exist_ok=True)
            with conv_path.open("w", encoding="utf-8") as f:
                f.write("time_s,iter,evals,best\n")
                for t_s, it, ev, b in history:
                    f.write(f"{t_s:.4f},{it},{ev},{b}\n")

        return int(best_cost), best_cols


def main():
    if len(sys.argv) < 4:
        print("Cach dung: python src/aco_or_grasp.py <input_file> <GRASP> <output_sol> [seed] [budget_sec] [conv_csv] [alpha]")
        sys.exit(1)

    in_file = sys.argv[1]
    algo = sys.argv[2].upper()
    if algo != "GRASP":
        print(f"Thuat toan khong ho tro: {algo} (chi ho tro GRASP)")
        sys.exit(1)

    out_file = sys.argv[3]
    seed = int(sys.argv[4]) if len(sys.argv) >= 5 else 42
    budget = float(sys.argv[5]) if len(sys.argv) >= 6 else 10.0
    conv_file = sys.argv[6] if len(sys.argv) >= 7 else "conv.csv"
    alpha = float(sys.argv[7]) if len(sys.argv) >= 8 else None

    inst = SCPInstance()
    if not inst.load_from_file(in_file):
        print(f"Loi doc file: {in_file}")
        sys.exit(1)

    out_path = Path(out_file)
    if out_path.parent:
        out_path.parent.mkdir(parents=True, exist_ok=True)

    t_start = time.perf_counter()
    solver = GRASPSolver(inst, seed=seed, alpha=alpha)
    cost, cols = solver.solve(budget_sec=budget, conv_file=conv_file)
    elapsed = time.perf_counter() - t_start
    save_solution(out_file, cost, cols)
    print(f"[GRASP] Cost: {cost} | Time: {elapsed:.4f}s")


if __name__ == "__main__":
    main()
