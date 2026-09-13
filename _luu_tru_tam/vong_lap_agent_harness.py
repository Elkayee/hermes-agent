# vong_lap_agent_harness.py
# Mo phong bo khung thuc thi (Execution Harness) - Trai tim van hanh cua mot Agent

import os
import sys
import json
import subprocess

# Dam bao hien thi tieng Viet tren Windows
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass


def thuc_thi_cong_cu_lenh(lenh_he_thong):
    """Cong cu thuc thi lenh tren he thong (Tool execution)."""
    try:
        tt = subprocess.run(
            lenh_he_thong,
            shell=True,
            capture_output=True,
            text=True,
            encoding="utf-8",
            timeout=30
        )
        return tt.stdout if tt.returncode == 0 else f"Loi: {tt.stderr}"
    except Exception as loi:
        return f"Ngoai le: {str(loi)}"


def mo_phong_goi_mo_hinh(ds_tin_nhan):
    """Mo phong phan hoi cua LLM kem theo yeu cau goi cong cu."""
    so_luong_tin = len(ds_tin_nhan)

    # Luot 1: Mo hinh quyet dinh goi cong cu xem thu muc
    if so_luong_tin == 2:
        return {
            "loai": "goi_cong_cu",
            "ten_cc": "thuc_thi_lenh",
            "tham_so": "dir /b" if sys.platform == "win32" else "ls"
        }

    # Luot 2: Mo hinh nhan ket qua va dua ra cau tra loi cuoi cung
    return {
        "loai": "tra_loi_cuoi",
        "noi_dung": "Toi da kiem tra xong thu muc va hoan thanh nhiem vu."
    }


def chay_vong_lap_harness(xau_yeu_cau, gioi_han_vong=5):
    """Vong lap thuc thi (Execution Harness) cot loi cua Agent."""
    print(f"[*] KHOI CHAY AGENT HARNESS VOI YEU CAU: '{xau_yeu_cau}'\n")

    # 1. Khoi tao lich su tro chuyen
    ds_tin = [
        {"vai_tro": "he_thong", "noi_dung": "Ban la tro ly AI co kha nang goi cong cu."},
        {"vai_tro": "nguoi_dung", "noi_dung": xau_yeu_cau}
    ]

    dem_vong = 0

    # 2. Vong lap ReAct: Suy nghi -> Goi cong cu -> Nhan ket qua -> Lap lai
    while dem_vong < gioi_han_vong:
        dem_vong += 1
        print(f"--- [VONG {dem_vong}] ---")

        # Buoc A: Goi mo hinh (Model Call)
        phan_hoi = mo_phong_goi_mo_hinh(ds_tin)

        # Buoc B: Neu mo hinh da hoan thanh -> Dung vong lap
        if phan_hoi["loai"] == "tra_loi_cuoi":
            print(f"[Agent]: {phan_hoi['noi_dung']}")
            return phan_hoi["noi_dung"]

        # Buoc C: Neu mo hinh yeu cau goi cong cu (Tool Call)
        if phan_hoi["loai"] == "goi_cong_cu":
            ten_cc = phan_hoi["ten_cc"]
            tham_so = phan_hoi["tham_so"]
            print(f"[Tool Call]: Goi '{ten_cc}' voi tham so '{tham_so}'")

            # Buoc D: Thuc thi cong cu trong moi truong thuc
            kq_cc = thuc_thi_cong_cu_lenh(tham_so)
            print(f"[Observation]: Ket qua tra ve ({len(kq_cc)} ky tu)")

            # Buoc E: Cap nhat ket qua vao lich su de mo hinh doc tiep
            ds_tin.append({"vai_tro": "tro_ly", "noi_dung": f"Goi {ten_cc}: {tham_so}"})
            ds_tin.append({"vai_tro": "cong_cu", "noi_dung": kq_cc})

    print("[!] Dat gioi han so vong lap toi da.")
    return "Khong the hoan thanh trong so vong cho phep."


if __name__ == "__main__":
    chay_vong_lap_harness("Liet ke cac tep trong thu muc hien tai")
