# Wayfinder Map: hermes-matt-pocock-pipeline

## Notes
Triển khai và vận hành chuỗi quy trình Matt Pocock trong Hermes Harness.

## Decisions So Far
- [01-router-bilingual-dictionary](issues/01-router-bilingual-dictionary.md): Sử dụng NFD Unicode Normalization để hỗ trợ tiếng Việt có dấu trong Router.
- [02-scaffold-auto-detection](issues/02-scaffold-auto-detection.md): Dùng cấu hình Local Markdown tại `.scratch/` làm bộ issue tracker mặc định để không phụ thuộc vào kết nối mạng và GitHub API.

## Fog
- Cần xây dựng logic auto-claim và auto-resolve khi kết thúc mỗi lượt invocation.
