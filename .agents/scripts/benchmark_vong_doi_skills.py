# benchmark_vong_doi_skills.py
# Bo Benchmark do luong tieu chi: Khi nao dung skill co san, khi nao tim ngoai, khi nao build skill moi va xac nhan su dung

import os
import sys
import json
import time
import re
import shutil
from pathlib import Path

# Dam bao terminal Windows ho tro tieng Viet khong loi ky tu
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

# Thiet lap thu muc goc
tm_goc = Path(__file__).resolve().parent.parent.parent
tm_scripts = tm_goc / ".agents" / "scripts"
sys.path.insert(0, str(tm_scripts))

# Nap module quet toan bo skills va bo dinh tuyen
from quet_tat_ca_skills import quet_toan_bo_skills_he_thong
from bo_dinh_tuyen_skills import tinh_diem_phu_hop

# Tu khoa bao hieu can dong goi / build skill moi
TU_KHOA_BUILD_MOI = [
    "tạo skill", "tao skill", "build skill", "đóng gói workflow", "dong goi workflow",
    "chuẩn hóa quy trình", "chuan hoa quy trinh", "lưu thành skill", "luu thanh skill",
    "xây dựng kỹ năng", "xay dung ky nang", "tự động hóa quy trình", "tu dong hoa quy trinh"
]

# Tu khoa bao hieu tac vu phuc tap can quy trinh rieng
TU_KHOA_PHUC_TAP = [
    "pipeline", "tự động hóa", "tu dong hoa", "chuyên biệt", "chuyen biet",
    "nhiều bước", "nhieu buoc", "runbook", "framework"
]

def danh_gia_nhu_cau_skill(xau_yc, ds_kn):
    """
    Ma tran ra quyet dinh cua Hermes Harness:
    1. DUNG_SKILL_CU: Neu co skill noi bo khop diem cao (>= 15).
    2. BUILD_SKILL_MOI: Neu co yeu cau dong goi ro rang hoac thieu nang luc + do phuc tap cao.
    3. TIM_SKILL_NGOAI: Neu thieu nang luc nhung la cau hoi tra cuu chung (find-skills).
    """
    xau_thg = xau_yc.lower()
    
    # 1. Kiem tra xem nguoi dung co yeu cau tuong minh ve viec BUILD skill khong
    la_yeu_cau_build = any(tk in xau_thg for tk in TU_KHOA_BUILD_MOI)
    
    # 2. Tinh diem khop voi toan bo 161 skills hien co
    ds_diem = []
    for kn in ds_kn:
        diem = tinh_diem_phu_hop(xau_yc, kn)
        if diem > 0:
            ds_diem.append((diem, kn))
            
    ds_diem.sort(key=lambda x: x[0], reverse=True)
    diem_cao_nhat = ds_diem[0][0] if ds_diem else 0
    top_kn = ds_diem[0][1]["ten"] if ds_diem else None
    
    # 3. Kiem tra muc do phuc tap cua tac vu
    co_tinh_phuc_tap = any(tk in xau_thg for tk in TU_KHOA_PHUC_TAP)

    # 4. Ra quyet dinh theo tieu chi ro rang
    if la_yeu_cau_build:
        return {
            "quyet_dinh": "BUILD_SKILL_MOI",
            "ly_do": "Nguoi dung yeu cau tuong minh dong goi/tao skill moi.",
            "top_skill": None,
            "diem": diem_cao_nhat
        }

    if diem_cao_nhat >= 15:
        return {
            "quyet_dinh": "DUNG_SKILL_CU",
            "ly_do": f"Khop voi skill noi bo hien co '{top_kn}' voi diem tin cay cao ({diem_cao_nhat}).",
            "top_skill": top_kn,
            "diem": diem_cao_nhat
        }
        
    if co_tinh_phuc_tap and diem_cao_nhat < 15:
        return {
            "quyet_dinh": "BUILD_SKILL_MOI",
            "ly_do": "Tac vu ky thuat phuc tap nhung chua co skill chuyen biet dat nguong tin cay (Capability Gap).",
            "top_skill": None,
            "diem": diem_cao_nhat
        }

    return {
        "quyet_dinh": "TIM_SKILL_NGOAI",
        "ly_do": "Khong khop skill noi bo nao dat nguong, kich hoat giao thuc find-skills tra cuu kho ngoai.",
        "top_skill": "find-skills",
        "diem": diem_cao_nhat
    }


