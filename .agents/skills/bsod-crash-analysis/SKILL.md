---
name: bsod-crash-analysis
description: Chuyên phân tích tệp memory.dmp khi Windows gặp sự cố màn hình xanh (BSOD) sử dụng WinDbg và xuất báo cáo.
---

# Kỹ Năng: Phân Tích Sự Cố Windows BSOD Crash

## Mục Tiêu
Cung cấp quy trình từng bước tải ký hiệu (Symbols), nạp dump và chạy lệnh !analyze -v để tìm driver gây lỗi.

## Quy Trình
1. Nạp tệp dump vào WinDbg: `windbg -z C:\Windows\MEMORY.DMP`.
2. Thiết lập symbol server: `.sympath srv*https://msdl.microsoft.com/download/symbols`.
3. Chạy phân tích tự động: `!analyze -v`.
4. Trích xuất tên MODULE_NAME và FAILURE_BUCKET_ID.
