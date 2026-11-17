#include "scp_core.hpp"
#include <chrono>
#include <random>
#include <cmath>
#include <climits>

using namespace std::chrono;

// ==========================================
// 1. THUAT TOAN CHINH XAC (NHANH CAN + GIAM CO)
// ==========================================
struct ExactSolver {
    const SCPInstance& inst;
    long long best_cost = LLONG_MAX;
    vector<int> best_cols;
    vector<int> cur_cols;
    vector<bool> dominated;
    double time_limit_sec;
    steady_clock::time_point start_time;
    bool timeout = false;

    ExactSolver(const SCPInstance& _inst, double _limit = 600.0)
        : inst(_inst), time_limit_sec(_limit) {
        dominated.assign(inst.n + 1, false);
    }

    // Giam co: Loai bo cot j1 neu tap phu cua j1 la tap con cua j2 va cost[j1] >= cost[j2]
    void preprocessDominatedColumns() {
        for (int j1 = 1; j1 <= inst.n; ++j1) {
            if (dominated[j1]) continue;
            if (inst.col_rows[j1].empty()) {
                dominated[j1] = true;
                continue;
            }
            for (int j2 = 1; j2 <= inst.n; ++j2) {
                if (j1 == j2 || dominated[j2]) continue;
                if (inst.cost[j2] <= inst.cost[j1] &&
                    inst.col_rows[j2].size() >= inst.col_rows[j1].size()) {
                    if (includes(inst.col_rows[j2].begin(), inst.col_rows[j2].end(),
                                 inst.col_rows[j1].begin(), inst.col_rows[j1].end())) {
                        dominated[j1] = true;
                        break;
                    }
                }
            }
        }
    }

    // Can duoi nhanh: voi moi hang chua phu, cong chi phi nho nhat chia cho kich thuoc cot
    long long lowerBound(const vector<int>& cov_cnt) {
        double lb = 0.0;
        for (int i = 1; i <= inst.m; ++i) {
            if (cov_cnt[i] == 0) {
                double min_unit = 1e18;
                for (int c : inst.row_cols[i]) {
                    if (!dominated[c]) {
                        min_unit = min(min_unit, (double)inst.cost[c] / inst.col_rows[c].size());
                    }
                }
                if (min_unit > 1e17) return LLONG_MAX / 2;
                lb += min_unit;
            }
        }
        return (long long)ceil(lb - 1e-9);
    }

    void dfs(long long cur_cost, int covered_rows, vector<int>& cov_cnt) {
        if (timeout) return;
        double elapsed = duration<double>(steady_clock::now() - start_time).count();
        if (elapsed > time_limit_sec) {
            timeout = true;
            return;
        }

        if (cur_cost >= best_cost) return;

        if (covered_rows == inst.m) {
            best_cost = cur_cost;
            best_cols = cur_cols;
            return;
        }

        if (cur_cost + lowerBound(cov_cnt) >= best_cost) return;

        // Chon hang chua phu co it lua chon nhat (MRV heuristic)
        int target_row = -1;
        int min_options = INT_MAX;
        for (int i = 1; i <= inst.m; ++i) {
            if (cov_cnt[i] == 0) {
                int opts = 0;
                for (int c : inst.row_cols[i]) if (!dominated[c]) opts++;
                if (opts == 0) return; // Ngo cut
                if (opts < min_options) {
                    min_options = opts;
                    target_row = i;
                }
            }
        }

        // Sap xep cac cot ung vien theo chi phi tang dan
        vector<int> candidates;
        for (int c : inst.row_cols[target_row]) {
            if (!dominated[c]) candidates.push_back(c);
        }
        sort(candidates.begin(), candidates.end(), [&](int a, int b) {
            return inst.cost[a] < inst.cost[b];
        });

        for (int c : candidates) {
            if (cur_cost + inst.cost[c] >= best_cost) continue;

            int newly_covered = 0;
            for (int r : inst.col_rows[c]) {
                if (cov_cnt[r] == 0) newly_covered++;
                cov_cnt[r]++;
            }
            cur_cols.push_back(c);

            dfs(cur_cost + inst.cost[c], covered_rows + newly_covered, cov_cnt);

            cur_cols.pop_back();
            for (int r : inst.col_rows[c]) {
                cov_cnt[r]--;
            }
        }
    }

