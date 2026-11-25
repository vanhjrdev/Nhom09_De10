# Tóm tắt công việc đã hoàn thành — Member D (Phạm Nhật Mai Thành)

## 1. Các tệp đã tạo và cập nhật

| Tệp | Chức năng |
|---|---|
| `src/aco_or_grasp.py` | Cài đặt thuật toán **GRASP** (`GRASPSolver`): dựng nghiệm tham lam ngẫu nhiên (RCL theo tỉ số Chvátal $c_j / g_j$, vòng 1 $\alpha=0$, các vòng sau $\alpha \sim U(0.02, 0.12)$), xóa cột thừa và tìm kiếm cục bộ (hoán đổi 1-1 + destroy-1 & greedy repair). Tương thích `scp_core.py`, `kiemtra.py` và CLI thống nhất của nhóm. |
| `experiments/run_all.py` | Script chạy thực nghiệm tổng hợp cho tất cả thuật toán (`EXACT`, `GREEDY`, `HC_FI`, `HC_BI`, `TS`, `SA`, `GA`, `GA_LS`, `GRASP`), tự động kiểm tra từng nghiệm bằng `src/kiemtra.py`, xuất `results/raw/<algo>.csv` (đúng schema 11 cột), `results/solutions/` và `results/conv/`. |
| `experiments/summarize.py` | Tổng hợp `best`, `mean`, `std`, `median`, `gap_best_pct`, `gap_mean_pct`, `opt_rate_pct`, `mean_time_s` (phân biệt rõ `OPT` và `BKS_nhom`) ra `results/summary.csv` và `results/summary.md`. |
| `experiments/statistics.py` | Kiểm định phi tham số thuần Python chuẩn: **Friedman** (trên trung bình từng instance) và **Wilcoxon signed-rank** từng cặp (ghép cặp theo `(instance, seed)` + hiệu chỉnh Holm), xuất `results/statistics.csv` và `results/statistics.md`. |
| `experiments/plot.py` | Vẽ biểu đồ SVG thuần Python chuẩn vào `results/figures/`: đường hội tụ trung vị (`conv_<instance>.svg`), boxplot phân bố chi phí (`boxplot_<instance>.svg`), và so sánh gap trung bình (`gap_comparison.svg`). |
| `README.md` | Cập nhật mục 3, 5, 6 với lệnh chạy `aco_or_grasp.py` (`GRASP`) và bộ script thực nghiệm/tổng hợp/biểu đồ/kiểm định của thành viên D. |
| `report/thanh_vien_D.tex` | Bản thảo báo cáo LaTeX phần Thành viên D (mô tả GRASP, thiết kế thực nghiệm, bảng tổng hợp, kiểm định thống kê và kết luận). |
| `results/member_d/` | Thư mục kết quả riêng của Member D (tương tự `results/member_c/`), chứa `GRASP.csv`, `summary.csv` (7 dòng tổng hợp GRASP), 70 tệp nghiệm `*_GRASP_s*.sol` và 70 tệp hội tụ `*_GRASP_s*_conv.csv`. |

> **Lưu ý sửa lỗi ở mã nguồn có sẵn:** Trong quá trình chạy thực nghiệm chéo, phát hiện `src/greedy.py` bị thiếu 3 dòng khai báo (`class State:`, `def _pick(...)`, `def run_cli(...)`) làm `greedy.py`, `local_search.py` và `tabu.py` lỗi `NameError`. Đã bổ sung lại 3 dòng khai báo này để toàn bộ module của nhóm chạy thông suốt.

## 2. Kết quả chạy thực nghiệm đã thực hiện

- **Cấu hình chạy:** 7 thể hiện tự sinh trong `data/tusinh/` (4 nhỏ, 3 vừa), 10 seed (`1..10`), ngân sách `0.3s`/lần chạy. Toàn bộ nghiệm đều đạt `HOP LE` qua `src/kiemtra.py`.
- **Kết quả nổi bật của GRASP:**
  - 4 thể hiện nhỏ (`nho_10x20_s101`..`nho_25x30_s104`): đạt tối ưu $10/10$ lần chạy (65, 136, 212, 133).
  - `vua_100x400_s201`: `best = 204`, `mean = 204.00 ± 0.00` (tốt nhất trong các thuật toán ở ngân sách 0.3s).
  - `vua_150x600_s202`: `best = 261`, `mean = 262.70 ± 2.11`.
  - `vua_200x1000_s203`: `best = 316`, `mean = 321.30 ± 4.11`.
- **Thống kê:**
  - Friedman ($\text{N}=7$, $\text{k}=8$): $\chi^2_F = 12.9564$, $p = 0.0732$; hạng trung bình tốt nhất là `TS` ($3.714$), đồng hạng nhì `GA_LS` và `GRASP` ($3.929$).
  - Wilcoxon signed-rank (ghép cặp theo `instance, seed`, hiệu chỉnh Holm): `GRASP` (mean chung `190.57`) vượt trội có ý nghĩa thống kê so với `GREEDY` (`195.00`, $p_{\text{Holm}} = 6.24 \times 10^{-7}$) và `GA` (`193.27`, $p_{\text{Holm}} = 0.0059$).

## 3. Việc còn lại (khi nhóm bổ sung dữ liệu chuẩn)

- Khi có các thể hiện OR-Library (như `scp41`, `scp51`, `scp61`) trong `data/chuan/`, chạy lại `python experiments\run_all.py --include-exact --budget 30` (hoặc ngân sách nhóm chốt), rồi chạy `summarize.py`, `statistics.py`, `plot.py` để cập nhật số liệu cuối cho báo cáo.
