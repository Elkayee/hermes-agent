# bo_dinh_tuyen_skills.py
# Module dinh tuyen va tu dong kich hoat Skills (tuong thich triet ly find-skills) cho Hermes Harness

import os
import sys
import json
import re
from pathlib import Path

# Dam bao terminal Windows khong bi loi ma hoa tieng Viet
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

# Cac duong dan goc chua skills
TM_SKILLS_USER = Path(r"C:\Users\Home33\.agents\skills")
TM_SKILLS_BUILTIN = Path(r"C:\Users\Home33\.gemini\antigravity-cli\builtin\skills")

# Tu dien tu khoa dac trung giup cham diem nhanh cac nhom bai toan
TU_DIEN_NHOM = {
    "reverse-engineering": ["reverse", "dich nguoc", "binary", "assembly", "disasm", "decompile", "pe", "elf", "unpack"],
    "ida-reverse": ["ida", "ida pro", "ida free", "hex-rays", "idb", "i64"],
    "ghidra-reverse": ["ghidra", "decompiler ghidra"],
    "radare2": ["radare2", "r2", "rabin2", "rasm2"],
    "apk-reverse": ["apk", "android", "smali", "jadx", "dex", "frida apk"],
    "dotnet-reverse": ["dotnet", ".net", "c#", "dnspy", "de4dot", "clr", "csharp"],
    "pentest-tools": ["pentest", "scan", "nmap", "sqlmap", "nuclei", "ffuf", "burp", "tan cong", "lo hong"],
    "api-security": ["api", "rest", "graphql", "endpoint", "swagger", "postman"],
    "code-review": ["review code", "soat code", "kiem tra code", "danh gia code", "pr review"],
    "tdd": ["tdd", "test driven", "viet test", "unit test", "integration test"],
    "diagnosing-bugs": ["debug", "loi", "bug", "crash", "trace error", "chan doan loi", "exception"],
    "ui-ux-pro-max": ["ui", "ux", "giao dien", "design system", "frontend layout", "mau sac", "css", "tailwind"],
    "ui-styling": ["styling", "shadcn", "component ui", "button", "modal", "card"],
    "banner-design": ["banner", "poster", "quang cao", "graphic design"],
    "diagram-generator": ["so do", "diagram", "mermaid", "flowchart", "kien truc", "sequence diagram"],
    "find-skills": ["find skill", "cai skill", "tim skill", "mo rong", "skill moi", "npx skills"]
}


def doc_toan_bo_skills():
    """Doc va cache danh muc tat ca cac skill hien co tren he thong."""
    ds_kn = []
    cac_tm = [TM_SKILLS_USER, TM_SKILLS_BUILTIN]

    for tm in cac_tm:
        if not tm.exists():
            continue
        for thu_muc in tm.iterdir():
            if thu_muc.is_dir():
                tep_sk = thu_muc / "SKILL.md"
                mo_ta = ""
                if tep_sk.exists():
                    try:
                        nd = tep_sk.read_text(encoding="utf-8", errors="ignore")
                        khop = re.search(r"^description:\s*(.+)$", nd, re.MULTILINE)
                        if khop:
                            mo_ta = khop.group(1).strip().strip('"\'')
                    except Exception:
                        mo_ta = ""
                ds_kn.append({
                    "ten": thu_muc.name,
                    "mo_ta": mo_ta,
                    "tep": str(tep_sk) if tep_sk.exists() else ""
                })
    return ds_kn


def lay_prompt_tu_transcript(duong_dan_ts):
    """Doc transcript.jsonl de lay cau yeu cau gan nhat cua nguoi dung."""
    if not duong_dan_ts:
        return ""
    tep_ts = Path(duong_dan_ts)
    if not tep_ts.exists():
        return ""

    xau_yc = ""
    try:
        with open(tep_ts, "r", encoding="utf-8", errors="ignore") as f:
            for dong in f:
                dong_s = dong.strip()
                if not dong_s:
                    continue
                try:
                    obj = json.loads(dong_s)
                    if obj.get("type") == "USER_INPUT":
                        nd = obj.get("content", "")
                        # Bop tach <USER_REQUEST>
                        khop = re.search(r"<USER_REQUEST>(.*?)</USER_REQUEST>", nd, re.DOTALL)
                        if khop:
                            xau_yc = khop.group(1).strip()
                        else:
                            xau_yc = nd.strip()
                except Exception:
                    pass
    except Exception:
        pass
    return xau_yc