    pair<long long, vector<int>> solve() {
        start_time = steady_clock::now();
        preprocessDominatedColumns();
        vector<int> cov_cnt(inst.m + 1, 0);
        dfs(0, 0, cov_cnt);
        return {best_cost, best_cols};
    }
};

// ==========================================
// 2. SIMULATED ANNEALING (SA) CHO SET COVER
// ==========================================
struct SASolver {
    const SCPInstance& inst;
    mt19937 rng;

    SASolver(const SCPInstance& _inst, uint32_t seed) : inst(_inst), rng(seed) {}

    // Khoi tao tham lam Chvatal + xoa cot thua
    void buildInitial(vector<bool>& in_sol, vector<int>& cov_cnt, long long& total_cost) {
        in_sol.assign(inst.n + 1, false);
        cov_cnt.assign(inst.m + 1, 0);
        total_cost = 0;
        int uncovered = inst.m;

        while (uncovered > 0) {
            int best_c = -1;
            double best_ratio = 1e18;
            for (int j = 1; j <= inst.n; ++j) {
                if (in_sol[j]) continue;
                int new_cov = 0;
                for (int r : inst.col_rows[j]) if (cov_cnt[r] == 0) new_cov++;
                if (new_cov > 0) {
                    double ratio = (double)inst.cost[j] / new_cov;
                    if (ratio < best_ratio) {
                        best_ratio = ratio;
                        best_c = j;
                    }
                }
            }
            in_sol[best_c] = true;
            total_cost += inst.cost[best_c];
            for (int r : inst.col_rows[best_c]) {
                if (cov_cnt[r] == 0) uncovered--;
                cov_cnt[r]++;
            }
        }
        removeRedundant(in_sol, cov_cnt, total_cost);
    }

    // Xoa cot thua (cac cot ma moi hang cua no deu co >= 2 cot phu)
    void removeRedundant(vector<bool>& in_sol, vector<int>& cov_cnt, long long& total_cost) {
        vector<int> chosen;
        for (int j = 1; j <= inst.n; ++j) if (in_sol[j]) chosen.push_back(j);
        // Xet xoa cot dat nhat truoc
        sort(chosen.begin(), chosen.end(), [&](int a, int b) {
            return inst.cost[a] > inst.cost[b];
        });

        for (int c : chosen) {
            bool can_remove = true;
            for (int r : inst.col_rows[c]) {
                if (cov_cnt[r] <= 1) {
                    can_remove = false;
                    break;
                }
            }
            if (can_remove) {
                in_sol[c] = false;
                total_cost -= inst.cost[c];
                for (int r : inst.col_rows[c]) cov_cnt[r]--;
            }
        }
    }

    // Sua chua khi bi thieu hang phu: them cot re nhat cho hang chua phu
    void repair(vector<bool>& in_sol, vector<int>& cov_cnt, long long& total_cost) {
        for (int i = 1; i <= inst.m; ++i) {
            if (cov_cnt[i] == 0) {
                int best_c = -1;
                double best_score = 1e18;
                for (int c : inst.row_cols[i]) {
                    int gain = 0;
                    for (int r : inst.col_rows[c]) if (cov_cnt[r] == 0) gain++;
                    double score = (double)inst.cost[c] / max(1, gain);
                    if (score < best_score) {
                        best_score = score;
                        best_c = c;
                    }
                }
                in_sol[best_c] = true;
                total_cost += inst.cost[best_c];
                for (int r : inst.col_rows[best_c]) cov_cnt[r]++;
            }
        }
    }

