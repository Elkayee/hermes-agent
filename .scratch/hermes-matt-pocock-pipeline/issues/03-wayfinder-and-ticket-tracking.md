# Issue 03: Tự động điều phối và xử lý frontier tickets qua Wayfinder

Status: resolved
Type: task
Blocked by: 02

## Context
Khi có nhiều tickets trong `.scratch/`, Agent cần biết ticket nào đã giải quyết (`resolved`), ticket nào đang chờ (`ready-for-agent`), và thứ tự blocking edges để tự động pick ticket tiếp theo.

## Scope
- Xây dựng module quét thư mục `.scratch/<feature>/issues/`.
- Xác định frontier tickets (unblocked, unclaimed).
- Tự động chuyển trạng thái `claimed` khi bắt đầu và `resolved` khi hoàn thành.
