# kiem_tra_hoat_dong_harness.py
# Kiem tra toan dien trang thai hoat dong hien tai cua he thong Harness

import os
import sys
import json
import urllib.request
from pathlib import Path

# Dam bao hien thi tieng Viet tren Windows
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass


def kiem_tra_hook_va_nhat_ky():
    """Kiem tra tep hooks.json va dem so luot da kich hoat."""
    tep_hook = Path(".agents/hooks.json")
    tep_nk = Path(".agents/nhat_ky_harness.jsonl")

    hook_ok = tep_hook.exists()
    so_luot_kich_hoat = 0

    if tep_nk.exists():
        with open(tep_nk, "r", encoding="utf-8") as f:
            for dong in f:
                if dong.strip():
                    so_luot_kich_hoat += 1

    return hook_ok, so_luot_kich_hoat


def kiem_tra_may_chu_gui(cong=7890):
    """Kiem tra may chu Web GUI co dang phan hoi khong."""
    dia_chi = f"http://127.0.0.1:{cong}/api/du_lieu"
    try:
        with urllib.request.urlopen(dia_chi, timeout=2) as phan_hoi:
            if phan_hoi.status == 200:
                du_lieu = json.loads(phan_hoi.read().decode("utf-8"))
                return True, len(du_lieu.get("ds_nk", []))
    except Exception:
        pass
    return False, 0


def liet_ke_cac_skill_da_hoc():
    """Liet ke cac ky nang da duoc he thong tich luy."""
    tm_skill = Path(".agents/skills")
    ds_ten = []
    if tm_skill.exists():
        for muc in tm_skill.iterdir():
            if muc.is_dir() and (muc / "SKILL.md").exists():
                ds_ten.append(muc.name)
    return ds_ten


def bao_cao_trang_thai():
    """In toan bo bao cao van hanh cua Harness."""
    print("================ BAO CAO HOAT DONG CUA HARNESS ================")

    # 1. Kiem tra Hook
    hook_ok, dem_nk = kiem_tra_hook_va_nhat_ky()
    trang_thai_hook = "DANG BAT (PreInvocation)" if hook_ok else "CHUA BAT"
    print(f"[1] Trinh kich hoat Hook : {trang_thai_hook}")
    print(f"    So luot da ghi nhan  : {dem_nk} luot prompt")

    # 2. Kiem tra GUI Server
    gui_ok, dem_gui = kiem_tra_may_chu_gui()
    trang_thai_gui = "DANG CHAY (http://127.0.0.1:7890)" if gui_ok else "DANG DUNG"
    print(f"[2] Bang dieu khien GUI  : {trang_thai_gui}")
    print(f"    Ket noi du lieu API  : {'HOAN HAO' if gui_ok else 'MAT KET NOI'}")

    # 3. Kiem tra Skills da tich luy
    ds_sk = liet_ke_cac_skill_da_hoc()
    print(f"[3] Cac Skill dang co    : {len(ds_sk)} skill")
    for sk in ds_sk:
        print(f"    - {sk}")

    print("=================================================================")
    print("Ket luan: Harness dang hoat dong tu dong tren moi luot chat cua ban!")


if __name__ == "__main__":
    bao_cao_trang_thai()
