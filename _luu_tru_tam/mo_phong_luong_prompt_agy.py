# mo_phong_luong_prompt_agy.py
# Mo phong chinh xac cach AGY xu ly moi khi nguoi dung go mot prompt

import json
from pathlib import Path


def buoc_1_nap_quy_tac_va_skill():
    """Doc tom tat cac luat va metadata cua skill (Progressive Disclosure)."""
    # Chi nap ten va mo ta ngan gon, khong nap toan bo noi dung de tiet kiem token
    ds_skill_tom_tat = {
        "kiem-thu-harness": "Bo khung danh gia va kiem thu tu dong cho AGY"
    }
    xau_luat = "Luon tra loi ro rang, uu tien giai thich tung buoc."
    return xau_luat, ds_skill_tom_tat


def buoc_2_ghep_ngu_canh(xau_prompt, xau_luat, ds_skill_tom_tat):
    """Ghep toan bo thong tin thanh goi tin gui cho Model."""
    goi_tin = {
        "system_instruction": f"Quy tac: {xau_luat} | Skills co san: {json.dumps(ds_skill_tom_tat, ensure_ascii=False)}",
        "user_input": xau_prompt
    }
    return goi_tin


def buoc_3_mo_hinh_ra_quyet_dinh(goi_tin):
    """Mo hinh phan tich y dinh nguoi dung de chon hanh dong."""
    xau_vao = goi_tin["user_input"].lower()

    # Neu nguoi dung yeu cau kiem thu -> Kich hoat skill
    if "kiem thu" in xau_vao or "harness" in xau_vao or "test" in xau_vao:
        return {
            "loai_hanh_dong": "goi_tool",
            "ten_tool": "run_command",
            "lenh": "python chay_harness_song_song.py"
        }
    # Neu la cau hoi thong thuong -> Tra loi truc tiep
    return {
        "loai_hanh_dong": "tra_loi_truc_tiep",
        "noi_dung": "Giai dap thac mac cua nguoi dung dua tren tri thuc san co."
    }


def xu_ly_mot_prompt_tren_agy(xau_prompt):
    """Ham tong the mo phong mot luot chat tren AGY."""
    # 1. Nap quy tac va danh sach skill
    xau_luat, ds_skill = buoc_1_nap_quy_tac_va_skill()

    # 2. Dong goi tin gui den Mo hinh
    goi_tin = buoc_2_ghep_ngu_canh(xau_prompt, xau_luat, ds_skill)

    # 3. Mo hinh suy nghi va dua ra hanh dong
    qd = buoc_3_mo_hinh_ra_quyet_dinh(goi_tin)

    return qd


if __name__ == "__main__":
    # Truong hop 1: Nguoi dung hoi binh thuong
    p1 = "Hom nay thoi tiet the nao?"
    kq1 = xu_ly_mot_prompt_tren_agy(p1)
    print(f"Prompt 1: '{p1}' -> Hanh dong: {kq1['loai_hanh_dong']}")

    # Truong hop 2: Nguoi dung nhac den kiem thu
    p2 = "Hay chay test harness cho toi"
    kq2 = xu_ly_mot_prompt_tren_agy(p2)
    print(f"Prompt 2: '{p2}' -> Hanh dong: {kq2['loai_hanh_dong']} (Lenh: {kq2.get('lenh')})")
