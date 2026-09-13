# bo_nao_nang_cao_hermes.py
# Nang cap hoan thien: Hoi tuong thong minh (Smart Recall) va Tu dong hoc so thich (Auto Preference Learning)

import os
import sys
import json
import sqlite3
import re
import time
from pathlib import Path

# Thiet lap UTF-8 cho Windows console
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

# Cac duong dan goc
TM_GOC = Path(__file__).resolve().parent.parent
TM_NHO = TM_GOC / "memory"
TEP_USER = TM_NHO / "USER.md"
TEP_MEM = TM_NHO / "MEMORY.md"
TEP_CTX = TM_NHO / "CONTEXT.md"
TEP_DB = Path(r"C:\Users\Home33\.gemini\antigravity-cli\conversation_summaries.db")

# Cac mau cau nhan dien nguoi dung dang ra quy tac moi
CAC_MAU_QUY_TAC = [
    r"từ giờ\s+(?:hãy|luôn|phải|không được)\s+(.+)",
    r"quy tắc\s*(?:mới|là)\s*:\s*(.+)",
    r"nhớ\s+(?:rằng|là)\s+(.+)",
    r"luôn\s+(?:dùng|sử dụng|áp dụng|tránh)\s+(.+)"
]


def hoc_so_thich_nguoi_dung(xau_yc):
    """Tu dong nhan dien khi nguoi dung dua ra quy tac/so thich moi de luu vao USER.md."""
    if not xau_yc:
        return False

    dong_moi = ""
    for mau in CAC_MAU_QUY_TAC:
        khop = re.search(mau, xau_yc, re.IGNORECASE)
        if khop:
            dong_moi = khop.group(0).strip()
            break

    if not dong_moi:
        return False

    # Doc noi dung cu de tranh trung lap
    nd_cu = TEP_USER.read_text(encoding="utf-8", errors="ignore") if TEP_USER.exists() else ""
    if dong_moi.lower() in nd_cu.lower():
        return False

    # Ghi them vao USER.md
    thoi_diem = time.strftime("%d/%m/%Y")
    dong_ghi = f"- [Tu dong ghi nhan {thoi_diem}]: {dong_moi}\n"
    try:
        with open(TEP_USER, "a", encoding="utf-8") as f:
            f.write(dong_ghi)
        return True
    except Exception:
        return False


def hoi_tuong_tri_thuc_lien_quan(xau_yc, gioi_han=3):
    """Tim kiem thong minh cac phien lam viec cu co noi dung khop voi cau hoi hien tai."""
    if not xau_yc or not TEP_DB.exists():
        return ""

    # Tach cac tu khoa co y nghia (do dai >= 3)
    cac_tu = [t.lower() for t in re.findall(r"\w+", xau_yc) if len(t) >= 3]
    cac_tu_loc = [t for t in cac_tu if t not in ["lam", "sao", "nhu", "the", "nao", "cho", "cua", "cac", "nay", "duoc"]]

    if not cac_tu_loc:
        return ""

    ds_khop = []
    try:
        kn = sqlite3.connect(str(TEP_DB))
        cs = kn.cursor()
        cs.execute(
            "SELECT conversation_id, title, preview, step_count FROM conversation_summaries "
            "WHERE title != '' AND title != 'New Chat'"
        )
        ds_hang = cs.fetchall()
        kn.close()

        for hang in ds_hang:
            ma_ph, tieu_de, xem_truoc, so_buoc = hang
            van_ban_gop = f"{tieu_de} {xem_truoc}".lower()
            
            # Tinh diem khop tu khoa
            diem = 0
            for tu in cac_tu_loc:
                if tu in van_ban_gop:
                    diem += 1

            if diem > 0:
                ds_khop.append((diem, tieu_de, xem_truoc, ma_ph[:8], so_buoc))

        # Sap xep theo do khop tu khoa cao nhat
        ds_khop.sort(key=lambda x: x[0], reverse=True)
    except Exception:
        return ""

    if not ds_khop:
        return ""

    top_khop = ds_khop[:gioi_han]
    ds_dong = [f"• [{t[1]}] (Phiên {t[3]}): {t[2][:120]}..." for t in top_khop]
    xau_hoi_tuong = (
        "=== [HERMES RECALL: KINH NGHIEM LIEN QUAN TU BRAIN] ===\n" +
        "\n".join(ds_dong)
    )
    return xau_hoi_tuong


def nang_cap_toan_dien(xau_yc):
    """Chay dong thoi hoc so thich va hoi tuong tri thuc lien quan."""
    # 1. Thu nghiem hoc so thich
    da_ghi_so_thich = hoc_so_thich_nguoi_dung(xau_yc)

    # 2. Hoi tuong kinh nghiem cu
    xau_hoi_tuong = hoi_tuong_tri_thuc_lien_quan(xau_yc)

    return da_ghi_so_thich, xau_hoi_tuong


if __name__ == "__main__":
    cau_hoi_thu = "Lỗi build nhị phân ChatCmd và cấu hình MCP"
    ghi, ht = nang_cap_toan_dien(cau_hoi_thu)
    print("Ket qua hoi tuong kinh nghiem cu:")
    print(ht if ht else "Khong tim thay kinh nghiem cu tuong dong.")
