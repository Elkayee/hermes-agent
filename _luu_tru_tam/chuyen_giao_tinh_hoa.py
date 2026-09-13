# chuyen_giao_tinh_hoa.py
# Trich xuat va chuyen giao toan bo cac ky nang tinh hoa cua Hermes vao AGY

import os
import sys
import shutil
from pathlib import Path

# Dam bao hien thi tieng Viet tren Windows
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

# Danh sach cac ky nang tinh hoa nhat cua Hermes can chuyen sang AGY
DS_SKILL_TINH_HOA = [
    ("systematic-debugging", "software-development/systematic-debugging"),
    ("test-driven-development", "software-development/test-driven-development"),
    ("codebase-inspection", "software-development/codebase-inspection"),
    ("simplify-code", "software-development/simplify-code")
]


def chuyen_giao_skills():
    """Sao chep cac skill tinh hoa tu Hermes sang thu muc .agents/skills cua AGY."""
    duong_dan_goc = Path(__file__).resolve().parent
    tm_nguon = duong_dan_goc / "skills"
    tm_dich = duong_dan_goc / ".agents" / "skills"
    tm_dich.mkdir(parents=True, exist_ok=True)

    print("================ CHUYEN GIAO TINH HOA SANG AGY ================")
    dem_thanh_cong = 0

    for ten_moi, duong_dan_con in DS_SKILL_TINH_HOA:
        tm_goc = tm_nguon / duong_dan_con
        tm_den = tm_dich / ten_moi

        if tm_goc.exists():
            try:
                # Sao chep toan bo thu muc skill bao gom SKILL.md va scripts
                if tm_den.exists():
                    shutil.rmtree(tm_den)
                shutil.copytree(tm_goc, tm_den)
                print(f"[+] Da chuyen giao thanh cong: '{ten_moi}'")
                dem_thanh_cong += 1
            except Exception as loi:
                print(f"[-] Loi khi chuyen '{ten_moi}': {str(loi)}")
        else:
            print(f"[-] Khong tim thay skill goc tai: {tm_goc}")

    print("---------------------------------------------------------------")
    print(f"[*] Tong so ky nang tinh hoa da duoc tich hop vao AGY: {dem_thanh_cong}")
    print(f"[*] Toan bo luu tai: {tm_dich}")
    return dem_thanh_cong


if __name__ == "__main__":
    chuyen_giao_skills()
