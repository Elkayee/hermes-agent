# bo_chay_harness_don_gian.py
# Bo khung chay danh gia (Harness) toi gian tich hop voi AGY

import json
import time
import subprocess
from pathlib import Path


def doc_ds_nhiem_vu(duong_dan_tep):
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


def chay_mot_nhiem_vu(nv, thu_muc_lam_viec="."):
    """Gui nhiem vu den agy va do thoi gian chay."""
    ma_nv = nv.get("id", "khong_ma")
    cau_hoi = nv.get("prompt", "")
    kq_mong_doi = nv.get("expected", "")

    tg_bat_dau = time.time()

    # Lenh chay agy o che do khong can hop thoai (headless / exec)
    lenh = ["agy", "exec", cau_hoi]

    try:
        tien_trinh = subprocess.run(
            lenh,
            cwd=thu_muc_lam_viec,
            capture_output=True,
            text=True,
            encoding="utf-8",
            timeout=120
        )
        xau_tra_ve = tien_trinh.stdout
        ma_loi = tien_trinh.returncode
    except Exception:
        xau_tra_ve = ""
        ma_loi = -1

    tg_chay = round(time.time() - tg_bat_dau, 2)

    # Kiem tra ket qua dat hay khong dat
    dat = (ma_loi == 0) and (kq_mong_doi in xau_tra_ve if kq_mong_doi else True)

    kq = {
        "id": ma_nv,
        "thoi_gian": tg_chay,
        "ma_loi": ma_loi,
        "dat": dat,
        "xau_ra": xau_tra_ve[:500]
    }
    return kq


def chay_toan_bo_harness(tep_dau_vao, tep_bao_cao):
    """Dieu phoi chay toan bo harness va ghi tong ket."""
    ds_nv = doc_ds_nhiem_vu(tep_dau_vao)
    ds_kq = []
    dem_dat = 0
    tong_so = len(ds_nv)

    for nv in ds_nv:
        kq = chay_mot_nhiem_vu(nv)
        if kq["dat"]:
            dem_dat += 1
        ds_kq.append(kq)

    tong_ket = {
        "tong_so": tong_so,
        "so_dat": dem_dat,
        "ti_le": round((dem_dat / tong_so) * 100, 2) if tong_so > 0 else 0,
        "chi_tiet": ds_kq
    }

    with open(tep_bao_cao, "w", encoding="utf-8") as f:
        json.dump(tong_ket, f, ensure_ascii=False, indent=2)

    return tong_ket


if __name__ == "__main__":
    tep_nv = "nhiem_vu_mau.jsonl"
    tep_kq = "ket_qua_danh_gia.json"

    # Tao tep nhiem vu mau neu chua co
    if not Path(tep_nv).exists():
        du_lieu_mau = [
            {"id": "nv_01", "prompt": "In ra Hello World", "expected": "Hello World"}
        ]
        with open(tep_nv, "w", encoding="utf-8") as f:
            for muc in du_lieu_mau:
                f.write(json.dumps(muc, ensure_ascii=False) + "\n")

    tk = chay_toan_bo_harness(tep_nv, tep_kq)
    print(f"Tong: {tk['tong_so']}, Dat: {tk['so_dat']}, Ti le: {tk['ti_le']}%")
