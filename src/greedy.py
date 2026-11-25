import os
import random
import sys
import time

from scp_core import SCPInstance


def load_instance(path):
    inst = SCPInstance()
    if not inst.load_from_file(path):
        raise OSError(f"Khong mo duoc tep vao: {path}")
    cost = inst.cost[1:]
    rows = [[c - 1 for c in inst.row_cols[i]] for i in range(1, inst.m + 1)]
    cols = [sorted(r - 1 for r in inst.col_rows[j]) for j in range(1, inst.n + 1)]
    return inst.m, inst.n, cost, rows, cols


def is_valid(inst, sol):
    m, n, cost, rows, cols = inst
    s = set(sol)
    return all(any(j in s for j in rows[i]) for i in range(m))




class State:
    def __init__(self, inst):
        self.m, self.n, self.c, self.rows, self.cols = inst
        self.colset = [set(c) for c in self.cols]
        self.sel = [False] * self.n
        self.cnt = [0] * self.m
        self.value = 0
        self.trail = []
        self.evals = 0

    def _add(self, j):
        self.sel[j] = True
        self.value += self.c[j]
        for i in self.cols[j]:
            self.cnt[i] += 1

    def _remove(self, j):
        self.sel[j] = False
        self.value -= self.c[j]
        for i in self.cols[j]:
            self.cnt[i] -= 1

    def add(self, j):
        self._add(j)
        self.trail.append((j, 1))

    def remove(self, j):
        self._remove(j)
        self.trail.append((j, -1))

    def mark(self):
        return len(self.trail)

    def rollback(self, mark):
        
        while len(self.trail) > mark:
            j, op = self.trail.pop()
            if op > 0:
                self._remove(j)
            else:
                self._add(j)

    def commit(self):
        self.trail.clear()

    def chosen(self):
        return [j for j in range(self.n) if self.sel[j]]

    def set_solution(self, sol):
        
        target = set(sol)
        for j in self.chosen():
            if j not in target:
                self.remove(j)
        for j in target:
            if not self.sel[j]:
                self.add(j)


def _pick(st, unc, rng=None, forbid=None):
    cand = set()
    for i in unc:
        cand.update(st.rows[i])
    best, ties = None, []
    for j in cand:
        if st.sel[j] or (forbid and j in forbid):
            continue
        k = sum(1 for i in st.cols[j] if i in unc)
        if k == 0:
            continue
        r = st.c[j] / k
        if best is None or r < best - 1e-12:
            best, ties = r, [j]
        elif abs(r - best) <= 1e-12:
            ties.append(j)
    if not ties:
        return None
    return rng.choice(sorted(ties)) if rng else min(ties)


def repair(st, rng=None, forbid=None):
    added = []
    unc = {i for i in range(st.m) if st.cnt[i] == 0}
    while unc:
        j = _pick(st, unc, rng, forbid)
        if j is None and forbid:
            j = _pick(st, unc, rng, None)
        if j is None:
            break                       
        st.add(j)
        added.append(j)
        unc.difference_update(st.cols[j])
    return added


def remove_redundant(st):
    removed = []
    for j in sorted(st.chosen(), key=lambda x: (-st.c[x], x)):
        if all(st.cnt[i] >= 2 for i in st.cols[j]):
            st.remove(j)
            removed.append(j)
    return removed


def greedy_chvatal(inst, rng=None):
    st = State(inst)
    repair(st, rng)
    remove_redundant(st)
    st.commit()
    return st


def run_cli(runners, doc):
    args = sys.argv[1:]
    if len(args) < 3:
        print(doc)
        sys.exit(1)
    inp, algo, out = args[:3]
    pos, params = [], {}
    for a in args[3:]:
        if "=" in a:
            k, v = a.split("=", 1)
            params[k] = v
        else:
            pos.append(a)
    seed = int(pos[0]) if len(pos) > 0 else 1
    budget = float(pos[1]) if len(pos) > 1 else 10.0
    conv = pos[2] if len(pos) > 2 else None
    if algo not in runners:
        sys.exit("Thuật toán không hợp lệ: %s (chọn trong %s)" % (algo, ", ".join(runners)))
    inst = load_instance(inp)
    rng = random.Random(seed)
    t0 = time.time()
    value, sol, log, t_best, evals, iters = runners[algo](inst, rng, budget, params, t0)
    elapsed = time.time() - t0
    ok = is_valid(inst, sol)

    for path in (out, conv, params.get("raw")):
        if path and os.path.dirname(path):
            os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(out, "w") as f:
        f.write("%d\n%s\n" % (value, " ".join(str(j + 1) for j in sorted(sol))))
    if conv:
        with open(conv, "w") as f:
            f.write("time_s,iter,evals,best\n")
            for t, it, ev, b in log:
                f.write("%.4f,%d,%d,%d\n" % (t, it, ev, b))
    raw = params.get("raw")
    if raw:
        new = not os.path.exists(raw)
        shown = ";".join("%s=%s" % (k, v) for k, v in sorted(params.items()) if k not in ("raw", "run"))
        name = os.path.splitext(os.path.basename(inp))[0]
        with open(raw, "a") as f:
            if new:
                f.write("instance,n,algorithm,params,seed,run,best_value,time_s,time_to_best_s,evaluations,feasible\n")
            f.write("%s,%d,%s,%s,%d,%s,%d,%.4f,%.4f,%d,%d\n" % (
                name, inst[1], algo, shown, seed, params.get("run", seed), value,
                elapsed, t_best, evals, 1 if ok else 0))
    print("%s,%s,seed=%d,value=%d,time_s=%.3f,feasible=%s" % (inp, algo, seed, value, elapsed, ok))


def _run_greedy(inst, rng, budget, params, t0):
    st = greedy_chvatal(inst)
    t = time.time() - t0
    return st.value, st.chosen(), [(t, 0, 0, st.value)], t, 0, 0


if __name__ == "__main__":
    run_cli({"GREEDY": _run_greedy}, __doc__)
