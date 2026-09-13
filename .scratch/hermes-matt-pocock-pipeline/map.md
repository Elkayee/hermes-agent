# Wayfinder Map: hermes-matt-pocock-pipeline

## Notes
Triển khai và vận hành chuỗi quy trình Matt Pocock trong Hermes Harness.

## Decisions So Far
- [01-router-bilingual-dictionary](issues/01-router-bilingual-dictionary.md): Sử dụng NFD Unicode Normalization để hỗ trợ tiếng Việt có dấu trong Router.
- [02-scaffold-auto-detection](issues/02-scaffold-auto-detection.md): Dùng cấu hình Local Markdown tại `.scratch/` làm bộ issue tracker mặc định để không phụ thuộc vào kết nối mạng và GitHub API.
- [03-wayfinder-and-ticket-tracking](issues/03-wayfinder-and-ticket-tracking.md): Xây dựng `bo_dieu_phoi_tickets.py` qua quy trình TDD Red -> Green, tự động quét frontier ticket và cập nhật trạng thái.

## Fog
- Feature hoàn tất 100%. Toàn bộ 3 tickets đã chuyển sang trạng thái resolved.

