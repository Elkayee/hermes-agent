# tu_dong_danh_gia_sinh_skill.py
# Co che tu dong danh gia va tu dong sinh Skill khong can nguoi dung yeu cau

import os
import sys
import json
from pathlib import Path

# Dam bao hien thi tieng Viet tren Windows
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass


def kiem_tra_co_nen_sinh_skill(so_buoc_goi_tool, co_loi_da_sua, xau_loai_nhiem_vu):
    """Bo loc thong minh tranh sinh skill rac tran lan."""
    # Dieu kien 1: Phai la tac vu phuc tap (tu 3 buoc goi tool tro len)
    if so_buoc_goi_tool < 3:
        return False, "Tac vu qua don gian, khong can sinh skill."

    # Dieu kien 2: Co kinh nghiem sua loi hoac la quy trinh ky thuat dac thu
    if not (co_loi_da_sua or xau_loai_nhiem_vu in ["build", "debug", "pipeline", "deploy"]):
        return False, "Khong co tinh quy trinh tai su dung."

    return True, "Dat tieu chuan tu dong sinh skill."


def tu_dong_sinh_skill_neu_du_tieu_chuan(ten_skill, mo_ta, huong_dan, so_buoc, co_loi, loai_nv):
    """Tu dong thuc thi sinh skill neu thoa man tieu chi."""
    nen_sinh, ly_do = kiem_tra_co_nen_sinh_skill(so_buoc, co_loi, loai_nv)

    if not nen_sinh:
        print(f"[-] BO QUA: {ly_do}")
        return None

    # Chuan hoa ten thu muc
    ten_tm = ten_skill.strip().lower().replace(" ", "-")
    duong_dan_tm = Path(".agents/skills") / ten_tm
    duong_dan_tm.mkdir(parents=True, exist_ok=True)

    noi_dung = f"""---
name: {ten_tm}
description: {mo_ta}
---

# Kỹ Năng Tu Dong Sinh: {ten_skill}

## Boi Canh Tich Luy
- So buoc thuc thi: {so_buoc}
- Kinh nghiem sua loi: {'Co' if co_loi else 'Khong'}
- Phan loai: {loai_nv}

## Quy Trinh
{huong_dan}
"""
    tep_sk = duong_dan_tm / "SKILL.md"
    with open(tep_sk, "w", encoding="utf-8") as f:
        f.write(noi_dung.strip() + "\n")

    print(f"[+] HE THONG DA TU DONG SINH SKILL: '{ten_tm}'")
    print(f"[+] Tep duoc luu tai: {tep_sk}")
    return str(tep_sk)


if __name__ == "__main__":
    # Truong hop 1: Tac vu don gian (Hoi dap 1 buoc) -> Bo qua tu dong
    print("--- KIEM TRA TRUONG HOP 1 ---")
    tu_dong_sinh_skill_neu_du_tieu_chuan(
        ten_skill="phep-cong-don-gian",
        mo_ta="Cong hai so 1 + 1",
        huong_dan="Lay 1 cong 1 bang 2",
        so_buoc=1,
        co_loi=False,
        loai_nv="tinh-toan"
    )

    # Truong hop 2: Tac vu phuc tap vuot qua loi (Debug he thong 4 buoc) -> Tu dong sinh
    print("\n--- KIEM TRA TRUONG HOP 2 ---")
    tu_dong_sinh_skill_neu_du_tieu_chuan(
        ten_skill="sua-loi-encoding-windows",
        mo_ta="Tu dong sua loi charmap cp1252 khi xuat tieng Viet ra console tren Windows.",
        huong_dan="1. Kiem tra sys.platform == 'win32'.\\n2. Goi sys.stdout.reconfigure(encoding='utf-8', errors='replace').",
        so_buoc=4,
        co_loi=True,
        loai_nv="debug"
    )
