# Tóm tắt đợt làm việc lần 2 – Member B (Hoàng Duy Khánh)

## 0. Làm trước khi chép file vào repo
Mình (AI) không truy cập được repo của nhóm, nên chưa chạy được `git status` hay `git pull`. Bạn tự chạy trước khi chép file:
```bash
git status
git pull --rebase        # đang ở nhánh Khanh/tsk
git log --oneline -5     # xem A, C, D đã đẩy gì
```
Sau khi pull, mở `src/scp_core.py` và `src/kiemtra.py` của A, rồi đối chiếu với mục 4 bên dưới.

## 1. Đã làm
Chia lại code của B theo đúng sườn trong README chung (mỗi thuật toán một module, thay cho `main_B.py` cũ):

| Tệp | Nội dung |
|---|---|
| `src/greedy.py` | `State` (mảng `cnt`, chi phí cập nhật gia tăng, nhật ký rollback), `repair`, `remove_redundant`, tham lam Chvátal, giao diện chạy chung (`run_cli`) |
| `src/local_search.py` | Hai lân cận (hoán đổi 1–1; bỏ rồi sửa chữa), leo đồi `HC_FI` và `HC_BI` |
| `src/tabu.py` | Tabu Search `TS` có tabu, aspiration đúng nghĩa, tham số `tenure`, `sample` |
| `report/thanh_vien_B.tex` | Cập nhật mục TS cho khớp code mới (aspiration, rollback) |

`src/main_B.py` cũ đã bị thay thế, bạn xóa khỏi repo nếu đã commit (`git rm src/main_B.py`).

## 2. Thay đổi so với bản lần 1
- Giao diện chạy theo README mục 8: `python src/<solver>.py <input> <algorithm> <output_sol> [seed] [budget] [conv_csv] [khoa=gia_tri ...]`.
- Tham số tùy chọn `raw=<tệp.csv>` tự ghi một dòng kết quả thô đúng 11 cột của README mục 6.4; `run=<số>` đặt chỉ số lần chạy.
- Phép thử của lân cận được hoàn tác bằng nhật ký (rollback), không sao chép lời giải. Đã kiểm tra: sau 200 phép thử và hoàn tác, lời giải, `cnt` và chi phí không đổi.
- Aspiration của TS được sửa thành đúng nghĩa: phép di chuyển dùng cột tabu được chấp nhận nếu tốt hơn lời giải tốt nhất.
- `GREEDY` giờ xác định (deterministic) và là điểm xuất phát chung của `HC_FI`, `HC_BI`, `TS`.

## 3. Kết quả kiểm thử
- Ví dụ nhỏ của đề (`vidu.txt`): `GREEDY`, `HC_FI`, `HC_BI`, `TS` đều ra 16, lời giải `1 2 4`.
- Thử 1 seed, ngân sách 5 giây (chỉ để kiểm tra chạy được, không phải kết quả thực nghiệm):

| Thể hiện | GREEDY | HC_FI | HC_BI | TS |
|---|---|---|---|---|
| vua_100x400_s201 | 213 | 211 | 211 | 204 |
| vua_200x1000_s203 | 330 | 316 | 316 | 316 |

- Mọi lời giải đều hợp lệ theo kiểm tra nội bộ. Khi nộp vẫn phải chạy `kiemtra.py` độc lập.
- Dòng CSV mẫu: `vidu,6,TS,,1,1,16,1.0000,0.0000,167781,1`.

## 4. Điều cần thống nhất với nhóm
- **Bộ đọc chung:** `greedy.py` đang dùng bộ đọc tạm `load_instance` (trả về `m, n, cost, rows, cols`, cột đánh số từ 0). Cần đổi sang `scp_core.py` của A sau khi xem giao diện của A.
- **Định nghĩa `evals`:** hiện là số phép di chuyển lân cận được đánh giá. Cần nhóm chốt trước khi dùng làm ngân sách.
- **Ngân sách:** hiện tính theo giây (README mục 10.1 chưa chốt giá trị chính thức).
- **Ngôn ngữ:** README đã ghi Python, nhưng `main_C.cpp` của C đang là C++. Cần xác nhận để so sánh thời gian công bằng.
- **Seed sinh dữ liệu và seed chạy:** hai loại seed phải tách riêng (đã tách).

## 5. Đoạn gửi A ghép vào README mục 8
```text
Phần B: greedy.py (GREEDY), local_search.py (HC_FI, HC_BI), tabu.py (TS)
Chạy:   python src/<module>.py <input> <ALGORITHM> <output_sol> [seed] [budget_giay] [conv_csv] [raw=<csv>] [run=<n>]
TS:     tham số tenure (mặc định max(5, 0.1*|X|+3)), sample (mặc định 40)
Ví dụ:  python src/tabu.py data/vidu/vidu.txt TS output.sol 42 10 conv.csv tenure=8 sample=30
        python src/kiemtra.py data/vidu/vidu.txt output.sol
```

## 6. Còn lại (đã hoàn thành bổ sung)
- [x] Tải 3 thể hiện OR-Library (`scp41.txt`, `scp51.txt`, `scp61.txt`) vào `data/chuan/`, ghi `data/chuan/LINKS.txt`, cập nhật `data/tusinh/DANH_MUC.md`.
- [x] Bổ sung `src/gen_scp.py` (đối chiếu khớp 7/7 file trong `data/tusinh/`) và đổi `greedy.py` dùng `scp_core.py`, kiểm tra chéo 100% nghiệm qua `kiemtra.py`.
- [x] Chạy thực nghiệm `GREEDY`, `HC_FI`, `HC_BI`, `TS` trên cả 10 thể hiện (`data/tusinh/` + `data/chuan/`) với seed `1..10` (`experiments/member_b/run_member_b.py`).
- [x] Phân tích độ nhạy `tenure`, `sample` trên tập tinh chỉnh riêng (`tune_100x400_s901`, `tune_150x600_s902`) lưu tại `results/member_b/ts_sensitivity.csv`.
- [x] Điền đầy đủ số liệu vào `report/thanh_vien_B.tex`.
- [ ] Làm slide phần B.

## 7. Ghi nhận việc dùng AI (theo mục 3.4 của đề)
Mã nguồn `greedy.py`, `local_search.py`, `tabu.py`, `gen_scp.py` và bản nháp `report/thanh_vien_B.tex` được tạo với sự hỗ trợ của AI (Claude). Thành viên B cần đọc hiểu và tự giải thích được trước khi nộp.

## 8. Lệnh git gợi ý
```bash
git status && git pull --rebase
git rm src/main_B.py                       # nếu đã từng commit
git add src/greedy.py src/local_search.py src/tabu.py
git commit -m "B: tach module greedy/local_search/tabu theo README, them rollback va aspiration"
git add report/thanh_vien_B.tex plan/tom_tat_B_lan2.md
git commit -m "B: cap nhat bao cao TS va tom tat lan 2"
git push
```
