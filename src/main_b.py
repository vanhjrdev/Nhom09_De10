import random
import sys
import time


def read_instance(path):
    with open(path) as f:
        tok = f.read().split()
    p = 0
    m, n = int(tok[0]), int(tok[1]); p = 2
    cost = [int(float(x)) for x in tok[p:p + n]]; p += n
    rows, cols = [], [[] for _ in range(n)]
    for i in range(m):
        k = int(tok[p]); p += 1
        r = [int(x) - 1 for x in tok[p:p + k]]; p += k
        rows.append(r)
        for j in r:
            cols[j].append(i)
    return m, n, cost, rows, cols


def is_valid(inst, sel):
    m, n, cost, rows, cols = inst
    s = set(sel)
    return all(any(j in s for j in rows[i]) for i in range(m))


class State:
    """sel[j]: cot j duoc chon; cnt[i]: so cot dang chon phu hang i (de tinh delta)."""

    def __init__(self, inst):
        self.m, self.n, self.c, self.rows, self.cols = inst
        self.sel = [False] * self.n
        self.cnt = [0] * self.m
        self.value = 0

    def add(self, j):
        self.sel[j] = True
        self.value += self.c[j]
        for i in self.cols[j]:
            self.cnt[i] += 1

    def remove(self, j):
        self.sel[j] = False
        self.value -= self.c[j]
        for i in self.cols[j]:
            self.cnt[i] -= 1

    def chosen(self):
        return [j for j in range(self.n) if self.sel[j]]

    def copy_solution(self):
        return self.chosen()


def repair(st, rng=None, forbid=None):
    """Them cot theo ti so chi phi / so hang moi phu cho den khi phu het. Tra ve cac cot da them."""
    added = []
    unc = {i for i in range(st.m) if st.cnt[i] == 0}
    while unc:
        cand = set()
        for i in unc:
            cand.update(st.rows[i])
        best, bj = None, []
        for j in cand:
            if st.sel[j] or (forbid and j in forbid):
                continue
            k = sum(1 for i in st.cols[j] if i in unc)
            if k == 0:
                continue
            r = st.c[j] / k
            if best is None or r < best - 1e-12:
                best, bj = r, [j]
            elif abs(r - best) <= 1e-12:
                bj.append(j)
        if not bj:                       
            return repair(st, rng, None) if forbid else added
        j = rng.choice(bj) if rng else bj[0]
        st.add(j)
        added.append(j)
        unc -= set(st.cols[j])
    return added


def remove_redundant(st):
    """Xoa cot thua: duyet theo chi phi giam dan, bo cot neu moi hang no phu con >= 2 cot."""
    for j in sorted(st.chosen(), key=lambda x: -st.c[x]):
        if all(st.cnt[i] >= 2 for i in st.cols[j]):
            st.remove(j)


def greedy_chvatal(inst, rng=None):
    st = State(inst)
    repair(st, rng)
    remove_redundant(st)
    return st


def hill_climb(st, rng, deadline, best_improvement, log=None, t0=0.0):
    """Lan can 1: hoan doi 1-1 (delta = c[k]-c[j]); lan can 2: bo cot j roi sua chua.
    best_improvement=False -> first improvement."""
    def snapshot():
        return st.chosen()

    def load(sol):
        for j in st.chosen():
            st.remove(j)
        for j in sol:
            st.add(j)

    improved = True
    while improved and time.time() < deadline:
        improved = False
        remove_redundant(st)
        sel = st.chosen()
        rng.shuffle(sel)
        best_move, best_delta = None, 0
        for j in sel:
            if time.time() >= deadline:
                break
            only = [i for i in st.cols[j] if st.cnt[i] == 1]
            # lan can 1: swap 1-1 co delta c[k]-c[j]
            if only:
                oset = set(only)
                for k in st.rows[only[0]]:
                    if st.sel[k] or k == j:
                        continue
                    if oset <= set(st.cols[k]):
                        d = st.c[k] - st.c[j]
                        if d < best_delta:
                            best_move, best_delta = ("swap", j, k), d
                            if not best_improvement:
                                break
                if best_move and not best_improvement:
                    break
            # lan can 2: bo j roi sua chua (kem xoa cot thua)
            snap, old = snapshot(), st.value
            st.remove(j)
            repair(st, rng, forbid={j})
            remove_redundant(st)
            d = st.value - old
            if d < best_delta:
                best_move, best_delta = ("dr", j, snapshot()), d
            load(snap)
            if best_move and not best_improvement:
                break
        if best_move:
            if best_move[0] == "swap":
                st.remove(best_move[1]); st.add(best_move[2])
            else:
                load(best_move[2])
            improved = True
            if log is not None:
                log.append((time.time() - t0, st.value))
    return st