def tao_tap_kiem_thu_benchmark():
    """Tap cac bai test khao sat day du moi tinh huong vong doi cua Skill."""
    return [
        {
            "id": "TC_SKILL_01_REVERSE",
            "prompt": "Dịch ngược file PE x64 và phân tích hàm giải mã payload trong Ghidra",
            "ky_vong_qd": "DUNG_SKILL_CU",
            "ky_vong_skill": ["ghidra-reverse", "reverse-engineering"],
            "mo_ta": "Truy van dung chinh xac skill dich nguoc hien co"
        },
        {
            "id": "TC_SKILL_02_REVIEW",
            "prompt": "Review code pull request mới nhất để kiểm tra vi phạm chuẩn thiết kế và convention",
            "ky_vong_qd": "DUNG_SKILL_CU",
            "ky_vong_skill": ["code-review"],
            "mo_ta": "Truy van dung skill danh gia ma nguon"
        },
        {
            "id": "TC_SKILL_03_TDD",
            "prompt": "Áp dụng phương pháp test-driven development viết unit test trước khi viết logic",
            "ky_vong_qd": "DUNG_SKILL_CU",
            "ky_vong_skill": ["tdd", "test-driven-development"],
            "mo_ta": "Truy van dung skill phat trien huong kiem thu"
        },
        {
            "id": "TC_SKILL_04_FIND_COMMUNITY",
            "prompt": "Tìm kiếm trên skills.sh xem cộng đồng có skill nào hỗ trợ kết nối database ClickHouse không",
            "ky_vong_qd": "TIM_SKILL_NGOAI",
            "ky_vong_skill": ["find-skills"],
            "mo_ta": "Kich hoat find-skills khi hoi tim kiem cong cu ben ngoai"
        },
        {
            "id": "TC_SKILL_05_BUILD_EXPLICIT",
            "prompt": "Hãy tạo skill mới tên là bsod-crash-analysis chuyên phân tích file memory.dmp khi Windows bị màn hình xanh",
            "ky_vong_qd": "BUILD_SKILL_MOI",
            "ky_vong_skill": None,
            "mo_ta": "Yeu cau tuong minh tao skill moi cho AGY"
        },
        {
            "id": "TC_SKILL_06_BUILD_GAP",
            "prompt": "Xây dựng pipeline chuyên biệt tự động audit smart contract Solidity và tối ưu hóa gas limit EVM nhiều bước",
            "ky_vong_qd": "BUILD_SKILL_MOI",
            "ky_vong_skill": None,
            "mo_ta": "Khoang trong nang luc kem do phuc tap cao doi hoi quy trinh rieng"
        }
    ]


