# trien_khai_harness_agy.py
# Bo khung danh gia va kiem thu (Harness) chuyen biet cho AGY

import os
import sys
import json
import time
import shutil
import subprocess
from pathlib import Path

# Thiet lap ma hoa UTF-8 cho console Windows tranh loi charmap
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass


def tim_duong_dan_agy():
    """Tim duong dan thuc thi cua agy tren may."""
    duong_dan_mac_dinh = r"C:\Users\Home33\AppData\Local\agy\bin\agy.exe"
    if os.path.exists(duong_dan_mac_dinh):
        return duong_dan_mac_dinh
    tim_thay = shutil.which("agy")
    return tim_thay if tim_thay else "agy"


def doc_tap_nhiem_vu(duong_dan_tep):
    """Doc danh sach cac bai kiem thu tu tep JSONL."""
    ds_nv = []
    tep = Path(duong_dan_tep)
    if not tep.exists():
        return ds_nv

    with open(tep, "r", encoding="utf-8") as f:
        for dong in f:
            xau_dong = dong.strip()
            if xau_dong:
                nv = json.loads(xau_dong)
                ds_nv.append(nv)
    return ds_nv


def chay_mot_bai_kiem_thu(nv, duong_dan_agy, thu_muc_lam_viec="."):
    """Giao bai toan cho agy xu ly va thu thap so lieu."""
    ma_nv = nv.get("id", "khong_ma")
    cau_hoi = nv.get("prompt", "")
    kq_mong_doi = str(nv.get("expected", "")).strip()

    tg_bat_dau = time.time()

    # Lenh goi agy voi dinh dang JSON de lay metrics
    lenh = [
        duong_dan_agy,
        "-p", cau_hoi,
        "--output-format", "json",
        "--effort", "low"
    ]

    xau_tra_ve = ""
    du_lieu_json = {}
    ma_loi = 0

    try:
        tien_trinh = subprocess.run(
            lenh,
            cwd=thu_muc_lam_viec,
            capture_output=True,
            text=True,
            encoding="utf-8",
            timeout=90
        )
        xau_tra_ve = tien_trinh.stdout
        ma_loi = tien_trinh.returncode
        if xau_tra_ve.strip():
            du_lieu_json = json.loads(xau_tra_ve.strip())
    except subprocess.TimeoutExpired:
        ma_loi = -2
    except Exception:
        ma_loi = -1

    tg_chay = round(time.time() - tg_bat_dau, 2)

    # Phan tich phan hoi tu du lieu JSON cua agy
    phan_hoi = du_lieu_json.get("response", "").strip() if du_lieu_json else xau_tra_ve.strip()
    so_luong_token = du_lieu_json.get("usage", {}).get("total_tokens", 0)
    so_vong_lap = du_lieu_json.get("num_turns", 0)

    # Kiem tra tieu chi vuot qua (pass / fail)
    dat = False
    if ma_loi == 0:
        if not kq_mong_doi:
            dat = True
        elif kq_mong_doi.lower() in phan_hoi.lower():
            dat = True

    kq = {
        "id": ma_nv,
        "dat": dat,
        "thoi_gian": tg_chay,
        "ma_loi": ma_loi,
        "so_token": so_luong_token,
        "so_luot": so_vong_lap,
        "phan_hoi": phan_hoi[:300]
    }
    return kq


def thuc_thi_harness(tep_dau_vao, tep_xuat_bao_cao):
    """Dieu phoi chay toan bo harness va in thong so."""
    duong_dan_agy = tim_duong_dan_agy()
    ds_nv = doc_tap_nhiem_vu(tep_dau_vao)
    ds_kq = []
    dem_dat = 0
    tong_token = 0
    tong_so = len(ds_nv)

    print(f"[*] Bat dau chay Harness voi {tong_so} nhiem vu qua AGY...")
    print(f"[*] Trinh thuc thi: {duong_dan_agy}\n")

    for i, nv in enumerate(ds_nv, start=1):
        print(f"-> Dang chay [{i}/{tong_so}]: {nv.get('id')} - {nv.get('prompt')[:40]}...")
        kq = chay_mot_bai_kiem_thu(nv, duong_dan_agy)
        ds_kq.append(kq)

        if kq["dat"]:
            dem_dat += 1
            print(f"   [PASS] {kq['thoi_gian']}s | Tokens: {kq['so_token']} | Tra ve: {kq['phan_hoi'][:50]}")
        else:
            print(f"   [FAIL] {kq['thoi_gian']}s | Ma loi: {kq['ma_loi']} | Tra ve: {kq['phan_hoi'][:50]}")

        tong_token += kq["so_token"]

    ti_le = round((dem_dat / tong_so) * 100, 2) if tong_so > 0 else 0.0

    bao_cao = {
        "tong_so": tong_so,
        "so_dat": dem_dat,
        "ti_le_dat": ti_le,
        "tong_token": tong_token,
        "chi_tiet": ds_kq
    }

    with open(tep_xuat_bao_cao, "w", encoding="utf-8") as f:
        json.dump(bao_cao, f, ensure_ascii=False, indent=2)

    print("\n================ TONG KET HARNESS ================")
    print(f"Tong so nhiem vu : {tong_so}")
    print(f"So luong dat     : {dem_dat}")
    print(f"Ti le thanh cong : {ti_le}%")
    print(f"Tong token tieu thu: {tong_token}")
    print(f"Bao cao luu tai  : {tep_xuat_bao_cao}")
    print("==================================================")
    return bao_cao


if __name__ == "__main__":
    tep_nv = "tap_kiem_thu_mau.jsonl"
    tep_bc = "ket_qua_danh_gia_agy.json"

    # Tao bo test case mau neu chua ton tai
    danh_sach_mau = [
        {
            "id": "TC_01_TOAN_HOC",
            "prompt": "Tinh gia tri: 125 * 8 bang bao nhieu? Chi tra loi duy nhat con so.",
            "expected": "1000"
        },
        {
            "id": "TC_02_THU_DO",
            "prompt": "Thu do cua Viet Nam la gi? Chi tra loi dung ten thanh pho.",
            "expected": "Hà Nội"
        }
    ]

    with open(tep_nv, "w", encoding="utf-8") as f:
        for muc in danh_sach_mau:
            f.write(json.dumps(muc, ensure_ascii=False) + "\n")

    thuc_thi_harness(tep_nv, tep_bc)
