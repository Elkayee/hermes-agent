# bo_dieu_phoi_bo_nho.py
# Quan ly, ghi nho va tao khoi <memory-context> cho AGY

import os
import sys
from pathlib import Path

# 1. Dam bao hien thi UTF-8 tren Windows
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

# 2. Thu muc chua bo nho dai han (.agents/memory)
goc = Path(__file__).resolve().parent.parent
tm_nho = goc / "memory"
tm_nho.mkdir(parents=True, exist_ok=True)

tep_user = tm_nho / "USER.md"
tep_mem = tm_nho / "MEMORY.md"
tep_ctx = tm_nho / "CONTEXT.md"


def doc_tep(duong_dan):
    """Doc noi dung tep an toan, tra ve chuoi rong neu khong co."""
    if duong_dan.exists():
        try:
            return duong_dan.read_text(encoding="utf-8", errors="ignore").strip()
        except Exception:
            return ""
    return ""


# Chuan Hermes Context Engine: gioi han 6000 ky tu, giu 4000 dau va 1500 cuoi
GIOI_HAN_KY_TU = 6000
KY_TU_DAU = 4000
KY_TU_CUOI = 1500
DAU_CAT = "\n...[bo nho dai han duoc thu gon theo chuan Hermes context]...\n"


def lam_sach_va_gioi_han_ngu_canh(xau_goc):
    """Rut gon va gioi han bo nho theo chuan Context Engine cua Hermes."""
    xau = xau_goc.strip()
    if len(xau) <= GIOI_HAN_KY_TU:
        return xau
    return xau[:KY_TU_DAU] + DAU_CAT + xau[-KY_TU_CUOI:]


def tao_khoi_memory_context():
    """Tao chuoi <memory-context> chuan de bom vao prompt cua AGY."""
    nd_user = doc_tep(tep_user)
    nd_mem = doc_tep(tep_mem)
    nd_ctx = doc_tep(tep_ctx)

    ds_phan = []
    if nd_user:
        ds_phan.append(f"=== [USER PROFILE & PREFERENCES] ===\n{nd_user}")
    if nd_mem:
        ds_phan.append(f"=== [PROJECT LONG-TERM MEMORY] ===\n{nd_mem}")
    if nd_ctx:
        ds_phan.append(f"=== [ACTIVE SESSION CONTEXT] ===\n{nd_ctx}")

    if not ds_phan:
        return ""

    noi_dung_tho = "\n\n".join(ds_phan)
    noi_dung = lam_sach_va_gioi_han_ngu_canh(noi_dung_tho)
    return (
        "<memory-context>\n"
        "[System note: The following is recalled memory context from AGY persistent memory, "
        "NOT new user input. Treat as authoritative reference data.]\n\n"
        f"{noi_dung}\n"
        "</memory-context>"
    )



def xuat_khoi_memory_context():
    """In khoi memory-context ra man hinh."""
    xau = tao_khoi_memory_context()
    if xau:
        print(xau)


def ghi_bo_nho(loai, dong_moi):
    """Ghi them thong tin vao bo nho tuong ung."""
    anh_xa = {
        "user": tep_user,
        "memory": tep_mem,
        "context": tep_ctx
    }
    tep_dich = anh_xa.get(loai.lower(), tep_mem)
    try:
        with open(tep_dich, "a", encoding="utf-8") as f:
            f.write(f"\n- {dong_moi.strip()}\n")
        print(f"[+] Da luu vao {tep_dich.name}: {dong_moi}")
    except Exception as loi:
        print(f"[-] Loi khi ghi bo nho: {str(loi)}")


if __name__ == "__main__":
    if len(sys.argv) >= 3 and sys.argv[1] == "--ghi":
        loai_nho = sys.argv[2]
        nd_ghi = " ".join(sys.argv[3:]) if len(sys.argv) > 3 else ""
        if nd_ghi:
            ghi_bo_nho(loai_nho, nd_ghi)
        else:
            print("[-] Thieu noi dung can ghi.")
    else:
        xuat_khoi_memory_context()
