#include "scp_core.hpp"
#include <chrono>
#include <cmath>
#include <random>
#include <stdexcept>

using Clock = std::chrono::steady_clock;

struct Individual {
    vector<char> chosen;
    vector<int> cover;
    long long cost = 0;
};

class GeneticSolver {
    const SCPInstance& instance;
    mt19937 rng;
    int population_size;
    double mutation_rate;
    bool hybrid;
    double budget;
    Clock::time_point start;
    long long evaluations = 0;

    double elapsed() const {
        return std::chrono::duration<double>(Clock::now() - start).count();
    }
    void add(Individual& x, int j) {
        x.chosen[j] = true;
        x.cost += instance.cost[j];
        for (int i : instance.col_rows[j]) ++x.cover[i];
    }
    void remove(Individual& x, int j) {
        x.chosen[j] = false;
        x.cost -= instance.cost[j];
        for (int i : instance.col_rows[j]) --x.cover[i];
    }
    void prune(Individual& x) {
        vector<int> order;
        for (int j = 1; j <= instance.n; ++j) if (x.chosen[j]) order.push_back(j);
        shuffle(order.begin(), order.end(), rng);
        stable_sort(order.begin(), order.end(), [&](int a, int b) { return instance.cost[a] > instance.cost[b]; });
        for (int j : order) {
            bool redundant = true;
            for (int i : instance.col_rows[j]) if (x.cover[i] <= 1) { redundant = false; break; }
            if (redundant) remove(x, j);
        }
    }
    void repair(Individual& x) {
        for (int i = 1; i <= instance.m; ++i) {
            if (x.cover[i]) continue;
            int best = -1;
            double best_ratio = 1e100;
            for (int j : instance.row_cols[i]) {
                int gain = 0;
                for (int r : instance.col_rows[j]) if (!x.cover[r]) ++gain;
                double ratio = static_cast<double>(instance.cost[j]) / gain;
                if (ratio < best_ratio || (ratio == best_ratio && (rng() & 1))) {
                    best_ratio = ratio;
                    best = j;
                }
            }
            if (best < 0) throw runtime_error("Hang khong duoc cot nao phu");
            add(x, best);
        }
        prune(x);
    }
    Individual fromBits(const vector<char>& bits) {
        Individual x{vector<char>(instance.n + 1, false), vector<int>(instance.m + 1, 0), 0};
        for (int j = 1; j <= instance.n; ++j) if (bits[j]) add(x, j);
        repair(x);
        ++evaluations;
        return x;
    }
    // Tim doi mot cot da chon lay mot cot chua chon, chi chap nhan cai thien.
    void localSearch(Individual& x) {
        vector<int> selected;
        for (int j = 1; j <= instance.n; ++j) if (x.chosen[j]) selected.push_back(j);
        shuffle(selected.begin(), selected.end(), rng);
        for (int old : selected) {
            if (elapsed() >= budget) break;
            vector<int> unique_rows;
            for (int i : instance.col_rows[old]) if (x.cover[i] == 1) unique_rows.push_back(i);
            if (unique_rows.empty()) { remove(x, old); continue; }
            int pivot = unique_rows.front();
            for (int i : unique_rows) if (instance.row_cols[i].size() < instance.row_cols[pivot].size()) pivot = i;
            int replacement = -1;
            for (int j : instance.row_cols[pivot]) {
                if (x.chosen[j] || instance.cost[j] >= instance.cost[old]) continue;
                bool feasible = true;
                for (int i : unique_rows) {
                    if (!binary_search(instance.col_rows[j].begin(), instance.col_rows[j].end(), i)) { feasible = false; break; }
                }
                if (feasible && (replacement < 0 || instance.cost[j] < instance.cost[replacement])) replacement = j;
            }
            if (replacement >= 0) { remove(x, old); add(x, replacement); }
        }
        prune(x);
    }
public:
    GeneticSolver(const SCPInstance& inst, unsigned seed, int pop, double mutation, bool use_local, double seconds)
        : instance(inst), rng(seed), population_size(pop), mutation_rate(mutation), hybrid(use_local), budget(seconds) {}

