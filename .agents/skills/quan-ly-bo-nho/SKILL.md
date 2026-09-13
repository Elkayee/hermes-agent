---
name: quan-ly-bo-nho
description: Quan ly va cap nhat he thong bo nho dai han va ngu canh phien lam viec cua AGY (USER.md, MEMORY.md, CONTEXT.md). Dung khi can luu lai quy dinh, quyet dinh kien truc hoac tien trinh cong viec.
---

# Ky Nang Quan Ly Bo Nho & Ngu Canh Cho AGY

Ky nang nay giup AGY chu dong quan ly va cap nhat he thong Memory Context:

## 1. Cac Vung Bo Nho
- `user`: Ho so nguoi dung, quy tac lap trinh, phong cach lam viec (`.agents/memory/USER.md`).
- `memory`: Bo nho dai han du an, kien truc, bai hoc kinh nghiem (`.agents/memory/MEMORY.md`).
- `context`: Ngữ canh hien tai cua phien lam viec, cac task dang thuc hien (`.agents/memory/CONTEXT.md`).

## 2. Cach Ghi Nho Thong Tin Moi
Su dung script dieu phoi bo nho:

```powershell
python .agents/scripts/bo_dieu_phoi_bo_nho.py --ghi <user|memory|context> "<noi_dung_can_luu>"
```

## 3. Cach Doc Toan Bo Bo Nho
Chay script khong doi so de xuat toan bo khoi `<memory-context>`:

```powershell
python .agents/scripts/bo_dieu_phoi_bo_nho.py
```
