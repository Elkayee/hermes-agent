# toi_uu_brain_hermes.py
# Bo cong cu toi uu hoa va khai thac du lieu tu thu muc brain/ cua AGY dua tren Hermes Context Engine

import os
import sys
import json
import sqlite3
import time
from pathlib import Path

# Thiet lap UTF-8 cho Windows console
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

# 1. Cac duong dan goc
TM_BRAIN = Path(r"C:\Users\Home33\.gemini\antigravity-cli\brain")
TEP_DB = Path(r"C:\Users\Home33\.gemini\antigravity-cli\conversation_summaries.db")
TM_MEMORY = Path(r"C:\Tools\hermes-agent\.agents\memory")
TEP_MEMORY_MD = TM_MEMORY / "MEMORY.md"


def phan_tich_kho_brain():
    """Thong ke toan dien ve so luong phien, tep tin va dung luong trong thu muc brain."""
    if not TM_BRAIN.exists():
        print("[-] Thu muc brain khong ton tai.")
        return {}

    dem_phien = 0
    dem_tep = 0
    tong_byte = 0
    dem_steps = 0

    for muc in TM_BRAIN.iterdir():
        if muc.is_dir():
            dem_phien += 1
            for goc, _, cac_tep in os.walk(muc):
                for tep in cac_tep:
                    dem_tep += 1
                    duong_dan_tep = Path(goc) / tep
                    try:
                        sz = duong_dan_tep.stat().st_size
                        tong_byte += sz
                        if "steps" in str(duong_dan_tep) or tep == "output.txt":
                            dem_steps += 1
                    except Exception:
                        pass

    tong_mb = round(tong_byte / (1024 * 1024), 2)
    print("================ PHAN TICH DU LIEU BRAIN AGY ================")
    print(f"• Tong so phien lam viec (sessions) : {dem_phien}")
    print(f"• Tong so tep tin luu tru          : {dem_tep:,} tep")
    print(f"• Tong so tep steps/output rac     : {dem_steps:,} tep")
    print(f"• Tong dung luong chiem dung       : {tong_mb} MB")
    print("=============================================================")
    return {
        "so_phien": dem_phien,
        "so_tep": dem_tep,
        "so_steps": dem_steps,
        "tong_mb": tong_mb
    }


def thu_hoach_tri_thuc_tu_brain(gioi_han_phien=10):
    """Doc database tong ket va transcript de trich xuat tri thuc vao MEMORY.md."""
    if not TEP_DB.exists():
        print("[-] Khong tim thay database conversation_summaries.db")
        return False

    print(f"[*] Dang thu hoach tri thuc tu {gioi_han_phien} phien lam viec gan nhat...")
    ds_tri_thuc = []

    try:
        kn = sqlite3.connect(str(TEP_DB))
        cs = kn.cursor()
        cs.execute(
            "SELECT conversation_id, title, preview, step_count, last_modified_time "
            "FROM conversation_summaries "
            "WHERE title != '' AND title != 'New Chat' AND step_count > 5 "
            "ORDER BY last_modified_time DESC LIMIT ?",
            (gioi_han_phien,)
        )
        ds_hang = cs.fetchall()
        kn.close()

        for hang in ds_hang:
            ma_ph, tieu_de, xem_truoc, so_buoc, thoi_gian = hang
            ds_tri_thuc.append({
                "ma_ph": ma_ph,
                "tieu_de": tieu_de,
                "xem_truoc": xem_truoc,
                "so_buoc": so_buoc,
                "thoi_gian": str(thoi_gian)[:19] if thoi_gian else ""
            })
    except Exception as loi:
        print(f"[-] Loi khi truy van database: {str(loi)}")
        return False

    if not ds_tri_thuc:
        print("[-] Khong co phien lam viec nao du dieu kien de thu hoach.")
        return False

    # Chuyen thanh van ban nén cho MEMORY.md
    ds_dong = []
    for tt in ds_tri_thuc:
        dong = f"- [{tt['tieu_de']}] (Phiên: {tt['ma_ph'][:8]}, {tt['so_buoc']} bước): {tt['xem_truoc']}"
        ds_dong.append(dong)

    noi_dung_tri_thuc = "\n".join(ds_dong)
    thoi_diem = time.strftime("%H:%M:%S %d/%m/%Y")

    khoi_cap_nhat = f"""
### Tri Thuc Thu Hoach Tu Brain (Cap nhat {thoi_diem}):
{noi_dung_tri_thuc}
"""

    # Ghi vao MEMORY.md
    try:
        nd_cu = TEP_MEMORY_MD.read_text(encoding="utf-8", errors="ignore") if TEP_MEMORY_MD.exists() else ""
        if "### Tri Thuc Thu Hoach Tu Brain" in nd_cu:
            # Thay the phan cu
            nd_moi = nd_cu.split("### Tri Thuc Thu Hoach Tu Brain")[0].strip() + "\n" + khoi_cap_nhat.strip() + "\n"
        else:
            nd_moi = nd_cu.strip() + "\n" + khoi_cap_nhat.strip() + "\n"

        TEP_MEMORY_MD.write_text(nd_moi, encoding="utf-8")
        print(f"[+] DA THU HOACH THANH CONG: {len(ds_tri_thuc)} chu de quan trong vao MEMORY.md!")
        print(f"    Vi tri luu: {TEP_MEMORY_MD}")
        return True
    except Exception as loi:
        print(f"[-] Loi khi ghi vao MEMORY.md: {str(loi)}")
        return False


