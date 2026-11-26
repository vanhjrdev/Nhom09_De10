# Nhóm 09 — Đề 10: Đặt camera giám sát giao thông

Bài toán phủ tập có trọng số (Weighted Set Cover).

## 1. Thông tin nhóm và phân công

| Thành viên | Họ tên | Phần code | Phần báo cáo |
|---|---|---|---|
| A | Phan Việt Anh | Bộ đọc (`scp_core.py`), bộ kiểm tra (`kiemtra.py`), `EXACT`, `SA` | Phát biểu bài toán, NP-khó, thuật toán chính xác, SA, ghép báo cáo |
| B | Hoàng Duy Khánh | `GREEDY`, `HC_FI`, `HC_BI`, `TS`, bộ sinh dữ liệu (`gen_scp.py`) | Heuristic, tìm kiếm cục bộ, Tabu Search |
| C | Huỳnh Xuân Huy | `GA` và `GA_LS` (GA + tìm kiếm cục bộ) | Genetic Algorithm và thuật toán lai |
| D | Mai Đàm Công Thành | `GRASP`, script thực nghiệm, tổng hợp, biểu đồ, kiểm định | Thực nghiệm, phân tích thống kê, kết luận |


## 2. Môi trường

- Hệ điều hành: Windows 11 Pro
- Ngôn ngữ: Python 3.12.9
- Thông dịch: CPython (không cần biên dịch)
- Thư viện: Chỉ dùng thư viện chuẩn Python (`argparse`, `collections`, `csv`, `dataclasses`, `html`, `math`, `os`, `pathlib`, `random`, `re`, `subprocess`, `sys`, `time`). Không có tệp khai báo phụ thuộc ngoài (`requirements.txt`).

## 3. Lệnh cài đặt, sinh dữ liệu và chạy một thuật toán trên một thể hiện

### Lệnh biên dịch / cài đặt
Python là ngôn ngữ thông dịch, không cần biên dịch hay cài đặt thư viện ngoài. Chạy trực tiếp với `python` (Python 3.12+).

### Khung lệnh thống nhất cho từng thuật toán
```powershell
python src\main_A.py <tep_vao> <EXACT|SA> <tep_ra> [seed] [budget_sec] [conv_csv]
python src\greedy.py <tep_vao> GREEDY <tep_ra> [seed] [budget_sec] [conv_csv]
python src\local_search.py <tep_vao> <HC_FI|HC_BI> <tep_ra> [seed] [budget_sec] [conv_csv]
python src\tabu.py <tep_vao> TS <tep_ra> [seed] [budget_sec] [conv_csv] [tenure=<int>] [sample=<int>]
python src\main_C.py <tep_vao> <GA|GA_LS> <tep_ra> [seed] [budget_sec] [conv_csv] [population] [mutation_rate]
python src\aco_or_grasp.py <tep_vao> GRASP <tep_ra> [seed] [budget_sec] [conv_csv] [alpha]
```

Sinh dữ liệu tự sinh (Member B):
```powershell
python src\gen_scp.py --presets
```

| Tham số | Ý nghĩa | Mặc định |
|---|---|---|
| `tep_vao` | Tệp instance định dạng OR-Library | bắt buộc |
| `thuật_toán` | `EXACT`, `SA`, `GREEDY`, `HC_FI`, `HC_BI`, `TS`, `GA`, `GA_LS`, `GRASP` | bắt buộc |
| `tep_ra` | Tệp nghiệm đầu ra | bắt buộc |
| `seed` | Seed sinh số ngẫu nhiên | `42` (`1` với `greedy.py`/`local_search.py`/`tabu.py`) |
| `budget_sec` | Ngân sách thời gian (giây) | `10.0` |
| `conv_csv` | Tệp log hội tụ (`time_s,iter,evals,best`) | `conv.csv` |
| `tenure`, `sample` | Độ dài tabu và số ứng viên mẫu mỗi vòng (`TS`) | `max(5, int(0.1*\|X\|)+3)`, `40` |
| `population`, `mutation_rate` | Kích thước quần thể và tỉ lệ đột biến (`GA`/`GA_LS`) | `40`, `1/n` |
| `alpha` | Ngưỡng danh sách ứng viên hạn chế RCL (`GRASP`) | vòng 1 `0.0`, sau `U(0.02, 0.12)` |

### Ví dụ chạy được ngay (ví dụ đề, kết quả đúng `16`)

```powershell
python src\main_A.py data\vidu\vidu.txt EXACT results\solutions\vidu_EXACT.sol 42 10
```

Kết quả mong đợi: `[EXACT] Cost: 16 | Time: ...s`

