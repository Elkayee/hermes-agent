# harness_kiem_thu_hermes_context_memory.py
# Bo Harness kiem thu va danh gia Context & Memory theo tieu chuan Hermes cho AGY

import os
import sys
import time
import json
from pathlib import Path

# Thiet lap UTF-8 tranh loi ky tu tren console Windows
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

# 1. Duong dan goc
tm_goc = Path(__file__).resolve().parent.parent
tm_agents = tm_goc / ".agents"
tm_scripts = tm_agents / "scripts"
tm_nho = tm_agents / "memory"

# Nhan vien dieu phoi bo nho
sys.path.insert(0, str(tm_scripts))
try:
    from bo_dieu_phoi_bo_nho import (
        tao_khoi_memory_context,
        lam_sach_va_gioi_han_ngu_canh,
        GIOI_HAN_KY_TU,
        KY_TU_DAU,
        KY_TU_CUOI,
        DAU_CAT
    )
except ImportError as loi:
    print(f"[!] Loi khong tim thay bo_dieu_phoi_bo_nho: {str(loi)}")
    sys.exit(1)


# 2. Cac bai kiem thu cua bo Harness (Hermes Evaluation Test Cases)

def bai_1_kiem_tra_cau_truc_rao_chan():
    """Kiem tra khoi <memory-context> dung tieu chuan Hermes."""
    xau = tao_khoi_memory_context()
    co_mo = "<memory-context>" in xau
    co_dong = "</memory-context>" in xau
    co_ghi_chu = "[System note: The following is recalled memory context" in xau
    dat = co_mo and co_dong and co_ghi_chu
    return {
        "ten": "Kiem tra rao chan <memory-context>",
        "dat": dat,
        "chi_tiet": f"Co the mo: {co_mo}, Co the dong: {co_dong}, Co system note: {co_ghi_chu}"
    }


def bai_2_kiem_tra_nen_ngu_canh_hermes():
    """Kiem tra bo loc Context Engine thu gon du lieu vuot nguong 6000 ky tu."""
    # Tao chuoi van ban gia lap dai 10,000 ky tu
    xau_dai = "A" * 5000 + "---GIUA---" + "B" * 5000
    xau_nen = lam_sach_va_gioi_han_ngu_canh(xau_dai)
    
    co_cat = DAU_CAT in xau_nen
    do_dai_dung = len(xau_nen) <= (KY_TU_DAU + len(DAU_CAT) + KY_TU_CUOI)
    giu_dau = xau_nen.startswith("A" * 100)
    giu_cuoi = xau_nen.endswith("B" * 100)
    
    dat = co_cat and do_dai_dung and giu_dau and giu_cuoi
    return {
        "ten": "Kiem tra nen Context Engine (Head 4000, Tail 1500)",
        "dat": dat,
        "chi_tiet": f"Do dai sau nen: {len(xau_nen)} ky tu (Goc: {len(xau_dai)}), Co dau cat: {co_cat}"
    }


def bai_3_kiem_tra_phan_tang_bo_nho():
    """Kiem tra 3 tang bo nho doc lap: USER, MEMORY va CONTEXT."""
    tep_u = tm_nho / "USER.md"
    tep_m = tm_nho / "MEMORY.md"
    tep_c = tm_nho / "CONTEXT.md"
    
    co_u = tep_u.exists() and len(tep_u.read_text(encoding="utf-8")) > 0
    co_m = tep_m.exists() and len(tep_m.read_text(encoding="utf-8")) > 0
    co_c = tep_c.exists() and len(tep_c.read_text(encoding="utf-8")) > 0
    
    dat = co_u and co_m and co_c
    return {
        "ten": "Kiem tra 3 tang bo nho (USER, MEMORY, CONTEXT)",
        "dat": dat,
        "chi_tiet": f"USER.md: {'OK' if co_u else 'Thieu'}, MEMORY.md: {'OK' if co_m else 'Thieu'}, CONTEXT.md: {'OK' if co_c else 'Thieu'}"
    }


def bai_4_kiem_tra_toc_do_thuc_thi_hook():
    """Kiem tra toc do tao memory context dam bao khong gay tre (< 0.5s)."""
    tg_dau = time.perf_counter()
    for _ in range(50):
        _ = tao_khoi_memory_context()
    tg_tong = time.perf_counter() - tg_dau
    tg_tb = (tg_tong / 50) * 1000 # miligiay
    
    dat = tg_tb < 100 # Phai duoi 100ms
    return {
        "ten": "Kiem tra toc do phan hoi (Benchmark Latency)",
        "dat": dat,
        "chi_tiet": f"Thoi gian trung binh: {tg_tb:.2f} ms/lan goi (Gioi han < 100ms)"
    }


def bai_5_kiem_tra_hop_dong_hook_agy():
    """Kiem tra script hook kich_hoat_harness_tu_dong tra ve dung dinh dang JSON."""
    tep_hk = tm_scripts / "kich_hoat_harness_tu_dong.py"
    co_hk = tep_hk.exists()
    
    import subprocess
    kq = subprocess.run(
        [sys.executable, str(tep_hk)],
        input="{}",
        capture_output=True,
        text=True,
        encoding="utf-8",
        timeout=10
    )
    
    hop_le = False
    co_ephemeral = False
    try:
        du_lieu = json.loads(kq.stdout.strip())
        cac_buoc = du_lieu.get("injectSteps", [])
        if cac_buoc and "ephemeralMessage" in cac_buoc[0]:
            hop_le = True
            co_ephemeral = "<memory-context>" in cac_buoc[0]["ephemeralMessage"]
    except Exception:
        pass
        
    dat = co_hk and (kq.returncode == 0) and hop_le and co_ephemeral
    return {
        "ten": "Kiem tra hop dong PreInvocation Hook cho AGY",
        "dat": dat,
        "chi_tiet": f"Returncode: {kq.returncode}, JSON chuan: {hop_le}, Chuyen memory vao ephemeralMessage: {co_ephemeral}"
    }


# 3. Ham dieu phoi chay toan bo bo Harness
def chay_toan_bo_harness():
    print("================================================================================")
    print("      HERMES HARNESS KIEM THU CONTEXT VA MEMORY CHO AGY (ANTIGRAVITY)")
    print("================================================================================\n")
    
    ds_bai = [
        bai_1_kiem_tra_cau_truc_rao_chan,
        bai_2_kiem_tra_nen_ngu_canh_hermes,
        bai_3_kiem_tra_phan_tang_bo_nho,
        bai_4_kiem_tra_toc_do_thuc_thi_hook,
        bai_5_kiem_tra_hop_dong_hook_agy
    ]
    
    dem_pass = 0
    tong_so = len(ds_bai)
    
    for i, ham in enumerate(ds_bai, 1):
        kq = ham()
        trang_thai = "[ PASS ]" if kq["dat"] else "[ FAIL ]"
        if kq["dat"]:
            dem_pass += 1
            
        print(f"Bai {i}: {trang_thai} - {kq['ten']}")
        print(f"       Chi tiet: {kq['chi_tiet']}\n")
        
    print("--------------------------------------------------------------------------------")
    print(f"KET QUA HARNESS: {dem_pass}/{tong_so} bai kiem thu dat yeu cau ({(dem_pass/tong_so)*100:.1f}%).")
    print("================================================================================")


if __name__ == "__main__":
    chay_toan_bo_harness()
