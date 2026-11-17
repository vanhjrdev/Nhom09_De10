#include "scp_core.hpp"

int main(int argc, char* argv[]) {
    if (argc < 3) {
        cerr << "Cu phap: kiemtra <tep_vao> <tep_loi_giai>\n";
        return 1;
    }

    SCPInstance inst;
    if (!inst.loadFromFile(argv[1])) {
        cerr << "KHONG HOP LE (Khong mo duoc tep vao)\n";
        return 1;
    }

    ifstream fsol(argv[2]);
    if (!fsol.is_open()) {
        cout << "KHONG HOP LE (Khong mo duoc tep loi giai)\n";
        return 0;
    }

    long long reported_cost;
    if (!(fsol >> reported_cost)) {
        cout << "KHONG HOP LE (Tep loi giai rong hoac sai dinh dang)\n";
        return 0;
    }

    vector<int> selected;
    int col;
    while (fsol >> col) {
        selected.push_back(col);
    }

    vector<bool> used(inst.n + 1, false);
    vector<bool> covered(inst.m + 1, false);
    long long actual_cost = 0;

    for (int c : selected) {
        if (c < 1 || c > inst.n) {
            cout << "KHONG HOP LE (Chi so cot nam ngoai pham vi: " << c << ")\n";
            return 0;
        }
        if (used[c]) {
            cout << "KHONG HOP LE (Cot bi chon lap lai: " << c << ")\n";
            return 0;
        }
        used[c] = true;
        actual_cost += inst.cost[c];
        for (int r : inst.col_rows[c]) {
            covered[r] = true;
        }
    }

    vector<int> uncovered;
    for (int i = 1; i <= inst.m; ++i) {
        if (!covered[i]) uncovered.push_back(i);
    }

    if (!uncovered.empty()) {
        cout << "KHONG HOP LE (Cac hang chua duoc phu:";
        for (int r : uncovered) cout << " " << r;
        cout << ") | Chi phi tinh duoc: " << actual_cost << "\n";
        return 0;
    }

    if (actual_cost != reported_cost) {
        cout << "KHONG HOP LE (Sai lech chi phi: bao cao=" << reported_cost
             << ", thuc te=" << actual_cost << ")\n";
        return 0;
    }

    cout << "HOP LE | Tong chi phi: " << actual_cost << "\n";
    return 0;
}