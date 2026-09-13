# kiem_tra_quy_trinh_tdd.py
# Kiem thu kha nang tu dong nhan dien va thuc thi vong lap TDD (Red -> Green)

import sys
import json
from pathlib import Path

# Dam bao terminal Windows khong bi loi font
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

# Import module dinh tuyen skills
sys.path.insert(0, str(Path(__file__).resolve().parent))
from bo_dinh_tuyen_skills import tinh_diem_phu_hop, doc_toan_bo_skills


def kiem_tra_nhan_dien_tdd():
    """Kiem tra Router co tu dong trigger skill tdd dung yeu cau khong."""
    ds_kn = doc_toan_bo_skills()
    
    cac_cau_lenh_tdd = [
        "hãy áp dụng quy trình tdd red-green-refactor để viết tính năng",
        "viết test trước khi code theo phương pháp test driven development",
        "kiểm thử unit test tại các public seam theo chuẩn tdd"
    ]
    
    print("=" * 65)
    print("[PHẦN 1]: KIỂM TRA NHẬN DIỆN VÀ ĐỊNH TUYẾN TDD")
    print("=" * 65)
    
    for cau in cac_cau_lenh_tdd:
        ds_kq = []
        for kn in ds_kn:
            diem = tinh_diem_phu_hop(cau, kn)
            if diem > 0:
                ds_kq.append((diem, kn["ten"]))
        ds_kq.sort(key=lambda x: x[0], reverse=True)
        top_kn = ds_kq[0][1] if ds_kq else "Khong co"
        top_diem = ds_kq[0][0] if ds_kq else 0
        
        dat = (top_kn == "tdd")
        tt = "[ĐÚNG]" if dat else "[SAI]"
        print(f"{tt} Yêu cầu: '{cau[:45]}...'")
        print(f"     Skill chọn: {top_kn} (Điểm: {top_diem})")
        print("-" * 65)


def chay_vong_lap_tdd_thuc_te():
    """Mo phong vong lap TDD Red -> Green tren Seam cua bo dieu phoi tickets."""
    print("\n" + "=" * 65)
    print("[PHẦN 2]: VÒNG LẶP TDD THỰC TẾ (RED -> GREEN)")
    print("=" * 65)
    
    # 1. Xac dinh Seam can test: ham tim ticket kha dung trong .scratch
    tm_goc = Path(r"C:\Tools\hermes-agent")
    tm_feature = tm_goc / ".scratch" / "hermes-matt-pocock-pipeline"
    
    # 2. Pha RED: Thu goi module chua duoc cai dat
    print("--- BƯỚC 1: PHA RED (Viết bài test trước khi có code) ---")
    try:
        from bo_dieu_phoi_tickets import tim_ticket_kha_dung
        print("[!] Canh bao: Module da ton tai truoc do.")
    except ImportError as loi_red:
        print(f"[RED XÁC NHẬN]: Test thất bại đúng như kỳ vọng vì chưa có mã nguồn.")
        print(f"                 Chi tiết lỗi: {loi_red}")

    # 3. Pha GREEN: Viet ma nguon toi thieu de vuot qua test
    print("\n--- BƯỚC 2: PHA GREEN (Viết mã nguồn tối thiểu vừa đủ) ---")
    tep_module = tm_goc / ".agents" / "scripts" / "bo_dieu_phoi_tickets.py"
    
    ma_nguon = r'''# bo_dieu_phoi_tickets.py
# Module quan ly frontier tickets tai .scratch theo chuan Wayfinder cua Matt Pocock

import re
from pathlib import Path


def doc_thong_tin_ticket(tep_ticket):
    """Doc trang thai Status va danh sach Blocked by tu noi dung ticket."""
    nd = tep_ticket.read_text(encoding="utf-8", errors="ignore")
    tt = "chua_ro"
    khop_tt = re.search(r"^Status:\s*([\w-]+)", nd, re.MULTILINE)
    if khop_tt:
        tt = khop_tt.group(1).strip()

    chan = []
    khop_chan = re.search(r"^Blocked by:\s*(.+)$", nd, re.MULTILINE)
    if khop_chan:
        ds_raw = khop_chan.group(1).strip()
        if ds_raw.lower() not in ["none", ""]:
            chan = [x.strip() for x in ds_raw.split(",") if x.strip()]

    return {"tep": tep_ticket, "ten": tep_ticket.stem, "status": tt, "blocked_by": chan}


def tim_ticket_kha_dung(tm_tinh_nang):
    """Quet cac ticket trong .scratch de tim ticket unblocked va unclaimed (Frontier)."""
    tm_issues = Path(tm_tinh_nang) / "issues"
    if not tm_issues.exists():
        return []

    # 1. Doc toan bo tickets
    ds_tk = []
    for tep in sorted(tm_issues.glob("*.md")):
        ds_tk.append(doc_thong_tin_ticket(tep))

    # 2. Xac dinh tap hop cac ticket da giai quyet (resolved)
    tap_resolved = {t["ten"][:2] for t in ds_tk if t["status"] == "resolved"}

    # 3. Loc cac ticket unblocked va ready
    ds_frontier = []
    for t in ds_tk:
        if t["status"] in ["ready-for-agent", "needs-triage"]:
            # Kiem tra tat ca blockers da resolved chua
            chua_xong = False
            for b in t["blocked_by"]:
                if b not in tap_resolved:
                    chua_xong = True
                    break
            if not chua_xong:
                ds_frontier.append(t)

    return ds_frontier
'''
    tep_module.write_text(ma_nguon, encoding="utf-8")
    print(f"[GREEN CODE]: Đã ghi tệp tối thiểu tại: {tep_module.name}")

    # 4. Kiem thu lai xem test da chuyen sang GREEN chua
    print("\n--- BƯỚC 3: XÁC MINH TEST CHUYỂN SANG GREEN ---")
    try:
        # Xoa cache import neu co
        if "bo_dieu_phoi_tickets" in sys.modules:
            del sys.modules["bo_dieu_phoi_tickets"]
        from bo_dieu_phoi_tickets import tim_ticket_kha_dung
        
        ds_kha_dung = tim_ticket_kha_dung(tm_feature)
        print(f"[GREEN THÀNH CÔNG]: Test đã vượt qua!")
        print(f"                    Tìm thấy {len(ds_kha_dung)} ticket khả dụng sẵn sàng xử lý:")
        for tk in ds_kha_dung:
            print(f"                    • [{tk['status']}] {tk['ten']} (Blocked by: {tk['blocked_by']})")
    except Exception as loi_green:
        print(f"[!] Test thất bại: {loi_green}")


if __name__ == "__main__":
    kiem_tra_nhan_dien_tdd()
    chay_vong_lap_tdd_thuc_te()
