# Kế hoạch họp nhóm: Đặt camera giám sát giao thông

## Mục tiêu cuộc họp

Thống nhất dữ liệu, cách thực nghiệm, đầu việc và thời hạn để các thành viên có thể so sánh thuật toán và ghép báo cáo. Những phương án dưới đây là đề xuất, không phải quyết định đã được nhóm thông qua.

## 1. Phân công và phạm vi

- **A:** Bộ đọc, bộ kiểm tra, thuật toán chính xác, SA; phát biểu bài toán, độ phức tạp và ghép báo cáo.
- **B:** Tham lam Chvátal, xóa cột thừa, tìm kiếm cục bộ, Tabu Search và bộ sinh dữ liệu.
- **C:** GA, GA lai tìm kiếm cục bộ; báo cáo và slide cho hai thuật toán.
- **D:** ACO hoặc GRASP, script thực nghiệm, biểu đồ, kiểm định thống kê và tổng hợp kết quả.
- Xác nhận đầu mối, thời hạn bàn giao và cách xử lý khi một phần phụ thuộc phần khác.
- Thống nhất phương án bốn metaheuristic và thuật toán lai; hỏi giảng viên xác nhận cách tính theo yêu cầu nhóm bốn người.

## 2. Chọn dữ liệu

- [ ] Chọn ít nhất **10 thể hiện**, thuộc ít nhất **3 mức kích thước**, gồm dữ liệu chuẩn và tự sinh.
- [ ] Chọn các thể hiện OR-Library trong `scp4x`, `scp5x`, `scp6x`, `scpa`–`scpd` hoặc `scpnre`–`scpnrh`; ghi nguồn tải và nguồn tối ưu/BKS cho từng thể hiện.
- [ ] Kiểm tra `scp41`: 200 hàng, 1.000 cột, giá trị tối ưu 429 theo đề.
- [ ] B thống nhất số hàng, số cột, khoảng chi phí, cách sinh quan hệ phủ và seed sinh cho từng thể hiện tự sinh. Mọi hàng phải được ít nhất một cột phủ.
- [ ] Tạo các thể hiện nhỏ, khoảng tối đa 30 cột, để A chạy thuật toán chính xác. Chỉ gọi giá trị là tối ưu khi thuật toán kết thúc và chứng minh được tối ưu.
- [ ] Đặt tên tệp, thư mục và lập bảng danh mục: tên, nguồn hoặc seed sinh, số hàng, số cột, giá trị tham chiếu và nguồn tham chiếu.
- [ ] Thống nhất định dạng OR-Library: `m n`, tiếp theo `n` chi phí, rồi với mỗi hàng là số cột phủ và danh sách chỉ số cột đánh số từ 1.

Phương án để thảo luận: 4 thể hiện tự sinh nhỏ, 3 tự sinh vừa và 3 thể hiện OR-Library. Nhóm cần xác định cụ thể ba mức kích thước và kiểm tra tính phù hợp trước khi chốt.

## 3. Quy trình thực nghiệm

- [ ] Chọn máy chạy; ghi CPU, RAM, hệ điều hành, phiên bản trình biên dịch và tùy chọn biên dịch.
- [ ] Thống nhất ngân sách theo thời gian hoặc số lần đánh giá với định nghĩa chung. Đề gợi ý 30 giây cho `scp4x`–`scp6x`, 120 giây cho bộ lớn; có thể điều chỉnh nhưng phải công bằng giữa các thuật toán được so sánh.
- [ ] Chọn ít nhất 10 seed chạy độc lập cho mỗi thuật toán trên mỗi thể hiện; đề xuất `1` đến `10`. Seed chạy thuật toán khác seed sinh dữ liệu.
- [ ] Chốt tham số mặc định của mỗi thuật toán trước khi chạy đánh giá; ghi đầy đủ các tham số và phiên bản mã nguồn.
- [ ] Kiểm tra từng lời giải bằng bộ kiểm tra và lưu kết quả kiểm tra. Không đưa lời giải không hợp lệ vào bảng chất lượng như lời giải hợp lệ.
- [ ] Với thuật toán chính xác, ghi trạng thái hoàn thành hay hết thời gian; không coi lời giải khi hết thời gian là tối ưu nếu chưa có chứng nhận.
- [ ] Thống nhất cách xử lý thời gian khởi tạo và giới hạn thời gian. GA của C hiện luôn hoàn tất khởi tạo, nên có thể vượt ngân sách; cần xem xét khi so sánh.
- [ ] Ghi nhận rằng ngân sách theo thời gian có thể tạo kết quả khác nhau dù dùng cùng seed.

## 4. Kết quả, phân tích và kiểm định

- [ ] Thống nhất tệp kết quả thô chứa ít nhất: thể hiện, thuật toán, seed, ngân sách, tham số, chi phí, thời gian, tính hợp lệ và trạng thái chạy.
- [ ] Lưu lời giải và log hội tụ cho từng lần chạy; thống nhất tên tệp và định nghĩa số lần đánh giá giữa các thuật toán.
- [ ] Tổng hợp best, trung bình, độ lệch chuẩn, thời gian trung bình và gap so với tối ưu/BKS. Với thể hiện nhỏ, báo cáo tỉ lệ đạt tối ưu.
- [ ] Nếu không có tối ưu/BKS, thống nhất giá trị tham chiếu và ghi rõ nguồn hoặc cách xác định; không gọi giá trị tốt nhất của nhóm là tối ưu.
- [ ] Vẽ đường hội tụ các thuật toán trên cùng thể hiện và cùng thang đo; D thống nhất cách lấy dữ liệu và số lần chạy được biểu diễn.
- [ ] Mỗi thành viên phân tích độ nhạy tham số metaheuristic phụ trách. Chốt tập tham số, dữ liệu, seed và ngân sách; tránh dùng tập đánh giá cuối để chọn tham số mà không ghi rõ.
- [ ] D đề xuất kiểm định Wilcoxon hoặc Friedman phù hợp thiết kế so sánh; thống nhất đơn vị ghép cặp, giả thuyết và cách báo cáo.

## 5. Bàn giao và mốc thời gian

| Đầu việc | Phụ trách | Thời hạn thống nhất | Trạng thái |
|---|---|---|---|
| Danh mục và nguồn dữ liệu chuẩn | Nhóm phân công | Chưa chốt | Chưa hoàn thành |
| Bộ sinh và dữ liệu tự sinh | B | Chưa chốt | Chưa hoàn thành |
| Mốc tối ưu cho dữ liệu nhỏ | A | Chưa chốt | Chưa hoàn thành |
| Chạy và phân tích GA, GA lai | C | Chưa chốt | Chưa hoàn thành |
| Script tổng hợp, biểu đồ, kiểm định | D | Chưa chốt | Chưa hoàn thành |
| Ghép báo cáo, rà soát và demo | Cả nhóm phối hợp | Chưa chốt | Chưa hoàn thành |

## 6. Biên bản cần điền sau họp

- Ngày họp và thành viên tham dự:
- Danh sách thể hiện và nguồn:
- Máy, ngân sách, seed và tham số đã chốt:
- Quy ước tệp kết quả và nơi lưu:
- Người phụ trách, thời hạn và phụ thuộc:
- Câu hỏi cần giảng viên xác nhận:
- Ngày kiểm tra tiến độ tiếp theo:
