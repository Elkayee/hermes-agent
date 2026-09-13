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

# Cac mau cau nhan dien nguoi dung dang ra quy tac / so thich moi
CAC_MAU_QUY_TAC = [
    # Mau ra lenh / Chi thi thoi gian
    r"(?:từ giờ|sau này|từ nay|lần sau)\s+(?:hãy|luôn|phải|đừng|không được|chú ý|cần|nên)\s+(.+)",
    r"quy tắc\s*(?:mới|là|bắt buộc|cần nhớ)?\s*[:\-]?\s*(.+)",
    r"(?:nhớ|ghi nhớ)\s+(?:rằng|là|kỹ|giúp|cho)\s+(.+)",
    r"luôn\s+(?:dùng|sử dụng|áp dụng|tránh|viết|giải thích|làm|tuân thủ|ưu tiên)\s+(.+)",
    r"(?:tuyệt đối|bắt buộc)\s+(?:không|phải|không được|cấm|chỉ|tránh|tuân thủ)\s+(.+)",
    r"không được\s+(?:dùng|phép|tự ý|sửa|xóa|push|chạy)\s+(.+)",
    r"đừng\s+(?:bao giờ|tự ý|dùng|sử dụng)\s+(.+)",
    r"(?:chú ý|lưu ý|yêu cầu)\s*(?:là)?\s*[:\-]?\s*(.+)",
    # Mau dinh chinh / Sua sai tu phan hoi cua user
    r"sửa lại\s*(?:là|thành)?\s*[:\-]?\s*(.+)",
    r"không phải\s+.*?(?:,\s*mà là|\s*mà phải là|\s*nhưng là)\s+(.+)",
    # Mau Tieng Anh
    r"(?:from now on|always|never|do not|don't|make sure to|remember to|rule is|keep in mind)\s+(.+)",
    r"(?:preference|guideline|instruction)\s*[:\-]\s*(.+)"
]


def phan_loai_danh_muc_quy_tac(dong_noi_dung):
    """Phan loai noi dung quy tac vao nhom tuong ung de de theo doi."""
    van_ban = dong_noi_dung.lower()
    if any(k in van_ban for k in ["code", "biến", "hàm", "class", "viết", "ngôn ngữ", "python", "rust", "java", "file", "tệp", "struct", "type", "method"]):
        return "Quy tắc Lập trình"
    if any(k in van_ban for k in ["giải thích", "ngắn gọn", "chi tiết", "tiếng việt", "format", "markdown", "bảng", "trả lời", "nói"]):
        return "Phong cách Trả lời"
    if any(k in van_ban for k in ["git", "push", "commit", "origin", "upstream", "cấm", "xóa", "terminal", "lệnh", "remote"]):
        return "Quy tắc Git & An toàn"
    if any(k in van_ban for k in ["port", "cổng", "gateway", "context", "engine", "harness", "server", "mcp", "service"]):
        return "Kiến trúc Hệ thống"
    return "Chỉ thị Chung"


def kiem_tra_trung_lap_ngu_nghia(dong_moi, noi_dung_cu):
    """Kiem tra xem quy tac moi da co noi dung tuong tu trong USER.md chua (tranh spam)."""
    if not noi_dung_cu:
        return False
    if dong_moi.lower() in noi_dung_cu.lower():
        return True

    # So khop tap tu khoa co nghia (do dai >= 3)
    tu_moi = set(w.lower() for w in re.findall(r"\w+", dong_moi) if len(w) >= 3)
    if not tu_moi:
        return False

    for dong in noi_dung_cu.splitlines():
        dong_s = dong.strip()
        if not dong_s or dong_s.startswith("#"):
            continue
        tu_dong = set(w.lower() for w in re.findall(r"\w+", dong_s) if len(w) >= 3)
        if not tu_dong:
            continue
        do_trung = len(tu_moi & tu_dong) / max(len(tu_moi), 1)
        if do_trung >= 0.8:  # Trung tren 80% tu khoa thi xem la trung lap
            return True
    return False


def lam_sach_dong_quy_tac(dong_tho):
    """Lam sach va chuan hoa van phong cua quy tac."""
    s = dong_tho.strip().rstrip(".,;!?")
    s = re.sub(r"^(nhớ là|từ giờ|sau này|quy tắc là|lưu ý là|chú ý là)\s*", "", s, flags=re.IGNORECASE).strip()
    if s:
        s = s[0].upper() + s[1:]
    return s


def hoc_so_thich_nguoi_dung(xau_yc):
    """Tu dong nhan dien khi nguoi dung dua ra quy tac/so thich moi de luu vao USER.md."""
    if not xau_yc:
        return False

    dong_moi = ""
    for mau in CAC_MAU_QUY_TAC:
        khop = re.search(mau, xau_yc, re.IGNORECASE)
        if khop:
            dong_moi = khop.group(1).strip()
            break

    if not dong_moi or len(dong_moi) < 6:
        return False

    dong_chuan = lam_sach_dong_quy_tac(dong_moi)
    if len(dong_chuan) < 6:
        return False

    # Doc noi dung cu de tranh trung lap
    nd_cu = TEP_USER.read_text(encoding="utf-8", errors="ignore") if TEP_USER.exists() else ""
    if kiem_tra_trung_lap_ngu_nghia(dong_chuan, nd_cu):
        return False

    danh_muc = phan_loai_danh_muc_quy_tac(dong_chuan)
    thoi_diem = time.strftime("%d/%m/%Y")
    dong_ghi = f"- [{danh_muc} - Ghi nhận {thoi_diem}]: {dong_chuan}\n"

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
