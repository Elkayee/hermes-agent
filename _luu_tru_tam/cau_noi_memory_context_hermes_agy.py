# cau_noi_memory_context_hermes_agy.py
# Cau noi dong bo Memory va Context giua Hermes Agent va AGY (Antigravity)

import os
import sys
import json
from pathlib import Path

# Dam bao hien thi ky tu tieng Viet tren terminal Windows
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

# 1. Ham lay duong dan thu muc cua Hermes va AGY
def lay_duong_dan_kho():
    tm_nha = Path.home()
    
    # Thu muc memory cua Hermes
    tm_hermes = tm_nha / ".hermes" / "memories"
    
    # Thu muc luu tru quy tac va bo nho cua AGY
    tm_agy = tm_nha / ".gemini" / "antigravity-cli"
    
    return tm_hermes, tm_agy

# 2. Ham doc bo nho cua Hermes (USER.md va MEMORY.md)
def doc_bo_nho_hermes(tm_hermes):
    du_lieu = {
        "nguoi_dung": "",
        "tri_thuc": ""
    }
    
    tep_user = tm_hermes / "USER.md"
    tep_mem = tm_hermes / "MEMORY.md"
    
    if tep_user.exists():
        du_lieu["nguoi_dung"] = tep_user.read_text(encoding="utf-8", errors="ignore")
        
    if tep_mem.exists():
        du_lieu["tri_thuc"] = tep_mem.read_text(encoding="utf-8", errors="ignore")
        
    return du_lieu

# 3. Ham tao khoi bo nho dong bo sang dinh dang Rule cua AGY
def chuyen_doi_sang_quy_tac_agy(du_lieu_hermes):
    xau = "# BỘ NHỚ ĐỒNG BỘ TỪ HERMES AGENT\n\n"
    
    nd_user = du_lieu_hermes.get("nguoi_dung", "").strip()
    nd_tri_thuc = du_lieu_hermes.get("tri_thuc", "").strip()
    
    if nd_user:
        xau += "## 1. Hồ sơ & Sở thích người dùng (USER.md)\n"
        for dong in nd_user.splitlines():
            if dong.strip():
                xau += f"- {dong.strip()}\n"
        xau += "\n"
        
    if nd_tri_thuc:
        xau += "## 2. Kiến thức & Ngữ cảnh dài hạn (MEMORY.md)\n"
        for dong in nd_tri_thuc.splitlines():
            if dong.strip():
                xau += f"- {dong.strip()}\n"
        xau += "\n"
        
    return xau

# 4. Ham doc va trich xuat log hoi thoai (Context) tu AGY de dong bo sang Hermes
def trich_xuat_ngu_canh_agy(tm_agy, conv_id):
    ds_tin = []
    tep_log = tm_agy / "brain" / conv_id / ".system_generated" / "logs" / "transcript.jsonl"
    
    if not tep_log.exists():
        return ds_tin
        
    with open(tep_log, "r", encoding="utf-8", errors="ignore") as f:
        for dong in f:
            dong_str = dong.strip()
            if not dong_str:
                continue
            try:
                muc = json.loads(dong_str)
                vai_tro = muc.get("source", "system")
                nd = muc.get("content", "")
                if nd:
                    ds_tin.append({
                        "vai_tro": vai_tro,
                        "noi_dung": nd[:200]  # Thu gon de tiet kiem bo nho
                    })
            except Exception:
                continue
                
    return ds_tin

# 5. Ham chay kiem tra toan bo luong ket noi
def chay_kiem_tra_cau_noi():
    print("=== KIEM TRA CAU NOI CONTEXT & MEMORY: HERMES <--> AGY ===")
    
    tm_hermes, tm_agy = lay_duong_dan_kho()
    print(f"1. Duong dan Hermes Memories : {tm_hermes}")
    print(f"   - Ton tai                 : {tm_hermes.exists()}")
    
    print(f"2. Duong dan AGY Core        : {tm_agy}")
    print(f"   - Ton tai                 : {tm_agy.exists()}")
    
    # Doc bo nho hien tai
    du_lieu = doc_bo_nho_hermes(tm_hermes)
    co_nd_user = len(du_lieu["nguoi_dung"]) > 0
    co_nd_mem = len(du_lieu["tri_thuc"]) > 0
    print(f"3. Trang thai du lieu Hermes :")
    print(f"   - USER.md                 : {'Co du lieu' if co_nd_user else 'Chua co hoac trong'}")
    print(f"   - MEMORY.md               : {'Co du lieu' if co_nd_mem else 'Chua co hoac trong'}")
    
    # Tao ban xem truoc chuyen doi sang AGY
    xau_quy_tac = chuyen_doi_sang_quy_tac_agy(du_lieu)
    dem_dong = len(xau_quy_tac.splitlines())
    print(f"4. Chuyen doi sang Rule AGY   : Da sinh ra {dem_dong} dong quy tac")
    
    # Kiem tra thu muc brain cua AGY
    tm_brain = tm_agy / "brain"
    if tm_brain.exists():
        ds_phien = [p.name for p in tm_brain.iterdir() if p.is_dir()]
        print(f"5. So luong phien chat AGY    : {len(ds_phien)} phien da ghi nhan")
    else:
        print(f"5. Thu muc brain cua AGY      : Chua khoi tao")
        
    print("===========================================================")

if __name__ == "__main__":
    chay_kiem_tra_cau_noi()
