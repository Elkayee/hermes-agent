# don_dep_kho.py
# Don dep cac tep rac va tam thoi o thu muc goc cua repo

import os
import shutil
from pathlib import Path

# 1. Xac dinh duong dan goc
goc = Path(__file__).resolve().parent

# 2. Danh sach cac tep rac / tam thoi can don dep o thu muc goc
ds_tep = [
    "bang_dieu_khien_gui.py",
    "bao_cao_sau_don_dep.py",
    "bo_chay_harness_don_gian.py",
    "chay_harness_song_song.py",
    "chuyen_giao_tinh_hoa.py",
    "don_dep_repo_hermes.py",
    "ket_qua_danh_gia_agy.json",
    "ket_qua_harness_song_song.json",
    "kiem_tra_hoat_dong_harness.py",
    "mo_phong_luong_prompt_agy.py",
    "tap_kiem_thu_mau.jsonl",
    "tap_kiem_thu_nang_cao.jsonl",
    "trien_khai_harness_agy.py",
    "tu_dong_danh_gia_sinh_skill.py",
    "tu_dong_tao_skill.py",
    "vong_lap_agent_harness.py",
    "kiem_tra_memory_context.py"
]

def don_dep():
    # Thu muc luu tru gom cac file tam
    tm_luu = goc / "_luu_tru_tam"
    tm_luu.mkdir(exist_ok=True)
    
    dem = 0
    for ten in ds_tep:
        tep = goc / ten
        if tep.exists() and tep != Path(__file__):
            # Di chuyen tep vao thu muc luu tru
            dich = tm_luu / ten
            shutil.move(str(tep), str(dich))
            print(f"[+] Da gom: {ten} -> _luu_tru_tam/")
            dem += 1
            
    print(f"\n[*] Tong so tep tam da duoc don dep: {dem}")
    print(f"[*] Thu muc goc da duoc tra lai su gon gang!")

if __name__ == "__main__":
    don_dep()
