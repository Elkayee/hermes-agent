# kich_hoat_harness_tu_dong.py
# Script chay tu dong qua PreInvocation Hook moi khi AGY nhan prompt tu nguoi dung

import os
import sys
import json
import time
from pathlib import Path

# Dam bao ma hoa UTF-8 tren Windows
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass


def xu_ly_kich_hoat_harness():
    """Doc payload tu stdin cua AGY va tra ve thong diep dieu phoi kem Memory Context."""
    xau_dau_vao = ""
    du_lieu = {}

    # 1. Doc du lieu stdin do AGY truyen vao
    try:
        if not sys.stdin.isatty():
            xau_dau_vao = sys.stdin.read()
            if xau_dau_vao.strip():
                du_lieu = json.loads(xau_dau_vao)
    except Exception:
        du_lieu = {}

    ma_phien = du_lieu.get("conversationId", "phien_chua_ro")
    so_luot = du_lieu.get("invocationNum", 1)

    # 2. Dinh tuyen va lua chon skill tu dong
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    chi_thi_skills = ""
    ten_skill_chon = "find-skills"
    try:
        from bo_dinh_tuyen_skills import dinh_tuyen_skills
        chi_thi_skills, ten_skill_chon = dinh_tuyen_skills(du_lieu)
    except Exception as loi_dt:
        chi_thi_skills = f"[!] Loi dinh tuyen skills: {str(loi_dt)}"

    # 3. Duong dan vao nhat ky harness
    tm_agents = Path(__file__).resolve().parent.parent
    tep_nk = tm_agents / "nhat_ky_harness.jsonl"

    ban_ghi = {
        "thoi_gian": round(time.time(), 2),
        "thoi_diem": time.strftime("%H:%M:%S %d/%m/%Y"),
        "ma_phien": ma_phien,
        "so_luot": so_luot,
        "trang_thai": "DA_KICH_HOAT",
        "skill_kich_hoat": ten_skill_chon
    }

    try:
        with open(tep_nk, "a", encoding="utf-8") as f:
            f.write(json.dumps(ban_ghi, ensure_ascii=False) + "\n")
    except Exception:
        pass

    # 4. Tu dong dong bo ngu canh va kich hoat Smart Recall tu Brain
    xau_hoi_tuong = ""
    try:
        from dong_bo_context_tu_dong import doc_yeu_cau_gan_nhat_tu_transcript, cap_nhat_context_md
        from bo_nao_nang_cao_hermes import nang_cap_toan_dien
        duong_dan_ts = du_lieu.get("transcriptPath", "")
        ds_yc = doc_yeu_cau_gan_nhat_tu_transcript(duong_dan_ts)
        if ds_yc:
            cap_nhat_context_md(ma_phien, ds_yc)
            _, xau_hoi_tuong = nang_cap_toan_dien(ds_yc[-1])
    except Exception:
        pass

    # 5. Nap khoi <memory-context> tu bo dieu phoi bo nho
    khoi_nho = ""
    try:
        from bo_dieu_phoi_bo_nho import tao_khoi_memory_context
        khoi_nho = tao_khoi_memory_context()
    except Exception as loi:
        khoi_nho = f"[!] Khong the nap memory context: {str(loi)}"

    # 6. Hop nhat thong diep Harness, Skills Router, Memory Context va Smart Recall
    thong_bao_harness = (
        "[HARNESS TRIGGERED]: Quy trinh thuc thi tu dong da duoc kich hoat.\n"
        "Yeu cau: 1) Kiem tra loi tung buoc; 2) Dung cong cu toi thieu; "
        "3) Tu kiem chung ket qua truoc khi phan hoi nguoi dung."
    )

    cac_phan = [thong_bao_harness]
    if chi_thi_skills:
        cac_phan.append(chi_thi_skills)
    if xau_hoi_tuong:
        cac_phan.append(xau_hoi_tuong)
    if khoi_nho:
        cac_phan.append(khoi_nho)

    thong_diep_tong = "\n\n".join(cac_phan)

    phan_hoi_hook = {
        "injectSteps": [
            {
                "ephemeralMessage": thong_diep_tong
            }
        ]
    }

    # 5. Xuat ra stdout theo dung hop dong cua AGY Hook
    print(json.dumps(phan_hoi_hook, ensure_ascii=False))


if __name__ == "__main__":
    xu_ly_kich_hoat_harness()
