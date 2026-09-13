---
name: kiem-thu-harness
description: Bo khung thuc thi danh gia va kiem thu (Harness) tu dong danh cho AGY. Dung khi nguoi dung muon chay tap kiem thu, benchmark toc do, do luong token hoac kiem thu hoi quy cac nhiem vu.
---

# Kiem Thu Harness Skill cho AGY

Skill nay cung cap bo khung Harness danh gia va benchmark tu dong cho AGY voi cac tinh nang:
1. Doc tap du lieu kiem thu tu tep JSONL.
2. Thuc thi song song da luong thong qua `agy.exe` o che do khong can tuong tac (`--print`).
3. Thu thap thong so token chi tiet (input, output, thinking, cache) va uoc tinh chi phi.
4. Kiem tra ket qua pass/fail va xuat bao cao JSON tong hop.

## Cach su dung

Chay bo harness kiem thu song song bang lenh:

```powershell
python chay_harness_song_song.py
```

Ket qua se duoc ghi vao tep `ket_qua_harness_song_song.json`.
