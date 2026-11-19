import time

from greedy import greedy_chvatal, remove_redundant, repair, run_cli


def tabu_search(inst, rng, budget, t0, tenure=None, sample=40):
    st = greedy_chvatal(inst)
    best_val, best_sol = st.value, st.chosen()
    log = [(time.time() - t0, 0, 0, best_val)]
    t_best = log[0][0]
    if tenure is None:
        tenure = max(5, int(0.1 * len(best_sol)) + 3)
    tabu_until = {}                     
    deadline = t0 + budget
    it = 0
    while time.time() < deadline:
        it += 1
        cur = st.chosen()
        if not cur:
            break
        cand = cur if len(cur) <= sample else rng.sample(cur, sample)
        tabu_set = {k for k, t in tabu_until.items() if t > it}
        move = None                      
        for j in cand:
            if time.time() >= deadline:
                break
            mk = st.mark()
            st.remove(j)
            added = repair(st, rng, forbid={j})
            remove_redundant(st)
            st.evals += 1
            used_tabu = any(a in tabu_set and st.sel[a] for a in added)
            if used_tabu and st.value >= best_val:       
                st.rollback(mk)
                st.remove(j)
                repair(st, rng, forbid=tabu_set | {j})
                remove_redundant(st)
                st.evals += 1
            v, sol = st.value, st.chosen()
            st.rollback(mk)
            if move is None or v < move[0]:
                move = (v, j, sol)
        if move is None:
            continue
        v, j, sol = move
        st.set_solution(sol)
        st.commit()
        tabu_until[j] = it + tenure + rng.randint(0, 2)
        if st.value < best_val:
            best_val, best_sol = st.value, st.chosen()
            t_best = time.time() - t0
            log.append((t_best, it, st.evals, best_val))
    return best_val, best_sol, log, t_best, st.evals, it


def _run_ts(inst, rng, budget, params, t0):
    tenure = int(params["tenure"]) if "tenure" in params else None
    sample = int(params.get("sample", 40))
    return tabu_search(inst, rng, budget, t0, tenure, sample)


if __name__ == "__main__":
    run_cli({"TS": _run_ts}, __doc__)
