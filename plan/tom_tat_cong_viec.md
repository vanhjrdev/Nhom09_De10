# Tóm tắt công việc đã làm (dự án Nhóm 09 — Đề 10)

## Thành viên C (Huỳnh Xuân Huy) — GA và GA_LS

### Đã có sẵn trong repo
- `src/main_C.py`: `GeneticSolver` cài GA (tournament size 3, lai ghép từng bit 1/2, mutation 1/n, elitism) và GA_LS (tìm kiếm cục bộ thay camera chọn bằng camera chưa chọn rẻ hơn phủ cùng nút).
- `experiments/member_c/run_tusinh.py`: runner chạy GA/GA_LS trên dữ liệu tự sinh, seed 1–10, budget mặc định 1.0s, population 40.

### Đã sửa trong phiên này
- `run_tusinh.py`: xuất kết quả thô vào `results/raw/GA.csv` và `results/raw/GA_LS.csv` (theo quy ước nộp bài mục 6.2: `results/raw/<thuật toán>.csv`).
- Schema cột: `instance,n,algorithm,params,seed,run,best_value,time_s,time_to_best_s,evaluations,feasible`.
- Tên file giải: `results/solutions/<instance>_<algorithm>_s<seed>.sol`.
- Log hội tụ: `results/conv/<instance>_<algorithm>_s<seed>_conv.csv`.
- `py_compile` OK.

### Còn cần làm của C
- [ ] Chuẩn bị dữ liệu tự sinh trong `data/tusinh/` (ít nhất vài file `.txt`, ghi seed sinh).
- [ ] Chạy `run_tusinh.py` để sinh `results/raw/GA.csv` và `results/raw/GA_LS.csv`.
- [ ] Phân tích độ nhạy tham số GA (population, mutation_rate) và ghi vào báo cáo.
- [ ] Xác nhận GA_LS tìm được giá trị 16 trên `data/vidu/vidu.txt` trong budget 0.1s (giống slide_thanh_vien_C.md đã ghi).
    - Lưu ý: file `data/vidu/vidu.sol` (`16` / `1 2 4`) thuộc phần việc của A tạo, C chỉ cần chạy thử trên `vidu.txt` có sẵn.

## Các thành viên còn lại — công việc còn thiếu (theo bai_tap_lon.tex đề 10)

### A (Phan Việt Anh) — Bộ đọc, kiểm tra, chính xác, SA
- [x] Chạy `EXACT` trên `data/vidu/vidu.txt` → phải ra 16 / 1 2 4.
- [x] Tạo `data/vidu/vidu.sol` (nội dung: `16` / `1 2 4`).
- [x] Xác nhận `kiemtra.py` trả về `HOP LE | Tong chi phi: 16`.

### B (Hoàng Duy Khánh) — Chvátal, xóa thừa, 2 lân cận, TS, sinh dữ liệu
- [x] `src/greedy.py`: tham lam Chvátal + xóa cột thừa.
- [x] `src/local_search.py`: HC_FI, HC_BI.
- [x] `src/tabu.py`: Tabu Search.
- [ ] `data/tusinh/`: chương trình sinh dữ liệu + instance (ghi seed, m, n, khoảng chi phí, mật độ).
- [ ] `data/chuan/`: dữ liệu chuẩn OR-Library hoặc ít nhất `LINKS.txt`.
- [ ] Chạy GREEDY/HC_FI/HC_BI/TS trên dữ liệu chuẩn và tự sinh.

### D (Phạm Nhật Mai Thành) — ACO/GRASP, script thực nghiệm, biểu đồ, kiểm định
- [ ] `src/aco_or_grasp.py`: ACO hoặc GRASP (chọn 1).
- [ ] `experiments/run_all.py`: chạy toàn bộ thực nghiệm (tất cả thuật toán, instance, seed 1–10).
- [ ] `experiments/summarize.py`, `plot.py`, `statistics.py`: bảng, biểu đồ hội tụ/boxplot, Wilcoxon/Friedman.
- [ ] `results/raw/<thuật toán>.csv` cho mỗi thuật toán.

## Cộng đồng
- [ ] 4 metaheuristic (SA, TS, GA, ACO/GRASP) + ít nhất 1 thuật toán lai (GA_LS đã có) → đáp yêu cầu nhóm 4.
- [ ] Thống nhất ngân sách và seed (1–10) trước khi chạy đánh giá cuối.
- [ ] Báo cáo PDF 20–40 trang, slide, demo (mục 12–13 README).
