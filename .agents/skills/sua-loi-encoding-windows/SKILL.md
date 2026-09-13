---
name: sua-loi-encoding-windows
description: Tu dong sua loi charmap cp1252 khi xuat tieng Viet ra console tren Windows.
---

# Kỹ Năng Tu Dong Sinh: sua-loi-encoding-windows

## Boi Canh Tich Luy
- So buoc thuc thi: 4
- Kinh nghiem sua loi: Co
- Phan loai: debug

## Quy Trinh
1. Kiem tra sys.platform == 'win32'.\n2. Goi sys.stdout.reconfigure(encoding='utf-8', errors='replace').
