# Spec: Tự Động Kích Hoạt và Vận Hành Bộ Engineering Skills Matt Pocock

## 1. Mục tiêu (Goal)
Tích hợp trọn vẹn bộ 14 kỹ năng kỹ thuật của Matt Pocock vào Hermes Harness và AGY CLI, cho phép tự động nhận diện ý định (intent-based auto-routing) qua cả tiếng Việt và tiếng Anh, tự động điều phối ticket và quản lý vòng đời phát triển phần mềm theo mô hình tracer-bullet vertical slicing.

## 2. Các Thành Phần Chính
- **Router Từ Điển & Chuẩn Hóa Tiếng Việt**: So khớp từ khóa không phân biệt hoa thường và dấu tiếng Việt (NFD Unicode Normalization).
- **Trình Quản Lý Ticket Cục Bộ (`.scratch/`)**: Mỗi ticket là một tệp markdown độc lập tại `.scratch/<feature>/issues/<NN>-<slug>.md`, khai báo rõ ràng các phụ thuộc chặn (`Blocked by:`).
- **Bộ Nhãn Triage 5 Vai Trò**: `needs-triage`, `needs-info`, `ready-for-agent`, `ready-for-human`, `wontfix`.
- **Hồi Tưởng & Phản Biện (Grilling & Retro)**: Kích hoạt `grill-me` trước khi code và `retro` sau khi hoàn thành.
