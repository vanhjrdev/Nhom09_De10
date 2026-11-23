# Nhóm 09 — Đề 10: Đặt camera giám sát giao thông

Bài toán phủ tập có trọng số (Weighted Set Cover).

## 1. Thông tin nhóm và phân công

| Thành viên | Họ tên — MSSV | Phần code | Phần báo cáo |
|---|---|---|---|
| A | Phan Việt Anh | Bộ đọc, bộ kiểm tra, thuật toán chính xác, SA | Phát biểu bài toán, NP-khó, thuật toán chính xác, SA, ghép báo cáo |
| B | Hoàng Duy Khánh | Tham lam Chvátal, xóa cột thừa, tìm kiếm cục bộ, TS, bộ sinh dữ liệu | Heuristic, tìm kiếm cục bộ, Tabu Search |
| C | Huỳnh Xuân Huy | GA và GA_LS (GA + tìm kiếm cục bộ) | Genetic Algorithm và thuật toán lai |
| D | Phạm Nhật Mai Thành | ACO hoặc GRASP, script thực nghiệm, biểu đồ, kiểm định | Thực nghiệm, phân tích thống kê, kết luận |

Đề: Đề 10 — Đặt camera giám sát giao thông: bài toán phủ tập (Set Cover), mức độ Khá.

## 2. Môi trường

- Hệ điều hành: Windows 11 Pro
- Ngôn ngữ: Python 3.12.9
- Thông dịch: CPython (không cần biên dịch)
- Thư viện: Chỉ dùng thư viện chuẩn Python (`argparse`, `csv`, `math`, `random`, `sys`, `time`, `pathlib`, `subprocess`, `re`, `dataclasses`). Không có tệp khai báo phụ thuộc (`requirements.txt`).

## 3. Lệnh chạy một thuật toán trên một thể hiện

### Khung lệnh thống nhất
```
python src\main_A.py <tep_vao> <EXACT|SA> <tep_ra> [seed] [budget_sec] [conv_csv]
python src\main_C.py <tep_vao> <GA|GA_LS> <tep_ra> [seed] [budget_sec] [conv_csv] [population] [mutation_rate]
```

| Tham số | Ý nghĩa | Mặc định |
|---|---|---|
| `tep_vao` | Tệp instance định dạng OR-Library | bắt buộc |
| `EXACT\|SA` / `GA\|GA_LS` | Thuật toán | bắt buộc |
| `tep_ra` | Tệp nghiệm đầu ra | bắt buộc |
| `seed` | Seed sinh số ngẫu nhiên | 42 |
| `budget_sec` | Ngân sách thời gian (giây) | 10.0 |
| `conv_csv` | Tệp log hội tụ (`time_s,iter,evals,best`) | conv.csv |
| `population` | Kích thước quần thể (GA) | 40 |
| `mutation_rate` | Xác suất đột biến (GA) | 1/n |

### Ví dụ chạy được ngay (ví dụ đề, kết quả đúng 16)

```
python src\main_A.py data\vidu\vidu.txt EXACT results\solutions\vidu_EXACT.sol 42 10 results\conv\vidu_EXACT_conv.csv
```

Kết quả mong đợi: `[EXACT] Cost: 16 | Time: ...s`

### Lệnh biên dịch/cài đặt
Python là ngôn ngữ thông dịch, không cần biên dịch hay cài đặt thư viện ngoài. Chạy trực tiếp với `python`.

## 4. Lệnh kiểm tra nghiệm

```
python src\kiemtra.py <tep_vao> <tep_loi_giai>
```

Ví dụ:
```
python src\kiemtra.py data\vidu\vidu.txt results\solutions\vidu_EXACT.sol
```

Kết quả mong đợi: `HOP LE | Tong chi phi: 16`

## 5. Chạy toàn bộ thực nghiệm và sinh lại bảng, biểu đồ

Thành viên C có sẵn script chạy GA và GA_LS trên dữ liệu tự sinh:

```
python experiments\member_c\run_tusinh.py [--budget 1.0] [--seeds 1 2 3 4 5 6 7 8 9 10] [--population 40] [--mutation-rate 0.025] [--output results] [instance...]
```

- Mặc định chạy mọi file `.txt` trong `data\tusinh`; xuất ra `results/raw/GA.csv` và `results/raw/GA_LS.csv`.
- Seed đã dùng: `1` đến `10`.
- Tệp kết quả thô: `results/raw/<thuật toán>.csv` (mỗi thuật toán một tệp), mỗi dòng là một lần chạy với cột `instance,n,algorithm,params,seed,run,best_value,time_s,time_to_best_s,evaluations,feasible`.
- Tệp nghiệm: `results/solutions/<thể hiện>_<thuật toán>_s<seed>.sol`.
- Log hội tụ: `results/conv/<thể hiện>_<thuật toán>_s<seed>_conv.csv`.
- Thời gian ước tính: tuỳ số instance và ngân sách (mặc định 1.0 giây/lần chạy).

Script tổng hợp chung, biểu đồ và kiểm định thống kê (của thành viên D) chưa hoàn thiện; khi hoàn thiện sẽ thêm lệnh tại đây.

## 6. Tham số mặc định của từng metaheuristic

| Thuật toán | Người phụ trách | Tham số mặc định |
|---|---|---|
| SA | A | seed=42, budget=10.0s, T0 = 0.05 × chi phí tốt nhất, alpha=0.995, steps_per_temp = max(20, n//5) |
| TS | B | Chưa cài đặt |
| GA | C | seed=42, budget=10.0s, population=40, mutation_rate=1/n, tournament size=3, lai ghép từng bit (chọn từ cha A hoặc B, 1/2 mỗi bit), elitism (giữ cá thể tốt nhất) |
| GA_LS | C | Tương tự GA; sau mỗi sự sinh, chạy tìm kiếm cục bộ: thay camera đã chọn bằng camera chưa chọn rẻ hơn phủ mọi nút chỉ được camera đó phủ, nếu chi phí thấp hơn |
| ACO/GRASP | D | Chưa chọn thuật toán |
