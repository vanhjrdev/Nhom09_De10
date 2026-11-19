import time

from greedy import State, greedy_chvatal, remove_redundant, repair, run_cli


def hill_climb(st, rng, deadline, best_improvement, log, t0):
    iters = 0
    improved = True
    while improved and time.time() < deadline:
        improved = False
        remove_redundant(st)
        st.commit()
        order = st.chosen()
        rng.shuffle(order)
        best = None                              
        done = False
        for j in order:
            if time.time() >= deadline:
                break
            only = [i for i in st.cols[j] if st.cnt[i] == 1]
            if only:
                need = set(only)
                for k in st.rows[only[0]]:
                    if st.sel[k] or k == j:
                        continue
                    st.evals += 1
                    if need <= st.colset[k]:
                        delta = st.c[k] - st.c[j]
                        if delta < 0:
                            if not best_improvement:
                                st.remove(j)
                                st.add(k)
                                st.commit()
                                done = True
                                break
                            if best is None or delta < best[0]:
                                best = (delta, "swap", (j, k))
                if done:
                    break
            
            mk, old = st.mark(), st.value
            st.remove(j)
            repair(st, rng, {j})
            remove_redundant(st)
            st.evals += 1
            delta = st.value - old
            if delta < 0:
                if not best_improvement:
                    st.commit()
                    done = True
                    break
                if best is None or delta < best[0]:
                    best = (delta, "dr", st.chosen())
            st.rollback(mk)
        if done:
            improved = True
        elif best is not None:
            _, kind, data = best
            if kind == "swap":
                st.remove(data[0])
                st.add(data[1])
            else:
                st.set_solution(data)
            st.commit()
            improved = True
        if improved:
            iters += 1
            log.append((time.time() - t0, iters, st.evals, st.value))
    return iters


def _run(best_improvement):
    def runner(inst, rng, budget, params, t0):
        st = greedy_chvatal(inst)
        log = [(time.time() - t0, 0, 0, st.value)]
        iters = hill_climb(st, rng, t0 + budget, best_improvement, log, t0)
        t_best = log[-1][0]
        return st.value, st.chosen(), log, t_best, st.evals, iters
    return runner


if __name__ == "__main__":
    run_cli({"HC_FI": _run(False), "HC_BI": _run(True)}, __doc__)
