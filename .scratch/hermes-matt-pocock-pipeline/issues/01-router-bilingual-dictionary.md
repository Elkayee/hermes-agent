# Issue 01: Nâng cấp Router song ngữ và chuẩn hóa tiếng Việt

Status: resolved
Type: task
Blocked by: none

## Context
Người dùng cần gọi các kỹ năng như `to-tickets`, `to-spec`, `grill-me`, `retro` bằng tiếng Việt có dấu. Hệ thống router cũ không có từ điển và không chuẩn hóa dấu.

## Scope
- Bổ sung 14 skills của Matt Pocock vào `TU_DIEN_NHOM`.
- Thêm hàm `bo_dau_tieng_viet` dùng `unicodedata.normalize('NFD')`.
- Viết test suite `kiem_tra_skills_matt_pocock.py`.

## Verification
- Đã chạy 11 test cases với kết quả 11/11 (100% SUCCESS).
- Đã commit và push vào `origin/main` (`67f42234d6`).
