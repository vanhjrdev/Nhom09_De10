# Tóm tắt công việc hiện tại (Nhóm 09 — Đề 10: Set Cover)

## 1. Trạng thái theo từng thành viên

### Thành viên A (Phan Việt Anh) — Bộ đọc, kiểm tra, chính xác, SA
- [x] `src/scp_core.py`: mô hình dữ liệu + bộ đọc OR-Library.
- [x] `src/kiemtra.py`: bộ kiểm tra độc lập (`HOP LE` / `KHONG HOP LE`, liệt kê hàng chưa phủ).
- [x] `src/main_A.py`: `ExactSolver` (nhánh cận + giảm cỡ) và `SASolver` (`SA`).
- [x] `data/vidu/vidu.sol` (`16` / `1 2 4`) và xác nhận `kiemtra.py` trả về `HOP LE | Tong chi phi: 16`.
- [x] `report/thanh_vien_A.tex`.
- [ ] Ghép báo cáo chung `report/BaoCao_Nhom09_De10.pdf` và `report/Slide_Nhom09_De10.pdf`.

### Thành viên B (Hoàng Duy Khánh) — Chvátal, xóa thừa, 2 lân cận, TS, dữ liệu
- [x] `src/greedy.py`: tham lam Chvátal + xóa cột thừa (đã vá 3 dòng khai báo thiếu `class State`, `def _pick`, `def run_cli`).
- [x] `src/local_search.py`: `HC_FI`, `HC_BI` (2 lân cận + đánh giá gia tăng qua mảng `cnt`).
- [x] `src/tabu.py`: `TS` (Tabu Search có aspiration và rollback).
- [x] `data/tusinh/`: 7 thể hiện tự sinh (4 nhỏ `10x20`–`25x30` seed `101..104`, 3 vừa `100x400`–`200x1000` seed `201..203`) và `DANH_MUC.md`.
- [x] `report/thanh_vien_B.tex`.
- [ ] Bổ sung chương trình sinh dữ liệu (`src/gen_scp.py`) vào repo.
- [ ] Bổ sung dữ liệu chuẩn OR-Library (`scp4x`–`scp6x`, tối thiểu `scp41` hoặc `LINKS.txt`) vào `data/chuan/`.
- [ ] Phân tích độ nhạy tham số `TS` (`tenure`, `sample`).

### Thành viên C (Huỳnh Xuân Huy) — GA và GA_LS
- [x] `src/main_C.py`: `GA` và `GA_LS` (thuật toán lai).
- [x] `experiments/member_c/run_example.py`, `run_tusinh.py`, `results/member_c/`.
- [x] `report/thanh_vien_C.tex`, `report/slide_thanh_vien_C.md`.
- [ ] Phân tích độ nhạy tham số `GA` (`population`, `mutation_rate`).

### Thành viên D (Phạm Nhật Mai Thành) — GRASP, thực nghiệm, biểu đồ, kiểm định
- [x] `src/aco_or_grasp.py`: chốt và cài đặt **GRASP** (RCL Chvátal + xóa cột thừa + local search hoán đổi 1-1 & destroy-1/repair).
- [x] `experiments/run_all.py`: chạy toàn bộ thuật toán (`EXACT`, `GREEDY`, `HC_FI`, `HC_BI`, `TS`, `SA`, `GA`, `GA_LS`, `GRASP`) với seed `1–10`, kiểm tra nghiệm qua `kiemtra.py`.
- [x] `experiments/summarize.py`, `statistics.py`, `plot.py`: sinh `results/summary.*`, `results/statistics.*` (Friedman + Wilcoxon signed-rank + Holm), và 15 biểu đồ SVG trong `results/figures/`.
- [x] `results/member_d/`: lưu riêng kết quả của `GRASP` (70 nghiệm `.sol`, 70 log `_conv.csv`, `GRASP.csv`, `summary.csv`).
- [x] `README.md`, `report/thanh_vien_D.tex`, `plan/member_D.md`.
- [ ] Phân tích độ nhạy tham số `alpha` của `GRASP`; chuyển/xuất biểu đồ sang `PNG/PDF` đúng Mục 6.2; chạy lại trên `data/chuan/` khi B bổ sung dữ liệu chuẩn.

## 2. Quy ước kỹ thuật đã chốt
- **Ngôn ngữ & môi trường:** Python 3.12.9 (chỉ dùng thư viện chuẩn).
- **Seed chạy thực nghiệm:** `1..10` (tách biệt với seed sinh dữ liệu `101..104`, `201..203`); seed mặc định CLI là `42`; `EXACT` dùng `1`.
- **4 metaheuristic + 1 lai:** `SA`, `TS`, `GA`, `GRASP` + `GA_LS`.

## 3. Việc còn thiếu theo đề bài tập lớn (trước khi đóng gói nộp)
1. Bổ sung bộ dữ liệu chuẩn OR-Library (hoặc `LINKS.txt`) vào `data/chuan/` để đủ tối thiểu 10 thể hiện thuộc 3 mức kích thước (Mục 3.3).
2. Bổ sung chương trình sinh dữ liệu tự sinh (`src/gen_scp.py`) theo Mục 6.2.
3. Bổ sung phân tích độ nhạy tham số cho `SA`, `TS`, `GA`, `GRASP` (yêu cầu nhóm 4 người, Mục 2.2).
4. Xuất biểu đồ sang `PNG/PDF` (Mục 6.2) và ghép `report/BaoCao_Nhom09_De10.pdf` (20–40 trang) + `report/Slide_Nhom09_De10.pdf`.
