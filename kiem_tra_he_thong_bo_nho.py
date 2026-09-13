# kiem_tra_he_thong_bo_nho.py
# Kiem tra toan dien he thong Memory Context va Git Remote cua repo AGY

import sys
import subprocess
from pathlib import Path

# Dam bao hien thi tieng Viet tren Windows
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

# 1. Duong dan goc va cac thu muc can kiem tra
goc = Path(__file__).resolve().parent
tm_nho = goc / ".agents" / "memory"
tep_dieu_phoi = goc / ".agents" / "scripts" / "bo_dieu_phoi_bo_nho.py"


def kiem_tra_git_remote():
    """Kiem tra xem git remote da duoc go bo hoan toan chua."""
    lenh = ["git", "remote", "-v"]
    kq = subprocess.run(lenh, capture_output=True, text=True, cwd=goc)
    ds_remote = kq.stdout.strip()
    
    print("================ 1. KIEM TRA GIT REMOTE ================")
    if not ds_remote:
        print("[+] THANH CONG: Khong con git remote nao (origin da duoc go bo hoan toan).")
    else:
        print(f"[-] CANH BAO: Van con remote:\n{ds_remote}")


def kiem_tra_cac_tep_bo_nho():
    """Kiem tra su ton tai cua cac tep bo nho cot loi."""
    print("\n================ 2. KIEM TRA TEP BO NHO ================")
    ds_tep = ["USER.md", "MEMORY.md", "CONTEXT.md"]
    dem = 0
    for ten in ds_tep:
        duong_dan = tm_nho / ten
        if duong_dan.exists():
            kb = round(duong_dan.stat().st_size / 1024, 2)
            print(f"[+] Tep '{ten:<12}': CO MAT ({kb} KB)")
            dem += 1
        else:
            print(f"[-] Tep '{ten:<12}': CHUA CO")
    print(f"[*] Tong so tep bo nho san sang: {dem}/{len(ds_tep)}")


def kiem_tra_ghi_va_xuat_memory():
    """Kiem tra kha nang ghi va xuat khoi <memory-context>."""
    print("\n================ 3. KIEM TRA KHOI MEMORY-CONTEXT ================")
    if not tep_dieu_phoi.exists():
        print(f"[-] Khong tim thay script dieu phoi tai: {tep_dieu_phoi}")
        return

    # Chay script lay khoi memory
    kq = subprocess.run([sys.executable, str(tep_dieu_phoi)], capture_output=True, text=True, cwd=goc)
    xau_xuat = kq.stdout.strip()
    
    co_the_mo = "<memory-context>" in xau_xuat
    co_the_dong = "</memory-context>" in xau_xuat
    co_user = "USER PROFILE" in xau_xuat
    co_mem = "PROJECT LONG-TERM MEMORY" in xau_xuat
    co_ctx = "ACTIVE SESSION CONTEXT" in xau_xuat

    print(f"[+] The mo <memory-context>    : {'CO' if co_the_mo else 'KHONG'}")
    print(f"[+] The dong </memory-context> : {'CO' if co_the_dong else 'KHONG'}")
    print(f"[+] Chua ho so USER            : {'CO' if co_user else 'KHONG'}")
    print(f"[+] Chua bo nho MEMORY         : {'CO' if co_mem else 'KHONG'}")
    print(f"[+] Chua ngu canh CONTEXT      : {'CO' if co_ctx else 'KHONG'}")
    
    if co_the_mo and co_the_dong:
        print("[+] HE THONG MEMORY CONTEXT CHO AGY: HOAT DONG HOAN HAO!")
    else:
        print("[-] HE THONG MEMORY CONTEXT: GAP LOI!")


if __name__ == "__main__":
    kiem_tra_git_remote()
    kiem_tra_cac_tep_bo_nho()
    kiem_tra_ghi_va_xuat_memory()
