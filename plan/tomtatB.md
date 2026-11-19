# Tóm tắt phần việc của member B (Đề 10 – Set Cover)

## 1. Phạm vi theo bảng phân công
- **Code:** tham lam Chvátal, xóa cột thừa, tìm kiếm cục bộ (2 lân cận), Tabu Search, bộ sinh dữ liệu tự sinh.
- **Báo cáo:** mục (d) Heuristic và tìm kiếm cục bộ; phần Tabu Search trong mục (e).
- **Slide:** Heuristic, tìm kiếm cục bộ, Tabu Search.

## 2. Các tệp đã tạo

| Tệp | Nội dung |
|---|---|
| `src/gen_scp.py` | Bộ sinh dữ liệu Set Cover, định dạng OR-Library. Mọi hàng có ít nhất 1 cột phủ. Cùng seed cho cùng tệp. |
| `src/main_B.py` | `GREEDY` (Chvátal + xóa cột thừa), `HC_FI`, `HC_BI` (leo đồi), `TS` (Tabu Search). |
| `data/tusinh/` | 4 thể hiện nhỏ (≤ 30 cột), 3 thể hiện vừa, kèm `DANH_MUC.md`. |
| `report/thanh_vien_B.tex` | Báo cáo mục (d) và phần TS. Còn chỗ `[CHO SO LIEU]` chờ thực nghiệm. |
| `plan/tom_tat_member_B.md` | Tệp này. |

## 3. Cách chạy
Sinh dữ liệu:
```
python src/gen_scp.py <m> <n> <mat_do> <seed_sinh> <tep_ra>
```
Chạy thuật toán:
```
python src/main_B.py <tep_vao> <GREEDY|HC_FI|HC_BI|TS> <seed> <giay> <tep.sol> [conv.csv]
```
Ví dụ: `python src/main_B.py data/vidu/vidu.txt TS 1 2 results/solutions/vidu_TS_s1.sol`

Tệp lời giải: dòng 1 là tổng chi phí, dòng 2 là các cột chọn (tăng dần, đánh số từ 1).
Kiểm tra độc lập bằng `src/kiemtra.py` của A.

## 4. Thiết kế chính
- Lời giải là tập cột; duy trì mảng `cnt[i]` (số cột đang chọn phủ hàng `i`) để tính delta nhanh.
- Lân cận 1: hoán đổi 1–1, hợp lệ khi cột mới phủ mọi hàng chỉ do cột cũ phủ; delta = c_k − c_j.
- Lân cận 2: bỏ một cột rồi sửa chữa (theo tỉ số Chvátal) và xóa cột thừa.
- Tabu Search: bỏ cột rồi sửa chữa, cột vừa bỏ bị cấm thêm lại trong `tenure` vòng; mặc định `tenure = max(5, ⌊0.1·|X|⌋+3)` cộng ngẫu nhiên 0–2; mỗi vòng xét tối đa 40 cột.

## 5. Kết quả kiểm thử đã có
- Trên ví dụ nhỏ của đề (`vidu.txt`): cả 4 thuật toán cho 16, lời giải `1 2 4` (đúng tối ưu của đề).
- Trên 7 thể hiện tự sinh: `GREEDY` cho lời giải hợp lệ.
- Chưa có kết quả thực nghiệm chính thức (10 seed, đủ ngân sách).

## 6. Hạn chế đã biết
- `main_B.py` đang tự chứa bộ đọc, chưa dùng chung `scp_core.py` của A.
- Code B viết bằng Python, `main_C.cpp` của C là C++; nhóm cần thống nhất ngôn ngữ khi so sánh thời gian.
- Aspiration của TS: cột bị cấm chỉ được thêm lại khi không còn ứng viên khác; kiểm tra aspiration theo giá trị tốt nhất gần như không kích hoạt.
- Log hội tụ đang ghi `iter` và `evals` bằng nhau; cần thống nhất định nghĩa số lần đánh giá.
- Chưa có 3 thể hiện OR-Library trong `data/chuan/`.

## 7. Việc còn lại
- [ ] Tải 3 thể hiện OR-Library vào `data/chuan/`, ghi nguồn và giá trị tối ưu/BKS vào `data/tusinh/DANH_MUC.md` (hoặc danh mục chung).
- [ ] Chạy `GREEDY`, `HC_FI`, `HC_BI`, `TS` với seed 1–10, ghi `results/raw/*.csv`.
- [ ] Phân tích độ nhạy tham số TS (tập thể hiện riêng, không dùng tập đánh giá cuối).
- [ ] Điền số liệu vào `report/thanh_vien_B.tex`.
- [ ] Làm slide phần B.

## 7b. Ghi nhận việc dùng AI (theo mục 3.4 của đề)
Mã nguồn `src/gen_scp.py`, `src/main_B.py` và bản nháp `report/thanh_vien_B.tex` được tạo với sự hỗ trợ của AI (Claude). Dữ liệu tự sinh trong `data/tusinh/` được sinh bằng `gen_scp.py`.
Thành viên B cần đọc hiểu, tự giải thích được thuật toán, và kiểm tra lại kết quả trước khi nộp.
Mục này cần ghi vào báo cáo (mục nguồn tham khảo hoặc phụ lục), vì đề yêu cầu ghi rõ mọi đoạn mã hoặc ý tưởng từ công cụ AI.

## 8. Lệnh git cho phần B
```
git checkout -b member-b
git add src/gen_scp.py src/main_B.py
git commit -m "B: gen_scp + Chvatal/HC/TS"
git add data/tusinh/
git commit -m "B: du lieu tu sinh va danh muc"
git add report/thanh_vien_B.tex plan/tom_tat_member_B.md
git commit -m "B: bao cao muc (d), TS va tom tat"
git push -u origin member-b
```
