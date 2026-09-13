# quan_ly_vong_doi_skills_telemetry.py
# Bo theo doi tan suat su dung Skill, xep hang Top va co che Tam Ngung (Deactivate) an toan

import os
import sys
import json
import time
import re
from pathlib import Path
from collections import Counter

# Dam bao UTF-8 khong loi font tieng Viet tren Windows
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

# Duong dan he thong
tm_goc = Path(__file__).resolve().parent.parent.parent
tm_agents = tm_goc / ".agents"
tm_brain = Path(r"C:\Users\Home33\.gemini\antigravity-cli\brain")
tep_nhat_ky = tm_agents / "nhat_ky_harness.jsonl"
tep_trang_thai = tm_agents / "trang_thai_skills.json"

# Danh sach cac skill he thong quan trong KHONG BAO GIO duoc phep deactive
SKILLS_BAT_TU = {
    "find-skills", "agy-customizations", "antigravity_guide", "code-review",
    "diagnosing-bugs", "tdd", "reverse-engineering", "api-security"
}


def doc_file_trang_thai():
    """Doc file luu trang thai bat/tat va tan suat cua cac skill."""
    if tep_trang_thai.exists():
        try:
            with open(tep_trang_thai, "r", encoding="utf-8", errors="ignore") as f:
                return json.load(f)
        except Exception:
            pass
    return {"skills": {}, "deactivated": []}


def ghi_file_trang_thai(dl):
    """Ghi trang thai cap nhat xuong file JSON."""
    try:
        with open(tep_trang_thai, "w", encoding="utf-8") as f:
            json.dump(dl, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"[-] Loi ghi trang thai skills: {e}")


def thu_thap_tan_suat_su_dung():
    """
    Quet nhat_ky_harness.jsonl va toan bo transcripts trong brain/
    de tong hop chinh xac so lan moi skill duoc kich hoat va moc thoi gian gan nhat.
    """
    dem_skill = Counter()
    lan_cuoi = {}

    # 1. Quet nhat_ky_harness.jsonl
    if tep_nhat_ky.exists():
        try:
            with open(tep_nhat_ky, "r", encoding="utf-8", errors="ignore") as f:
                for dong in f:
                    dong_s = dong.strip()
                    if not dong_s:
                        continue
                    try:
                        obj = json.loads(dong_s)
                        sk = obj.get("skill_kich_hoat")
                        tg = obj.get("thoi_gian", 0)
                        if sk:
                            dem_skill[sk] += 1
                            if sk not in lan_cuoi or tg > lan_cuoi[sk]:
                                lan_cuoi[sk] = tg
                    except Exception:
                        pass
        except Exception:
            pass

    # 2. Quet them tu cac phien transcript trong brain/ neu co ghi nhan
    if tm_brain.exists():
        try:
            for tep_ts in tm_brain.glob("**/transcript.jsonl"):
                try:
                    with open(tep_ts, "r", encoding="utf-8", errors="ignore") as f:
                        for dong in f:
                            if "SKILL.md" in dong or "skill_kich_hoat" in dong:
                                # Tim kiem ten skill duoc nhac toi
                                khop = re.findall(r"skills[\\/]([a-zA-Z0-9_\-]+)[\\/]SKILL\.md", dong)
                                for ten_kn in khop:
                                    dem_skill[ten_kn] += 1
                except Exception:
                    pass
        except Exception:
            pass

    return dem_skill, lan_cuoi


def dong_bo_va_phan_tich_skills():
    """
    Tong hop so lieu toan dien:
    - Tong so skill
    - So skill dang Active vs Deactivated
    - Top skill su dung nhieu nhat
    - Danh sach skill Ngu Dong (Dormant / Cold)
    """
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    from quet_tat_ca_skills import quet_toan_bo_skills_he_thong

    ds_kn = quet_toan_bo_skills_he_thong()
    dem_skill, lan_cuoi = thu_thap_tan_suat_su_dung()
    tt = doc_file_trang_thai()
    ds_deact = set(tt.get("deactivated", []))

    bang_thong_ke = []
    so_active = 0
    so_deact = 0

    for kn in ds_kn:
        ten = kn["ten"]
        so_lan = dem_skill.get(ten, 0)
        tg_gan_nhat = lan_cuoi.get(ten, 0)
        dang_bat = ten not in ds_deact

        if dang_bat:
            so_active += 1
        else:
            so_deact += 1

        bang_thong_ke.append({
            "ten": ten,
            "nguon": kn.get("nguon", "Toan cuc"),
            "mo_ta": kn.get("mo_ta", ""),
            "duong_dan": kn.get("duong_dan", ""),
            "so_lan_dung": so_lan,
            "tg_gan_nhat": tg_gan_nhat,
            "trang_thai": "ACTIVE" if dang_bat else "DEACTIVATED",
            "co_the_deactivate": ten not in SKILLS_BAT_TU
        })

    # Sap xep theo so lan dung giam dan
    bang_thong_ke.sort(key=lambda x: (x["so_lan_dung"], x["tg_gan_nhat"]), reverse=True)

    # Top skills
    top_skills = [k for k in bang_thong_ke if k["so_lan_dung"] > 0][:10]

    # Danh sach Dormant (0 lan dung va khong phai skill bat tu)
    ds_dormant = [k for k in bang_thong_ke if k["so_lan_dung"] == 0 and k["co_the_deactivate"]]

    bao_cao = {
        "tong_skills": len(ds_kn),
        "so_active": so_active,
        "so_deactivated": so_deact,
        "ti_le_su_dung": round((len([k for k in bang_thong_ke if k["so_lan_dung"] > 0]) / len(ds_kn)) * 100, 2) if ds_kn else 0,
        "top_skills": top_skills,
        "so_dormant": len(ds_dormant),
        "danh_sach": bang_thong_ke
    }

    return bao_cao


