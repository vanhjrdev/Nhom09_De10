# Thành viên C — Huỳnh Xuân Huy: GA và GA_LS

## Code đã có
- `src/main_C.py`: `GeneticSolver`. GA: tournament size 3, lai ghép từng bit (1/2 mỗi bit), đột biến `1/n`, elitism (giữ cá thể tốt nhất). GA_LS: sau mỗi con sinh, tìm kiếm cục bộ — thay camera đã chọn bằng camera chưa chọn rẻ hơn phủ mọi nút chỉ được camera đó phủ, nếu chi phí thấp hơn.
- `experiments/member_c/run_tusinh.py`: chạy GA và GA_LS trên dữ liệu tự sinh, seed 1–10, budget mặc định 1.0s, population 40. Xuất `results/raw/GA.csv` và `results/raw/GA_LS.csv` theo quy ước đề mục 6.2.

## Công việc còn làm
- Thêm file `.txt` vào `data/tusinh/` (dữ liệu tự sinh, ghi seed sinh).
- Chạy `run_tusinh.py` sinh `results/raw/GA.csv` và `results/raw/GA_LS.csv`.
- Phân tích độ nhạy tham số GA (population, mutation_rate).
- Xác nhận GA_LS ra 16 trên `data/vidu/vidu.txt` trong budget 0.1s.
- Viết phần báo cáo: Genetic Algorithm và thuật toán lai.

## Lưu ý
- `data/vidu/vidu.sol` (`16` / `1 2 4`) thuộc phần việc của A tạo, C chỉ chạy thử trên `vidu.txt` có sẵn.
