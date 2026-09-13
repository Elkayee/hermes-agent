# chay_harness_song_song.py
# Bo khung danh gia va kiem thu (Harness) song song chuyen biet cho AGY

import os
import sys
import json
import time
import shutil
import threading
import subprocess
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed

# Cau hinh bang ma UTF-8 cho Windows console
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

# Khoa chong xung dot khi in nhieu luong
khoa_in = threading.Lock()


def tim_duong_dan_agy():
    """Tim trinh thuc thi agy tren may."""
    duong_dan_mac_dinh = r"C:\Users\Home33\AppData\Local\agy\bin\agy.exe"
    if os.path.exists(duong_dan_mac_dinh):
        return duong_dan_mac_dinh
    tim_thay = shutil.which("agy")
    return tim_thay if tim_thay else "agy"


def doc_tap_nhiem_vu(duong_dan_tep):
    """Doc danh sach cac nhiem vu tu tep JSONL."""
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


def chay_mot_nhiem_vu(nv, duong_dan_agy, thu_muc_lam_viec="."):
    """Gui mot nhiem vu cho agy va bieu dien so lieu chi tiet."""
    ma_nv = nv.get("id", "khong_ma")
    cau_hoi = nv.get("prompt", "")
    kq_mong_doi = str(nv.get("expected", "")).strip()

    tg_bat_dau = time.time()

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

    # Phan tich phan hoi va chi tiet cac loai token
    phan_hoi = du_lieu_json.get("response", "").strip() if du_lieu_json else xau_tra_ve.strip()
    so_lieu_token = du_lieu_json.get("usage", {})

    token_vao = so_lieu_token.get("input_tokens", 0)
    token_ra = so_lieu_token.get("output_tokens", 0)
    token_suy_nghi = so_lieu_token.get("thinking_tokens", 0)
    token_cache = so_lieu_token.get("cache_read_tokens", 0)
    tong_token = so_lieu_token.get("total_tokens", 0)
    so_vong = du_lieu_json.get("num_turns", 0)

    # Uoc tinh chi phi ($/1M token mau: Vao $0.15, Ra $0.60)
    chi_phi = round(((token_vao * 0.15) + (token_ra * 0.60)) / 1_000_000, 6)

    # Danh gia ket qua
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
        "token_vao": token_vao,
        "token_ra": token_ra,
        "token_suy_nghi": token_suy_nghi,
        "token_cache": token_cache,
        "tong_token": tong_token,
        "chi_phi": chi_phi,
        "so_vong": so_vong,
        "phan_hoi": phan_hoi[:200]
    }

    # In thong tin dong bo an toan giua cac luong
    with khoa_in:
        trang_thai = "[PASS]" if dat else "[FAIL]"
        print(f"{trang_thai} {ma_nv:<16} | {tg_chay:>5}s | Token: {tong_token:>5} | CP: ${chi_phi:<8} | Tra ve: {phan_hoi[:40]}")

    return kq


def thuc_thi_harness_song_song(tep_dau_vao, tep_xuat_bao_cao, so_luong_luong=2):
    """Dieu phoi chay toan bo harness da luong song song."""
    duong_dan_agy = tim_duong_dan_agy()
    ds_nv = doc_tap_nhiem_vu(tep_dau_vao)
    ds_kq = []
    tong_so = len(ds_nv)

    print(f"[*] KHOI DONG HARNESS SONG SONG (So luong luong: {so_luong_luong})")
    print(f"[*] Tong so bai toan: {tong_so}")
    print(f"[*] Trinh thuc thi  : {duong_dan_agy}\n")
    print(f"{'Kq':<6} {'Ma NV':<16} | {'Thoi Gian':<8} | {'Tokens':<13} | {'Chi Phi':<11} | {'Phan Hoi'}")
    print("-" * 75)

    tg_toan_bo_bat_dau = time.time()

    with ThreadPoolExecutor(max_workers=so_luong_luong) as thuc_thi:
        cac_tac_vu = [
            thuc_thi.submit(chay_mot_nhiem_vu, nv, duong_dan_agy)
            for nv in ds_nv
        ]
        for tac_vu in as_completed(cac_tac_vu):
            kq = tac_vu.result()
            ds_kq.append(kq)

    tg_tong = round(time.time() - tg_toan_bo_bat_dau, 2)

    # Thong ke so lieu
    dem_dat = sum(1 for item in ds_kq if item["dat"])
    tong_token = sum(item["tong_token"] for item in ds_kq)
    tong_chi_phi = round(sum(item["chi_phi"] for item in ds_kq), 6)
    ti_le = round((dem_dat / tong_so) * 100, 2) if tong_so > 0 else 0.0

    bao_cao = {
        "tong_so": tong_so,
        "so_dat": dem_dat,
        "ti_le_dat": ti_le,
        "tong_thoi_gian": tg_tong,
        "tong_token": tong_token,
        "tong_chi_phi": tong_chi_phi,
        "chi_tiet": ds_kq
    }

    with open(tep_xuat_bao_cao, "w", encoding="utf-8") as f:
        json.dump(bao_cao, f, ensure_ascii=False, indent=2)

    print("-" * 75)
    print("================ TONG KET HARNESS SONG SONG ================")
    print(f"Tong so nhiem vu   : {tong_so}")
    print(f"So luong dat       : {dem_dat}")
    print(f"Ti le thanh cong   : {ti_le}%")
    print(f"Tong thoi gian chay: {tg_tong}s")
    print(f"Tong token tieu thu: {tong_token}")
    print(f"Uoc tinh chi phi   : ${tong_chi_phi}")
    print(f"Bao cao luu tai    : {tep_xuat_bao_cao}")
    print("============================================================")
    return bao_cao


if __name__ == "__main__":
    tep_nv = "tap_kiem_thu_nang_cao.jsonl"
    tep_bc = "ket_qua_harness_song_song.json"

    # Tao bo test case mau da dang
    danh_sach_mau = [
        {
            "id": "TC_01_TOAN",
            "prompt": "Giai phep tinh: 25 * 25 bang bao nhieu? Chi tra loi so.",
            "expected": "625"
        },
        {
            "id": "TC_02_THU_DO",
            "prompt": "Thu do cua Nhat Ban la gi? Chi tra loi ten thanh pho.",
            "expected": "Tokyo"
        },
        {
            "id": "TC_03_CODE",
            "prompt": "Viet mot ham Python ten la 'chao' tra ve 'hello'. Chi in ma ham khong giai thich.",
            "expected": "def chao"
        }
    ]

    with open(tep_nv, "w", encoding="utf-8") as f:
        for muc in danh_sach_mau:
            f.write(json.dumps(muc, ensure_ascii=False) + "\n")

    thuc_thi_harness_song_song(tep_nv, tep_bc, so_luong_luong=2)