def tam_ngung_skill(ten_skill, ly_do="Nguoi dung yeu cau hoac khong su dung"):
    """Tam ngung (Deactivate) mot skill an toan."""
    if ten_skill in SKILLS_BAT_TU:
        return False, f"Skill '{ten_skill}' la ky nang he thong bat buoc, khong the tam ngung."

    tt = doc_file_trang_thai()
    ds_deact = set(tt.get("deactivated", []))
    if ten_skill in ds_deact:
        return True, f"Skill '{ten_skill}' da o trang thai tam ngung truoc do."

    ds_deact.add(ten_skill)
    tt["deactivated"] = list(ds_deact)
    if "chi_tiet" not in tt:
        tt["chi_tiet"] = {}
    tt["chi_tiet"][ten_skill] = {
        "thoi_diem": time.time(),
        "ly_do": ly_do
    }
    ghi_file_trang_thai(tt)
    return True, f"Da tam ngung (Deactivate) thanh cong skill '{ten_skill}'."


def kich_hoat_lai_skill(ten_skill):
    """Kich hoat lai (Reactivate) mot skill da bi tam ngung."""
    tt = doc_file_trang_thai()
    ds_deact = set(tt.get("deactivated", []))
    if ten_skill not in ds_deact:
        return True, f"Skill '{ten_skill}' hien dang hoat dong (Active)."

    ds_deact.remove(ten_skill)
    tt["deactivated"] = list(ds_deact)
    if "chi_tiet" in tt and ten_skill in tt["chi_tiet"]:
        del tt["chi_tiet"][ten_skill]
    ghi_file_trang_thai(tt)
    return True, f"Da kich hoat lai (Reactivate) thanh cong skill '{ten_skill}'."


def tu_dong_tam_ngung_skills_dormant_ctf():
    """
    Tu dong deactive cac skill thuoc nhom competition-* neu khong dung,
    giup lam sach context va tang toc do dinh tuyen cho cac tac vu lap trinh thong thuong.
    """
    bc = dong_bo_va_phan_tich_skills()
    dem_ngung = 0
    for kn in bc["danh_sach"]:
        ten = kn["ten"]
        if ten.startswith("competition-") and kn["so_lan_dung"] == 0:
            ok, _ = tam_ngung_skill(ten, "Tu dong loc skill CTF ngu dong")
            if ok:
                dem_ngung += 1
    return dem_ngung


if __name__ == "__main__":
    print("=================================================================")
    print("      HERMES HARNESS - SKILL TELEMETRY & LIFECYCLE CONTROLLER    ")
    print("=================================================================")
    bc = dong_bo_va_phan_tich_skills()
    print(f"• Tong so skills      : {bc['tong_skills']}")
    print(f"• Dang hoat dong      : {bc['so_active']} Active")
    print(f"• Dang tam ngung      : {bc['so_deactivated']} Deactivated")
    print(f"• Ti le tung su dung  : {bc['ti_le_su_dung']}%")
    print(f"• So skill ngu dong   : {bc['so_dormant']} skills")
    print("\n--- TOP 10 SKILLS DUOC SU DUNG NHIEU NHAT ---")
    for i, sk in enumerate(bc["top_skills"], 1):
        print(f"  {i}. {sk['ten']:<30} : {sk['so_lan_dung']} lan ({sk['trang_thai']})")

    # Kiem tra thu deactive mot skill competition
    print("\n[*] Kiem tra thu nghiem deactive 1 skill ngu dong:")
    test_kn = "competition-zip-archive"
    ok, msg = tam_ngung_skill(test_kn, "Kiem tra telemetry")
    print(f"  -> {msg}")
    bc2 = dong_bo_va_phan_tich_skills()
    print(f"  -> So active sau khi deactive: {bc2['so_active']}, Deactivated: {bc2['so_deactivated']}")

    # Kich hoat lai ngay de tra ve nguyen ven
    ok2, msg2 = kich_hoat_lai_skill(test_kn)
    print(f"[*] Kiem tra reactivate:")
    print(f"  -> {msg2}")