def chay_benchmark_vong_doi():
    """Chay toan bo quy trinh benchmark va tinh toan cac chi so KPI."""
    print("=================================================================")
    print("      HERMES HARNESS - BENCHMARK QUYET DINH VONG DOI SKILL       ")
    print("=================================================================")

    ds_kn = quet_toan_bo_skills_he_thong()
    print(f"[*] Tong so skills noi bo dang nạp: {len(ds_kn)} skills.")
    
    tap_kt = tao_tap_kiem_thu_benchmark()
    ds_ket_qua = []
    dem_dung_qd = 0
    dem_dung_skill = 0
    tong_tg = 0.0

    for tc in tap_kt:
        t0 = time.time()
        kq = danh_gia_nhu_cau_skill(tc["prompt"], ds_kn)
        dt = time.time() - t0
        tong_tg += dt
        
        dung_qd = (kq["quyet_dinh"] == tc["ky_vong_qd"])
        dung_sk = True
        if tc["ky_vong_skill"]:
            dung_sk = (kq["top_skill"] in tc["ky_vong_skill"])

        if dung_qd:
            dem_dung_qd += 1
        if dung_sk:
            dem_dung_skill += 1

        dat_toan_dien = dung_qd and dung_sk
        trang_thai = "✓ PASS" if dat_toan_dien else "✗ FAIL"

        ds_ket_qua.append({
            "id": tc["id"],
            "prompt": tc["prompt"],
            "ky_vong_qd": tc["ky_vong_qd"],
            "thuc_te_qd": kq["quyet_dinh"],
            "ky_vong_skill": tc["ky_vong_skill"],
            "thuc_te_skill": kq["top_skill"],
            "dat": dat_toan_dien,
            "thoi_gian": round(dt, 4),
            "ly_do": kq["ly_do"]
        })

        print(f"[{trang_thai}] {tc['id']}: Quyết định: {kq['quyet_dinh']} | Skill: {kq['top_skill']} ({dt:.4f}s)")

    ti_le_qd = round((dem_dung_qd / len(tap_kt)) * 100, 2)
    ti_le_sk = round((dem_dung_skill / len(tap_kt)) * 100, 2)
    tg_tb = round(tong_tg / len(tap_kt), 4)

    print("\n---------------- TONG HOP KET QUA BENCHMARK ----------------")
    print(f"• Do chinh xac quyet dinh (Decision Accuracy) : {ti_le_qd}% ({dem_dung_qd}/{len(tap_kt)})")
    print(f"• Do chinh xac chon skill (Skill Match Accuracy): {ti_le_sk}% ({dem_dung_skill}/{len(tap_kt)})")
    print(f"• Thoi gian phan tich trung binh               : {tg_tb}s/truy van")
    print("------------------------------------------------------------\n")

    # 5. Kiem thu chu trinh thuc te: Build skill moi -> Nap vao kho -> Su dung ngay
    print("[*] KIEM THU CHU TRINH THUC TE: BUILD SKILL MOI & TAI SU DUNG...")
    ten_skill_thu_nghiem = "bsod-crash-analysis"
    tm_skill_moi = tm_goc / ".agents" / "skills" / ten_skill_thu_nghiem
    tm_skill_moi.mkdir(parents=True, exist_ok=True)
    
    noi_dung_skill = f"""---
name: {ten_skill_thu_nghiem}
description: Chuyên phân tích tệp memory.dmp khi Windows gặp sự cố màn hình xanh (BSOD) sử dụng WinDbg và xuất báo cáo.
---

# Kỹ Năng: Phân Tích Sự Cố Windows BSOD Crash

## Mục Tiêu
Cung cấp quy trình từng bước tải ký hiệu (Symbols), nạp dump và chạy lệnh !analyze -v để tìm driver gây lỗi.

## Quy Trình
1. Nạp tệp dump vào WinDbg: `windbg -z C:\\Windows\\MEMORY.DMP`.
2. Thiết lập symbol server: `.sympath srv*https://msdl.microsoft.com/download/symbols`.
3. Chạy phân tích tự động: `!analyze -v`.
4. Trích xuất tên MODULE_NAME và FAILURE_BUCKET_ID.
"""
    tep_sk_moi = tm_skill_moi / "SKILL.md"
    tep_sk_moi.write_text(noi_dung_skill.strip() + "\n", encoding="utf-8")
    print(f"[+] Da build thanh cong skill moi tai: {tep_sk_moi}")

    # Quet lai toan bo kho sau khi build
    ds_kn_moi = quet_toan_bo_skills_he_thong()
    tim_thay = any(k["ten"] == ten_skill_thu_nghiem for k in ds_kn_moi)
    print(f"[+] So luong skills sau khi build: {len(ds_kn_moi)} (Tang them: {'Co' if tim_thay else 'Khong'})")

    # Kiem tra routing ngay lap tuc
    cau_hoi_test = "Tôi có file memory.dmp bị crash màn hình xanh, hãy dùng bsod analysis kiểm tra driver nào gây lỗi"
    kq_test_moi = danh_gia_nhu_cau_skill(cau_hoi_test, ds_kn_moi)
    print(f"[+] Kiem thu su dung skill moi vua build:")
    print(f"    - Quyet dinh : {kq_test_moi['quyet_dinh']}")
    print(f"    - Skill chon : {kq_test_moi['top_skill']}")
    print(f"    - Diem so    : {kq_test_moi['diem']}")
    
    thanh_cong_vong_doi = (kq_test_moi["quyet_dinh"] == "DUNG_SKILL_CU" and kq_test_moi["top_skill"] == ten_skill_thu_nghiem)
    print(f"==> KET LUAN VONG DOI: {'HOAN TOAN THANH CONG (100%)' if thanh_cong_vong_doi else 'THAT BAI'}")

    # Luu bao cao benchmark ra JSON de dashboard Hermes doc duoc
    bao_cao = {
        "thoi_diem": time.time(),
        "tong_so": len(tap_kt),
        "so_dat": dem_dung_qd,
        "ti_le_dat": ti_le_qd,
        "tong_thoi_gian": round(tong_tg, 4),
        "thoi_gian_tb": tg_tb,
        "tong_token": 0,
        "tong_chi_phi": 0.0,
        "chi_tiet": [
            {
                "id": k["id"],
                "dat": k["dat"],
                "thoi_gian": k["thoi_gian"],
                "token_vao": 0,
                "token_ra": 0,
                "token_suy_nghi": 0,
                "tong_token": 0,
                "chi_phi": 0.0,
                "phan_hoi": f"Quyet dinh: {k['thuc_te_qd']} -> Skill: {k['thuc_te_skill']} ({k['ly_do']})"
            }
            for k in ds_ket_qua
        ],
        "vong_doi_build_moi": {
            "ten_skill": ten_skill_thu_nghiem,
            "tim_thay_sau_build": tim_thay,
            "kich_hoat_thanh_cong": thanh_cong_vong_doi
        }
    }

    tep_bc = tm_goc / "_luu_tru_tam" / "ket_qua_benchmark_skills.json"
    tep_bc.parent.mkdir(parents=True, exist_ok=True)
    with open(tep_bc, "w", encoding="utf-8") as f:
        json.dump(bao_cao, f, ensure_ascii=False, indent=2)
    print(f"[+] Da xuat bao cao benchmark tai: {tep_bc}")

    # Ghi them file jsonl vao tap kiem thu de tab Test Suites tren Dashboard hien thi
    tep_jsonl = tm_goc / "_luu_tru_tam" / "tap_kiem_thu_skills_lifecycle.jsonl"
    with open(tep_jsonl, "w", encoding="utf-8") as f:
        for tc in tap_kt:
            f.write(json.dumps({
                "id": tc["id"],
                "prompt": tc["prompt"],
                "expected": f"{tc['ky_vong_qd']} ({tc['ky_vong_skill'] or 'Build'})",
                "loai_tap": "Vòng đời Skill"
            }, ensure_ascii=False) + "\n")
    print(f"[+] Da cap nhat tap kiem thu tai: {tep_jsonl}")

    return bao_cao


if __name__ == "__main__":
    chay_benchmark_vong_doi()