    pair<long long, vector<int>> solve(double budget_sec, const string& conv_csv_file) {
        auto t0 = steady_clock::now();
        ofstream fconv(conv_csv_file);
        fconv << "time_s,iter,evals,best\n";

        vector<bool> cur_sol, best_sol;
        vector<int> cur_cov;
        long long cur_cost = 0;

        buildInitial(cur_sol, cur_cov, cur_cost);
        best_sol = cur_sol;
        long long best_cost = cur_cost;

        double T = max(1.0, best_cost * 0.05); // Nhiet do khoi tao
        double alpha = 0.995;                  // He so lam nguoi
        int steps_per_temp = max(20, inst.n / 5);

        uniform_int_distribution<int> col_dist(1, inst.n);
        uniform_real_distribution<double> prob_dist(0.0, 1.0);

        long long iter = 0, evals = 1;
        fconv << "0.0000,0,1," << best_cost << "\n";

        while (true) {
            double elapsed = duration<double>(steady_clock::now() - t0).count();
            if (elapsed >= budget_sec) break;

            for (int step = 0; step < steps_per_temp; ++step) {
                iter++;
                vector<bool> next_sol = cur_sol;
                vector<int> next_cov = cur_cov;
                long long next_cost = cur_cost;

                // Lan can: Bo 1-2 cot ngau nhien dang chon, sau do sua chua + xoa thua
                int flip_cnt = (prob_dist(rng) < 0.7) ? 1 : 2;
                for (int f = 0; f < flip_cnt; ++f) {
                    int c = col_dist(rng);
                    if (next_sol[c]) {
                        next_sol[c] = false;
                        next_cost -= inst.cost[c];
                        for (int r : inst.col_rows[c]) next_cov[r]--;
                    } else {
                        next_sol[c] = true;
                        next_cost += inst.cost[c];
                        for (int r : inst.col_rows[c]) next_cov[r]++;
                    }
                }

                repair(next_sol, next_cov, next_cost);
                removeRedundant(next_sol, next_cov, next_cost);
                evals++;

                long long delta = next_cost - cur_cost;
                if (delta <= 0 || prob_dist(rng) < exp(-(double)delta / T)) {
                    cur_sol = move(next_sol);
                    cur_cov = move(next_cov);
                    cur_cost = next_cost;

                    if (cur_cost < best_cost) {
                        best_cost = cur_cost;
                        best_sol = cur_sol;
                        double now_s = duration<double>(steady_clock::now() - t0).count();
                        fconv << now_s << "," << iter << "," << evals << "," << best_cost << "\n";
                    }
                }
            }
            T = max(0.01, T * alpha);
        }

        vector<int> res_cols;
        for (int j = 1; j <= inst.n; ++j) if (best_sol[j]) res_cols.push_back(j);
        return {best_cost, res_cols};
    }
};

int main(int argc, char* argv[]) {
    if (argc < 4) {
        cerr << "Cach dung: ./solver <input_file> <EXACT|SA> <output_sol> [seed] [budget_sec] [conv_csv]\n";
        return 1;
    }

    string in_file = argv[1];
    string algo = argv[2];
    string out_file = argv[3];
    uint32_t seed = (argc >= 5) ? stoul(argv[4]) : 42;
    double budget = (argc >= 6) ? stod(argv[5]) : 10.0;
    string conv_file = (argc >= 7) ? argv[6] : "conv.csv";

    SCPInstance inst;
    if (!inst.loadFromFile(in_file)) {
        cerr << "Loi doc file: " << in_file << "\n";
        return 1;
    }

    auto t_start = steady_clock::now();
    if (algo == "EXACT") {
        ExactSolver solver(inst, budget);
        auto [cost, cols] = solver.solve();
        double elapsed = duration<double>(steady_clock::now() - t_start).count();
        saveSolution(out_file, cost, cols);
        cout << "[EXACT] Cost: " << cost << " | Time: " << elapsed << "s"
             << (solver.timeout ? " (TIMEOUT)" : "") << "\n";
    } else if (algo == "SA") {
        SASolver solver(inst, seed);
        auto [cost, cols] = solver.solve(budget, conv_file);
        double elapsed = duration<double>(steady_clock::now() - t_start).count();
        saveSolution(out_file, cost, cols);
        cout << "[SA] Cost: " << cost << " | Time: " << elapsed << "s\n";
    }
    return 0;
}