    Individual solve(const string& log_path) {
        start = Clock::now();
        ofstream log(log_path);
        if (!log) throw runtime_error("Khong mo duoc tep hoi tu");
        log << "time_s,iter,evals,best\n";
        uniform_real_distribution<double> real(0.0, 1.0);
        vector<Individual> population;
        Individual best;
        auto registerBest = [&](const Individual& x, long long generation) {
            if (best.chosen.empty() || x.cost < best.cost) {
                best = x;
                log << elapsed() << ',' << generation << ',' << evaluations << ',' << best.cost << '\n';
            }
        };
        for (int k = 0; k < population_size; ++k) {
            vector<char> bits(instance.n + 1, false);
            if (k) for (int j = 1; j <= instance.n; ++j) bits[j] = real(rng) < 0.25;
            auto x = fromBits(bits);
            if (hybrid) localSearch(x);
            registerBest(x, 0);
            population.push_back(move(x));
        }
        auto tournament = [&]() -> const Individual& {
            uniform_int_distribution<int> pick(0, population_size - 1);
            int a = pick(rng), b = pick(rng), c = pick(rng);
            int winner = population[a].cost <= population[b].cost ? a : b;
            if (population[c].cost < population[winner].cost) winner = c;
            return population[winner];
        };
        long long generation = 0;
        while (elapsed() < budget) {
            ++generation;
            vector<Individual> next;
            next.push_back(best); // Giu lai ca the tot nhat.
            while (static_cast<int>(next.size()) < population_size && elapsed() < budget) {
                const Individual& a = tournament();
                const Individual& b = tournament();
                vector<char> bits(instance.n + 1, false);
                for (int j = 1; j <= instance.n; ++j) {
                    bits[j] = (real(rng) < 0.5 ? a.chosen[j] : b.chosen[j]);
                    if (real(rng) < mutation_rate) bits[j] = !bits[j];
                }
                auto child = fromBits(bits);
                if (hybrid) localSearch(child);
                registerBest(child, generation);
                next.push_back(move(child));
            }
            if (static_cast<int>(next.size()) == population_size) population = move(next);
        }
        return best;
    }
};

int main(int argc, char* argv[]) {
    if (argc < 4 || argc > 9) {
        cerr << "Cach dung: ./solver_C <input_file> <GA|GA_LS> <output_sol> [seed] [budget_sec] [conv_csv] [population] [mutation_rate]\n";
        return 1;
    }
    try {
        string algorithm = argv[2];
        if (algorithm != "GA" && algorithm != "GA_LS") throw runtime_error("Thuat toan phai la GA hoac GA_LS");
        unsigned seed = argc > 4 ? stoul(argv[4]) : 42;
        double budget = argc > 5 ? stod(argv[5]) : 10.0;
        string log = argc > 6 ? argv[6] : "conv.csv";
        int population = argc > 7 ? stoi(argv[7]) : 40;
        SCPInstance inst;
        if (!inst.loadFromFile(argv[1])) throw runtime_error("Khong doc duoc tep dau vao");
        if (inst.m <= 0 || inst.n <= 0) throw runtime_error("Kich thuoc phai duong");
        for (int j = 1; j <= inst.n; ++j) if (inst.cost[j] < 0) throw runtime_error("Chi phi phai khong am");
        for (int i = 1; i <= inst.m; ++i) if (inst.row_cols[i].empty()) throw runtime_error("Co hang khong duoc phu");
        double mutation = argc > 8 ? stod(argv[8]) : 1.0 / inst.n;
        if (!isfinite(budget) || budget <= 0 || population < 2 || !isfinite(mutation) || mutation < 0 || mutation > 1)
            throw runtime_error("Tham so khong hop le");
        GeneticSolver solver(inst, seed, population, mutation, algorithm == "GA_LS", budget);
        auto x = solver.solve(log);
        vector<int> columns;
        for (int j = 1; j <= inst.n; ++j) if (x.chosen[j]) columns.push_back(j);
        ofstream output(argv[3]);
        if (!output) throw runtime_error("Khong mo duoc tep loi giai");
        output << x.cost << '\n';
        for (size_t i = 0; i < columns.size(); ++i) output << (i ? " " : "") << columns[i];
        output << '\n';
        cout << '[' << algorithm << "] Cost: " << x.cost << '\n';
    } catch (const exception& e) {
        cerr << "Loi: " << e.what() << '\n';
        return 1;
    }
}