def tabu_search(inst, rng, budget, log, t0, tenure=None, sample=40):
    st = greedy_chvatal(inst, rng)
    best_val, best_sol = st.value, st.chosen()
    log.append((time.time() - t0, best_val))
    tenure = tenure or max(5, int(0.1 * len(best_sol)) + 3)
    tabu_until = {}
    it = 0
    deadline = t0 + budget
    while time.time() < deadline:
        it += 1
        cur = st.chosen()
        cand_cols = cur if len(cur) <= sample else rng.sample(cur, sample)
        move_best = None                     # (gia tri, j, loi giai moi)
        for j in cand_cols:
            if time.time() >= deadline:
                break
            old_sol = st.chosen()
            st.remove(j)
            forb = {k for k, t in tabu_until.items() if t > it}
            forb.add(j)
            repair(st, rng, forbid=forb)
            remove_redundant(st)
            v, sol = st.value, st.chosen()
            for a in st.chosen():
                st.remove(a)
            for a in old_sol:
                st.add(a)
            is_tabu = tabu_until.get(j, 0) > it
            if is_tabu and v >= best_val:    # tieu chi mong doi (aspiration)
                continue
            if move_best is None or v < move_best[0]:
                move_best = (v, j, sol)
        if move_best is None:
            continue
        v, j, sol = move_best
        for a in st.chosen():
            st.remove(a)
        for a in sol:
            st.add(a)
        tabu_until[j] = it + tenure + rng.randint(0, 2)
        if st.value < best_val:
            best_val, best_sol = st.value, st.chosen()
            log.append((time.time() - t0, best_val))
    return best_val, best_sol


def main():
    if len(sys.argv) < 6:
        print(__doc__)
        sys.exit(1)
    path, algo, seed, budget, out = sys.argv[1], sys.argv[2], int(sys.argv[3]), float(sys.argv[4]), sys.argv[5]
    conv = sys.argv[6] if len(sys.argv) > 6 else None
    inst = read_instance(path)
    rng = random.Random(seed)
    t0 = time.time()
    log = []
    if algo == "GREEDY":
        st = greedy_chvatal(inst)
        val, sol = st.value, st.chosen()
        log.append((time.time() - t0, val))
    elif algo in ("HC_FI", "HC_BI"):
        st = greedy_chvatal(inst, rng)
        log.append((time.time() - t0, st.value))
        hill_climb(st, rng, t0 + budget, algo == "HC_BI", log, t0)
        val, sol = st.value, st.chosen()
    elif algo == "TS":
        val, sol = tabu_search(inst, rng, budget, log, t0)
    else:
        sys.exit("Thuat toan khong hop le: " + algo)
    elapsed = time.time() - t0
    ok = is_valid(inst, sol)
    with open(out, "w") as f:
        f.write(f"{val}\n{' '.join(str(j + 1) for j in sorted(sol))}\n")
    if conv:
        with open(conv, "w") as f:
            f.write("time_s,iter,evals,best\n")
            for i, (t, b) in enumerate(log):
                f.write(f"{t:.4f},{i},{i},{b}\n")
    print(f"{path},{algo},seed={seed},value={val},time_s={elapsed:.3f},feasible={ok}")


if __name__ == "__main__":
    main()
