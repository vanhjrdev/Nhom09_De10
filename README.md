# Đặt camera giám sát giao thông: Set Cover

Mã nguồn thành viên A nằm trong `src/main_A.py`; bộ kiểm tra nằm trong `src/kiemtra.py`. Thành viên C cung cấp GA và GA lai tìm kiếm cục bộ trong `src/main_C.py`. Các chương trình dùng chung bộ đọc `src/scp_core.py` và chạy bằng Python 3.9 trở lên, không cần thư viện ngoài.

## Chạy phần thành viên C

```sh
python src/main_C.py data/vidu/vidu.txt GA ga.sol 42 1 ga_conv.csv
python src/main_C.py data/vidu/vidu.txt GA_LS ga_ls.sol 42 1 ga_ls_conv.csv
python src/kiemtra.py data/vidu/vidu.txt ga.sol
python src/kiemtra.py data/vidu/vidu.txt ga_ls.sol
```

Cú pháp: `python src/main_C.py <input_file> <GA|GA_LS> <output_sol> [seed] [budget_sec] [conv_csv] [population] [mutation_rate]`. Mặc định: seed 42, 10 giây, `conv.csv`, quần thể 40, xác suất đột biến bằng nghịch đảo số cột. Đầu vào dùng định dạng OR-Library của đề, lời giải ghi chi phí và danh sách cột tăng dần. Nhật ký CSV có các cột `time_s,iter,evals,best` và ghi khi tìm được lời giải tốt hơn. `evals` đếm số cá thể được sửa chữa, không đếm các phép thử hoán đổi cục bộ; không so sánh ngân sách theo số này với thuật toán khác nếu chưa thống nhất định nghĩa. Khởi tạo quần thể luôn hoàn tất, do đó tổng thời gian có thể vượt ngân sách, đặc biệt với dữ liệu lớn hoặc ngân sách rất nhỏ. Ngân sách theo thời gian không đảm bảo tái lập chính xác kết quả dù cùng seed.

Phần báo cáo LaTeX để ghép vào báo cáo chung: `report/thanh_vien_C.tex`; dàn ý slide: `report/slide_thanh_vien_C.md`. Các giá trị mặc định chưa được tinh chỉnh. Nhóm cần chạy thí nghiệm, kiểm định và bổ sung kết quả trước khi kết luận.

Kiểm thử ban đầu trên ví dụ đề: chạy `python experiments/member_c/run_example.py`. Script chạy mỗi thuật toán với 10 seed và kiểm tra lời giải; ghi kết quả vào `results/member_c`. Đây chỉ là kiểm thử nhỏ, chưa thay thế thực nghiệm chính thức.
