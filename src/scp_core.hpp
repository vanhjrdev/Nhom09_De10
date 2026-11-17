#pragma once
#include <iostream>
#include <fstream>
#include <vector>
#include <string>
#include <algorithm>
#include <numeric>

using namespace std;

struct SCPInstance {
    int m = 0; // Số nút giao (hàng, đánh số 1..m)
    int n = 0; // Số vị trí đặt camera (cột, đánh số 1..n)
    vector<long long> cost; // Chi phí cột j (1..n)
    vector<vector<int>> row_cols; // Hàng i được phủ bởi các cột nào
    vector<vector<int>> col_rows; // Cột j phủ được các hàng nào (S_j)

    bool loadFromFile(const string& filename) {
        ifstream fin(filename);
        if (!fin.is_open()) return false;

        if (!(fin >> m >> n)) return false;
        cost.assign(n + 1, 0);
        row_cols.assign(m + 1, {});
        col_rows.assign(n + 1, {});

        for (int j = 1; j <= n; ++j) {
            fin >> cost[j];
        }

        for (int i = 1; i <= m; ++i) {
            int k;
            fin >> k;
            row_cols[i].reserve(k);
            for (int idx = 0; idx < k; ++idx) {
                int col;
                fin >> col;
                if (col >= 1 && col <= n) {
                    row_cols[i].push_back(col);
                    col_rows[col].push_back(i);
                }
            }
        }
        // Sắp xếp lại cho chuẩn chỉ
        for (int j = 1; j <= n; ++j) {
            sort(col_rows[j].begin(), col_rows[j].end());
            col_rows[j].erase(unique(col_rows[j].begin(), col_rows[j].end()), col_rows[j].end());
        }
        return true;
    }
};

// Hàm ghi lời giải chuẩn: dòng 1 tổng chi phí, dòng 2 danh sách cột tăng dần
inline void saveSolution(const string& out_file, long long total_cost, vector<int> selected_cols) {
    sort(selected_cols.begin(), selected_cols.end());
    selected_cols.erase(unique(selected_cols.begin(), selected_cols.end()), selected_cols.end());
    ofstream fout(out_file);
    fout << total_cost << "\n";
    for (size_t i = 0; i < selected_cols.size(); ++i) {
        fout << selected_cols[i] << (i + 1 == selected_cols.size() ? "" : " ");
    }
    fout << "\n";
}