## 4. Lệnh kiểm tra nghiệm

```powershell
python src\kiemtra.py <tep_vao> <tep_loi_giai>
```

Ví dụ:
```powershell
python src\kiemtra.py data\vidu\vidu.txt results\solutions\vidu_EXACT.sol
```

Kết quả mong đợi: `HOP LE | Tong chi phi: 16`

## 5. Chạy toàn bộ thực nghiệm và sinh lại bảng, biểu đồ

### Chạy toàn bộ thực nghiệm của nhóm (Member D)
```powershell
python experiments\run_all.py [--include-exact] [--budget 0.5] [--seeds 1 2 3 4 5 6 7 8 9 10]
python experiments\summarize.py
python experiments\statistics.py
python experiments\plot.py
```

- **Tập dữ liệu:** 7 thể hiện tự sinh trong `data\tusinh\` (`nho_10x20_s101`..`vua_200x1000_s203`) và 3 thể hiện chuẩn OR-Library trong `data\chuan\` (`scp41`, `scp51`, `scp61`).
- **Danh sách seed đã dùng:** `1, 2, 3, 4, 5, 6, 7, 8, 9, 10` cho tất cả thuật toán metaheuristic/tìm kiếm cục bộ (`EXACT` dùng `seed = 1`; seed sinh dữ liệu tách riêng: `101..104`, `201..203` và tập tinh chỉnh `901..902`).
- **Đầu ra:**
  - Kết quả thô: `results\raw\<thuật_toán>.csv` (11 cột: `instance,n,algorithm,params,seed,run,best_value,time_s,time_to_best_s,evaluations,feasible`).
  - Nghiệm và log hội tụ: `results\solutions\<thể_hiện>_<thuật_toán>_s<seed>.sol`, `results\conv\<thể_hiện>_<thuật_toán>_s<seed>_conv.csv`.
  - Bảng tổng hợp: `results\summary.csv`, `results\summary.md`.
  - Kiểm định thống kê: `results\statistics.csv`, `results\statistics.md` (Friedman và Wilcoxon signed-rank + Holm).
  - Biểu đồ: `results\figures\` (`conv_*.svg`, `boxplot_*.svg`, `gap_comparison.svg`).
- **Thời gian chạy ước tính:** Với 10 thể hiện × 8 thuật toán × 10 seed = 800 lần chạy tại `--budget 0.5`, tổng thời gian khoảng **~5,6 phút (~336 giây)** trên Windows 11; các lệnh `summarize.py`, `statistics.py`, `plot.py` chạy dưới 5 giây.

### Script thực nghiệm riêng của thành viên (B, C)
- Thành viên B (đánh giá + phân tích độ nhạy `TS` vào `results\member_b\`):
  ```powershell
  python experiments\member_b\run_member_b.py --budget 0.5 --tune-budget 0.3
  ```
- Thành viên C (chạy `GA`, `GA_LS` trên dữ liệu tự sinh):
  ```powershell
  python experiments\member_c\run_tusinh.py [--budget 1.0] [--seeds 1 2 3 4 5 6 7 8 9 10] [--population 40] [--mutation-rate 0.025] [--output results] [instance...]
  ```

## 6. Tham số mặc định của từng metaheuristic

| Thuật toán | Người phụ trách | Tham số mặc định |
|---|---|---|
| `SA` | A | `seed=42`, `budget=10.0s`, `T0 = 0.05 × chi phí ban đầu`, `alpha=0.995`, `steps_per_temp = max(20, n//5)`, sửa chữa + xóa cột thừa |
| `TS` | B | `seed=1` (CLI) / `1..10` (thực nghiệm), `budget=10.0s`, `tenure = max(5, int(0.1*\|X\|)+3)`, `sample=40`, tiêu chí aspiration khi tốt hơn `best_val` |
| `GA` | C | `seed=42`, `budget=10.0s`, `population=40`, `mutation_rate=1/n`, `tournament_size=3`, lai ghép đồng đều từng bit (`1/2`), elitism (1 cá thể tốt nhất) |
| `GA_LS` | C | Tương tự `GA`; sau khi sinh con chạy tìm kiếm cục bộ 1 lượt (thay camera đã chọn bằng camera chưa chọn rẻ hơn phủ mọi nút chỉ được camera đó phủ) |
| `GRASP` | D | `seed=42`, `budget=10.0s`, vòng 1 `alpha=0.0`, các vòng sau `alpha ~ U(0.02, 0.12)`, xóa cột thừa + tìm kiếm cục bộ (hoán đổi 1-1 và phá hủy 1 - sửa chữa tham lam) |
