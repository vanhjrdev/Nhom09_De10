# Danh mục dữ liệu tự sinh (do B sinh bằng `src/gen_scp.py`)

Chi phí cột nằm trong khoảng [1, 100]. Seed sinh dữ liệu khác với seed chạy thuật toán (1–10).
Cột đánh số từ 1, định dạng OR-Library.

| Tên tệp | Mức | Hàng m | Cột n | Mật độ | Seed sinh | Giá trị tham chiếu |
|---|---|---|---|---|---|---|
| nho_10x20_s101.txt | nhỏ | 10 | 20 | 0.30 | 101 | tối ưu (A chạy) |
| nho_15x25_s102.txt | nhỏ | 15 | 25 | 0.25 | 102 | tối ưu (A chạy) |
| nho_20x28_s103.txt | nhỏ | 20 | 28 | 0.20 | 103 | tối ưu (A chạy) |
| nho_25x30_s104.txt | nhỏ | 25 | 30 | 0.20 | 104 | tối ưu (A chạy) |
| vua_100x400_s201.txt | vừa | 100 | 400 | 0.05 | 201 | tốt nhất trong thực nghiệm |
| vua_150x600_s202.txt | vừa | 150 | 600 | 0.04 | 202 | tốt nhất trong thực nghiệm |
| vua_200x1000_s203.txt | vừa | 200 | 1000 | 0.03 | 203 | tốt nhất trong thực nghiệm |

Ghi chú đối chiếu: B đã tự kiểm tra bằng nhánh cận riêng, 4 thể hiện nhỏ có tối ưu lần lượt là
65, 136, 212, 133. Chỉ coi là chính thức khi thuật toán chính xác của A chạy ra khớp.

## Dữ liệu chuẩn OR-Library (`data/chuan/`, tải ngày 2026-11-25)

| Tên tệp | Mức | Hàng m | Cột n | Nguồn tải | Tối ưu/BKS | Nguồn tối ưu/BKS |
|---|---|---|---|---|---|---|
| scp41.txt | lớn | 200 | 1000 | `https://people.brunel.ac.uk/~mastjjb/jeb/orlib/files/scp41.txt` | 429 (OPT) | Beasley (1987), EJOR 31:85–93 |
| scp51.txt | lớn | 200 | 2000 | `https://people.brunel.ac.uk/~mastjjb/jeb/orlib/files/scp51.txt` | 253 (OPT) | Beasley (1987), EJOR 31:85–93 |
| scp61.txt | lớn | 200 | 1000 | `https://people.brunel.ac.uk/~mastjjb/jeb/orlib/files/scp61.txt` | 138 (OPT) | Beasley (1987), EJOR 31:85–93 |
