# Tóm tắt công việc hiện tại (Nhóm 09 — Đề 10: Set Cover)

## 1. Trạng thái theo từng thành viên

### Thành viên A (Phan Việt Anh) — Bộ đọc, kiểm tra, chính xác, SA
- [x] `src/scp_core.py`: mô hình dữ liệu + bộ đọc OR-Library.
- [x] `src/kiemtra.py`: bộ kiểm tra độc lập (`HOP LE` / `KHONG HOP LE`, liệt kê hàng chưa phủ).
- [x] `src/main_A.py`: `ExactSolver` (nhánh cận + giảm cỡ) và `SASolver` (`SA`, hỗ trợ tham số `t0_factor`, `cool_alpha`).
- [x] `data/vidu/vidu.sol` (`16` / `1 2 4`) và xác nhận `kiemtra.py` trả về `HOP LE | Tong chi phi: 16`.
- [x] Phân tích độ nhạy tham số `SA` (`results/member_d/sa_sensitivity.csv`).
- [x] `report/thanh_vien_A.tex`.
- [ ] Điền MSSV/GV/tỉ lệ đóng góp và biên dịch `report/BaoCao_Nhom09_De10.pdf` + `report/Slide_Nhom09_De10.pdf`.

### Thành viên B (Hoàng Duy Khánh) — Chvátal, xóa thừa, 2 lân cận, TS, dữ liệu
- [x] `src/greedy.py`: tham lam Chvátal + xóa cột thừa, đã tích hợp bộ đọc chung `scp_core.py`.
- [x] `src/local_search.py`: `HC_FI`, `HC_BI` (2 lân cận + đánh giá gia tăng qua mảng `cnt`).
- [x] `src/tabu.py`: `TS` (Tabu Search có aspiration và rollback).
- [x] `src/gen_scp.py`: chương trình sinh dữ liệu tự sinh (tái lập khớp 7/7 thể hiện trong `data/tusinh/`).
- [x] `data/chuan/`: đã tải 3 thể hiện chuẩn OR-Library (`scp41.txt`, `scp51.txt`, `scp61.txt`) + `LINKS.txt` + cập nhật `DANH_MUC.md`.
- [x] `experiments/member_b/run_member_b.py`: đánh giá trên cả 10 thể hiện (`results/member_b/eval_member_b.csv`) và phân tích độ nhạy `TS` (`results/member_b/ts_sensitivity.csv`).
- [x] `report/thanh_vien_B.tex`.
- [ ] Làm slide phần B.

### Thành viên C (Huỳnh Xuân Huy) — GA và GA_LS
- [x] `src/main_C.py`: `GA` và `GA_LS` (thuật toán lai).
- [x] `experiments/member_c/run_example.py`, `run_tusinh.py`, `run_ga_sensitivity.py`, `results/member_c/ga_sensitivity.{csv,md}`.
- [x] `report/thanh_vien_C.tex`, `report/slide_thanh_vien_C.md`, `report/bao_cao_nhom09_de10.tex`.

### Thành viên D (Phạm Nhật Mai Thành) — GRASP, thực nghiệm, biểu đồ, kiểm định
- [x] `src/aco_or_grasp.py`: chốt và cài đặt **GRASP** (RCL Chvátal + xóa cột thừa + local search hoán đổi 1-1 & destroy-1/repair).
- [x] `experiments/run_all.py`: chạy đủ 800 lần trên **10 thể hiện** (7 tự sinh + 3 OR-Library `scp41`, `scp51`, `scp61`), seed `1–10`, kiểm tra nghiệm qua `kiemtra.py`.
- [x] `experiments/summarize.py`, `statistics.py`, `plot.py`: sinh `results/summary.*`, `results/statistics.*` (Friedman $\chi^2_F = 19{,}9419, p = 0{,}0057$; Wilcoxon + Holm), và `21` biểu đồ SVG trong `results/figures/`.
- [x] `experiments/member_d/run_sensitivity.py`: phân tích độ nhạy `GRASP` (`alpha`) và `SA` (`t0_factor`, `cool_alpha`) tại `results/member_d/{grasp,sa}_sensitivity.csv`.
- [x] `results/member_d/`: lưu riêng kết quả của `GRASP`.
- [x] `README.md`, `report/thanh_vien_D.tex` (đã cập nhật số liệu 10 thể hiện), `report/bao_cao_nhom09_de10.tex` (đã đồng bộ GRASP & số liệu mới), `plan/member_D.md`.
- [ ] Chuyển biểu đồ `.svg` sang `.png`/`.pdf` (Mục 6.2) nếu biên dịch LaTeX.

## 2. Quy ước kỹ thuật đã chốt
- **Ngôn ngữ & môi trường:** Python 3.12.9 (chỉ dùng thư viện chuẩn).
- **Dữ liệu chuẩn + tự sinh:** Đủ **10 thể hiện thuộc 3 mức kích thước** (4 nhỏ `10x20`–`25x30`, 3 vừa `100x400`–`200x1000`, 3 lớn chuẩn OR-Library `scp41`, `scp51`, `scp61`).
- **Seed chạy thực nghiệm:** `1..10` (tách biệt với seed sinh dữ liệu `101..104`, `201..203`, và tập tinh chỉnh `901..902`); seed mặc định CLI là `42`; `EXACT` dùng `1`.
- **4 metaheuristic + 1 lai:** `SA`, `TS`, `GA`, `GRASP` + `GA_LS` (đều đã có phân tích độ nhạy tham số).

## 3. Việc còn lại trước khi đóng gói nộp `Nhom09_De10.zip`
1. Điền MSSV, tên giảng viên, tỉ lệ đóng góp, ghi chú công cụ AI vào `report/bao_cao_nhom09_de10.tex` và biên dịch bằng XeLaTeX (ví dụ trên Overleaf) thành `report/BaoCao_Nhom09_De10.pdf`.
2. Chuyển biểu đồ trong `results/figures/` từ `.svg` sang `.png`/`.pdf` (Mục 6.2).
3. Tạo slide thuyết trình chung `report/Slide_Nhom09_De10.pdf` (5 phút).
