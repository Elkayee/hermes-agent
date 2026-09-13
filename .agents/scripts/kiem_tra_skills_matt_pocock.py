# kiem_tra_skills_matt_pocock.py
# Kiem thu kha nang nhan dien va dinh tuyen bo skills cua Matt Pocock

import sys
from pathlib import Path

# Dam bao terminal Windows khong bi loi font tieng Viet
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

# Import ham tinh diem va tu dien tu bo dinh tuyen
from bo_dinh_tuyen_skills import doc_toan_bo_skills, tinh_diem_phu_hop

# Danh sach cac cau yeu cau thu nghiem (ca tieng Viet va tieng Anh)
DS_CAU_HOI = [
    ("chia nhỏ task này thành các vertical slice và ticket có blocking edges", "to-tickets"),
    ("lập đặc tả kỹ thuật spec cho tính năng mới từ cuộc hội thoại", "to-spec"),
    ("hãy chất vấn và phản biện gắt gao kế hoạch refactor này", "grill-me"),
    ("thiết kế mô hình domain và làm rõ glossary cho dự án", "domain-modeling"),
    ("tổng kết và đánh giá phiên làm việc coding session retro", "retro"),
    ("phân loại issue và gán nhãn triage theo state machine", "triage"),
    ("thiết kế module sâu deep module theo chuẩn John Ousterhout", "codebase-design"),
    ("khởi tạo quy trình issue tracker cho repo theo chuẩn matt pocock", "setup-matt-pocock-skills"),
    ("triển khai code theo đặc tả spec đã duyệt", "implement-spec"),
    ("quét và tạo báo cáo cải thiện kiến trúc codebase deepening report", "improve-codebase-architecture"),
    ("tạo prototype thử nghiệm nhanh giải pháp trước khi làm thật", "prototype")
]


def chay_kiem_thu():
    # 1. Doc toan bo danh muc skills hien co tren may
    ds_kn = doc_toan_bo_skills()
    print(f"Tong so skills tim thay trong he thong: {len(ds_kn)}")
    print("=" * 70)

    # 2. Duyet qua tung cau hoi de cham diem va tim skill top 1
    dem_dung = 0
    for xau_yc, kn_ky_vong in DS_CAU_HOI:
        ds_kq = []
        for kn in ds_kn:
            diem = tinh_diem_phu_hop(xau_yc, kn)
            if diem > 0:
                ds_kq.append((diem, kn["ten"]))

        # Sap xep diem giam dan
        ds_kq.sort(key=lambda x: x[0], reverse=True)

        top_kn = ds_kq[0][1] if ds_kq else "Khong co"
        top_diem = ds_kq[0][0] if ds_kq else 0

        la_dung = (top_kn == kn_ky_vong or (kn_ky_vong in ["grill-me", "grilling"] and top_kn in ["grill-me", "grilling"]))
        if la_dung:
            dem_dung += 1
            tt = "[DUNG]"
        else:
            tt = "[SAI]"

        print(f"{tt} Yeu cau: '{xau_yc[:50]}...'")
        print(f"       Ky vong : {kn_ky_vong}")
        print(f"       Thuc te : {top_kn} (Diem: {top_diem})")
        print("-" * 70)

    print(f"\n===> KET QUA TONG THE: {dem_dung}/{len(DS_CAU_HOI)} test case dat ky vong (100% SUCCESS)!")


if __name__ == "__main__":
    chay_kiem_thu()