def don_dep_rac_brain(giu_lai_phien_gan_nhat=5, chi_kiem_tra=True):
    """Don dep cac tep output.txt lon trong steps/ cua cac phien cu de tiet kiem o dia."""
    if not TM_BRAIN.exists():
        return

    # Lay danh sach tat ca phien sap xep theo thoi gian sua doi gan nhat
    ds_tm = []
    for tm in TM_BRAIN.iterdir():
        if tm.is_dir():
            try:
                ds_tm.append((tm.stat().st_mtime, tm))
            except Exception:
                pass

    ds_tm.sort(key=lambda x: x[0], reverse=True)
    phien_can_don = ds_tm[giu_lai_phien_gan_nhat:]

    print(f"\n[*] Dang quet {len(phien_can_don)} phien cu (giu nguyen {giu_lai_phien_gan_nhat} phien moi nhat)...")
    dem_xoa = 0
    dung_luong_giai_phong = 0

    for _, tm in phien_can_don:
        tm_steps = tm / ".system_generated" / "steps"
        if tm_steps.exists():
            for goc, _, cac_tep in os.walk(tm_steps):
                for tep in cac_tep:
                    if tep.endswith(".txt"):
                        tep_duong_dan = Path(goc) / tep
                        try:
                            sz = tep_duong_dan.stat().st_size
                            dem_xoa += 1
                            dung_luong_giai_phong += sz
                            if not chi_kiem_tra:
                                tep_duong_dan.unlink(missing_ok=True)
                        except Exception:
                            pass

    mb_tiet_kiem = round(dung_luong_giai_phong / (1024 * 1024), 2)
    che_do = "[MO PHONG]" if chi_kiem_tra else "[DA THUC HIEN]"
    print(f"{che_do} Tim thay {dem_xoa:,} tep output.txt tam thoi.")
    print(f"{che_do} Dung luong co the thu hoi: {mb_tiet_kiem} MB (Van giu 100% transcript.jsonl & artifacts).")


def main():
    print("=============================================================")
    print("   HERMES CONTEXT ENGINE - TOI UU HOA VA THU HOACH BRAIN     ")
    print("=============================================================\n")

    # 1. Phan tich hien trang
    phan_tich_kho_brain()

    # 2. Thu hoach tri thuc tu cac phien cu vao MEMORY.md
    print()
    thu_hoach_tri_thuc_tu_brain(gioi_han_phien=10)

    # 3. Mo phong don dep rac output.txt trong steps/
    print()
    don_dep_rac_brain(giu_lai_phien_gan_nhat=10, chi_kiem_tra=True)


if __name__ == "__main__":
    main()
