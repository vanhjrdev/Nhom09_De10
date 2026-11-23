# Genetic Algorithm

- Mã hóa: mỗi bit biểu thị một vị trí camera.
- Khởi tạo quần thể hợp lệ bằng sửa chữa và xóa cột thừa.
- Tournament 3; lai đồng đều; đột biến từng bit; giữ cá thể tốt nhất.
- Tham số mặc định: 40 cá thể, xác suất đột biến $1/n$.

# GA lai tìm kiếm cục bộ

- Sau sửa chữa, thử thay một camera bằng camera rẻ hơn.
- Chỉ thay nếu mọi nút vẫn được phủ; cập nhật số camera phủ gia tăng.
- Cùng dữ liệu, seed và ngân sách để so sánh GA và GA lai.
- Dùng kết quả thực nghiệm của nhóm để bổ sung biểu đồ và nhận xét.

# Kiểm thử chéo ban đầu

- 4 thể hiện tự sinh nhỏ của B, 10 seed, ngân sách 0,05 giây.
- 80/80 lời giải GA và GA_LS hợp lệ qua bộ kiểm tra độc lập.
- Cả hai thuật toán khớp các giá trị đối chiếu 65, 136, 212 và 133 ở mọi seed.
- Chưa kết luận ưu thế thuật toán; cần ngân sách chính thức và dữ liệu chuẩn/lớn.