def tinh_diem_phu_hop(xau_yc, kn):
    """Cham diem muc do phu hop cua skill dua tren yeu cau cua nguoi dung."""
    if not xau_yc:
        return 0

    yc_thg = xau_yc.lower()
    ten_kn = kn["ten"].lower()
    mo_ta_kn = kn["mo_ta"].lower()
    diem = 0

    # 1. Ten skill xuat hien truc tiep
    if ten_kn in yc_thg:
        diem += 50

    # 2. Khop tu khoa dac trung trong tu dien (dung word boundary tranh khop nham substring nhu 'pe' trong 'pipeline')
    if ten_kn in TU_DIEN_NHOM:
        for tk in TU_DIEN_NHOM[ten_kn]:
            if len(tk) <= 3:
                if re.search(r"\b" + re.escape(tk) + r"\b", yc_thg):
                    diem += 15
            else:
                if tk in yc_thg:
                    diem += 15

    # 3. Khop cac tu rieng le cua ten skill
    cac_tu_ten = ten_kn.replace("-", " ").split()
    for tu in cac_tu_ten:
        if len(tu) > 2:
            if re.search(r"\b" + re.escape(tu) + r"\b", yc_thg):
                diem += 8

    # 4. Khop mot phan mo ta
    cac_tu_yc = re.findall(r"\w+", yc_thg)
    for tu in set(cac_tu_yc):
        if len(tu) >= 4 and tu in mo_ta_kn:
            diem += 2

    return diem


def dinh_tuyen_skills(du_lieu_payload):
    """Phan tich prompt va tao chi thi kich hoat skill bat buoc cho Agent."""
    duong_dan_ts = du_lieu_payload.get("transcriptPath", "")
    xau_yc = lay_prompt_tu_transcript(duong_dan_ts)

    ds_kn = doc_toan_bo_skills()
    ds_diem = []

    for kn in ds_kn:
        diem = tinh_diem_phu_hop(xau_yc, kn)
        if diem > 0:
            ds_diem.append((diem, kn))

    # Sap xep skill theo diem cao nhat
    ds_diem.sort(key=lambda x: x[0], reverse=True)

    # Tao chi thi Harness
    if ds_diem and ds_diem[0][0] >= 10:
        top_kn = ds_diem[0][1]
        ten_top = top_kn["ten"]
        tep_top = top_kn["tep"]
        
        # Danh sach cac skill lien quan phu
        ds_phu = [x[1]["ten"] for x in ds_diem[1:3]]
        xau_phu = f" (Kem de xuat phu: {', '.join(ds_phu)})" if ds_phu else ""

        # Kiem tra xem skill co dang bi tam ngung khong de tu dong danh thuc (Auto-Wakeup)
        thong_bao_wakeup = ""
        tep_tt = Path(__file__).resolve().parent.parent / "trang_thai_skills.json"
        if tep_tt.exists():
            try:
                with open(tep_tt, "r", encoding="utf-8", errors="ignore") as f:
                    ds_deact = set(json.load(f).get("deactivated", []))
                    if ten_top in ds_deact:
                        from quan_ly_vong_doi_skills_telemetry import kich_hoat_lai_skill
                        kich_hoat_lai_skill(ten_top)
                        thong_bao_wakeup = "\n• [TỰ ĐỘNG ĐÁNH THỨC]: Kỹ năng này đang ở trạng thái tạm ngưng (Deactivated). Hệ thống đã tự động kích hoạt lại (Auto-Reactivated)!"
            except Exception:
                pass

        chi_thi = (
            f"[HERMES SKILL ROUTER - MANDATORY ACTIVATION]\n"
            f"• Phat hien yeu cau phu hop nhat voi Skill: '{ten_top}'{xau_phu}.{thong_bao_wakeup}\n"
            f"• Duong dan SKILL.md: {tep_top}\n"
            f"• QUY TAC BAT BUOC: Truoc khi tra loi hoac thuc thi code, ban PHAI dung 'view_file' "
            f"doc noi dung SKILL.md cua skill nay de nam ro runbook va huong dan chuan hoa."
        )
        return chi_thi, ten_top
    else:
        # Neu khong co skill noi bo nao dat diem cao -> Kich hoat triet ly find-skills
        chi_thi = (
            f"[HERMES SKILL ROUTER - FIND-SKILLS PROTOCOL]\n"
            f"• Khong tim thay skill noi bo nao khop hoan toan voi yeu cau hien tai.\n"
            f"• QUY TAC BAT BUOC (find-skills): Neu tac vu doi hoi quy trinh hoac cong cu chuyen biet, "
            f"ban hay kich hoat quy trinh 'find-skills' (tra cuu 'npx skills find <tu_khoa>' hoac tren https://skills.sh) "
            f"de de xuat skill thich hop cho nguoi dung, tranh tu thuc thi cam tinh."
        )
        return chi_thi, "find-skills"


if __name__ == "__main__":
    # Kiem thu nhanh module
    du_lieu_mau = {"transcriptPath": ""}
    kq, ten = dinh_tuyen_skills(du_lieu_mau)
    print("Ket qua dinh tuyen:")
    print(kq)
    print(f"Skill chon: {ten}")
