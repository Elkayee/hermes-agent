# don_dep_repo_hermes.py
# Script don dep toan bo cac thanh phan thua cua Hermes, chi giu lai Harness va AGY

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

# Danh sach cac thu muc "mo thua" khong dung den
DS_THU_MUC_XOA = [
    "apps",             # Electron desktop app
    "ui-tui",           # React Ink TUI terminal
    "gateway",          # Cac bot Telegram, Discord, Slack
    "tui_gateway",      # Backend TUI JSON-RPC
    "web",              # Web dashboard SPA
    "website",          # Tai lieu Docusaurus
    "cron",             # Bo lap lich tac vu cron
    "docker",           # Cac tep Docker build
    "nix",              # Cac tep cau hinh NixOS
    "contributors",     # Danh sach cong tac vien
    "assets",           # Hinh anh minh hoa
    "tests-js",         # Kiem thu giao dien JavaScript
    "plugin-catalog",   # Kho plugin ben ngoai
    "plugins",          # Cac plugin mac dinh cua Hermes
    "locales",          # Da ngon ngu cua giao dien
    "mcp-research-data" # Du lieu nghien cuu cu
]


def tinh_dung_luong_thu_muc(duong_dan_tm):
    """Tinh tong dung luong byte cua mot thu muc."""
    tong_byte = 0
    tm = Path(duong_dan_tm)
    if not tm.exists():
        return 0
    for can_tep, _, ds_ten_tep in os.walk(tm):
        for ten in ds_ten_tep:
            duong_dan_tep = os.path.join(can_tep, ten)
            try:
                tong_byte += os.path.getsize(duong_dan_tep)
            except Exception:
                pass
    return tong_byte


def quet_va_don_dep(co_thuc_thi=False):
    """Quet cac thu muc thua va thuc hien don dep."""
    duong_dan_goc = Path(__file__).resolve().parent
    tong_dung_luong_xoa = 0
    ds_thuc_te_can_xoa = []

    print("================ KIEM TRA VA DON DEP REPO ================")
    for ten_tm in DS_THU_MUC_XOA:
        tm_muc_tieu = duong_dan_goc / ten_tm
        if tm_muc_tieu.exists() and tm_muc_tieu.is_dir():
            dung_luong = tinh_dung_luong_thu_muc(tm_muc_tieu)
            tong_dung_luong_xoa += dung_luong
            dung_luong_mb = round(dung_luong / (1024 * 1024), 2)
            ds_thuc_te_can_xoa.append((tm_muc_tieu, dung_luong_mb))
            print(f"[-] Tim thay thu muc thua: {ten_tm:<20} ({dung_luong_mb:>7} MB)")

    tong_mb = round(tong_dung_luong_xoa / (1024 * 1024), 2)
    print("----------------------------------------------------------")
    print(f"[*] Tong so thu muc can don dep: {len(ds_thuc_te_can_xoa)}")
    print(f"[*] Tong dung luong se giai phong: {tong_mb} MB")

    if not co_thuc_thi:
        print("\n[!] Che do mo phong (Dry-run). Chua co gi bi xoa.")
        print("[!] De xoa that su, hay truyen them doi so: --thuc-thi")
        return

    # Thuc hien xoa that su
    print("\n[!] DANG THUC HIEN XOA CAC THU MUC THUA...")
    for tm, mb in ds_thuc_te_can_xoa:
        try:
            shutil.rmtree(tm, ignore_errors=True)
            print(f"    [OK] Da xoa: {tm.name} ({mb} MB)")
        except Exception as loi:
            print(f"    [LOI] Khong the xoa {tm.name}: {str(loi)}")

    print(f"\n[+] HOAN TAT DON DEP! Da giai phong ~{tong_mb} MB dung luong.")
    print("[+] Repo hien chi con lai: .agents (Harness), bo khung benchmark va script AGY.")


if __name__ == "__main__":
    thuc_thi = "--thuc-thi" in sys.argv
    quet_va_don_dep(co_thuc_thi=thuc_thi)
