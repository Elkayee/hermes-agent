# quan_ly_skills.py
# Bo cong cu quan ly, tao moi va cap nhat Skill cho AGY (Antigravity)

import os
import sys
import re
import shutil
from pathlib import Path

# Dam bao ma hoa UTF-8 tren Windows
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

# 1. Thu muc chua skills trong AGY (.agents/skills)
tm_goc = Path(__file__).resolve().parent.parent
tm_skills = tm_goc / "skills"
tm_skills.mkdir(parents=True, exist_ok=True)


# 2. Ham liet ke toan bo skills hien co
def liet_ke_skills():
    """Liet ke toan bo cac skill da cai dat trong he thong."""
    ds = []
    if not tm_skills.exists():
        return ds
        
    for tm in sorted(tm_skills.iterdir()):
        if tm.is_dir():
            tep_md = tm / "SKILL.md"
            mo_ta = "Chua co mo ta"
            if tep_md.exists():
                try:
                    nd = tep_md.read_text(encoding="utf-8", errors="ignore")
                    khop = re.search(r"^description:\s*(.+)$", nd, re.MULTILINE)
                    if khop:
                        mo_ta = khop.group(1).strip()
                except Exception:
                    pass
            ds.append({"ten": tm.name, "mo_ta": mo_ta, "duong_dan": str(tep_md)})
    return ds


# 3. Ham tao skill moi
def tao_skill_moi(ten_skill, xau_mo_ta, xau_huong_dan):
    """Tao moi mot skill voi frontmatter chuan va cau truc thu muc."""
    ten_chuan = ten_skill.strip().lower().replace(" ", "-")
    tm_moi = tm_skills / ten_chuan
    tm_moi.mkdir(parents=True, exist_ok=True)
    
    # Tao them cac thu muc con neu can
    (tm_moi / "scripts").mkdir(exist_ok=True)
    (tm_moi / "references").mkdir(exist_ok=True)
    
    nd = f"""---
name: {ten_chuan}
description: {xau_mo_ta}
---

# Huong Dan Ky Nang: {ten_skill}

## Muc Dinh
{xau_mo_ta}

## Quy Trinh Thuc Hien
{xau_huong_dan}
"""
    tep_md = tm_moi / "SKILL.md"
    tep_md.write_text(nd.strip() + "\n", encoding="utf-8")
    print(f"[+] Da tao thanh cong skill moi: '{ten_chuan}'")
    print(f"    Vi tri: {tep_md}")
    return True


# 4. Ham cap nhat skill hien co (Update Skill)
def cap_nhat_skill(ten_skill, mo_ta_moi=None, them_quy_trinh=None, thay_the_toan_bo=None):
    """Cap nhat noi dung hoac bo sung quy trinh cho mot skill da ton tai."""
    ten_chuan = ten_skill.strip().lower().replace(" ", "-")
    tm_skill = tm_skills / ten_chuan
    tep_md = tm_skill / "SKILL.md"
    
    if not tep_md.exists():
        print(f"[-] Khong tim thay skill '{ten_chuan}' de cap nhat.")
        return False
        
    nd_cu = tep_md.read_text(encoding="utf-8", errors="ignore")
    
    # Sao luu an toan truoc khi sua
    tep_bak = tm_skill / "SKILL.md.bak"
    tep_bak.write_text(nd_cu, encoding="utf-8")
    
    # Truong hop 1: Thay the toan bo noi dung bang noi dung moi
    if thay_the_toan_bo:
        tep_md.write_text(thay_the_toan_bo.strip() + "\n", encoding="utf-8")
        print(f"[+] Da cap nhat toan bo noi dung skill '{ten_chuan}'.")
        return True
        
    nd_moi = nd_cu
    
    # Truong hop 2: Cap nhat truong description trong frontmatter
    if mo_ta_moi:
        if re.search(r"^description:\s*.+$", nd_moi, re.MULTILINE):
            nd_moi = re.sub(
                r"^description:\s*.+$",
                f"description: {mo_ta_moi.strip()}",
                nd_moi,
                flags=re.MULTILINE
            )
        else:
            nd_moi = nd_moi.replace("---\n", f"---\ndescription: {mo_ta_moi.strip()}\n", 1)
        print(f"[+] Da cap nhat mo ta moi cho skill '{ten_chuan}'.")
        
    # Truong hop 3: Bo sung quy trinh vao cuoi tep SKILL.md
    if them_quy_trinh:
        nd_moi = nd_moi.strip() + f"\n\n### Cap Nhat / Bo Sung Quy Trinh:\n{them_quy_trinh.strip()}\n"
        print(f"[+] Da noi them quy trinh moi vao skill '{ten_chuan}'.")
        
    tep_md.write_text(nd_moi.strip() + "\n", encoding="utf-8")
    return True


# 5. Dieu phoi dong lenh CLI
def main():
    if len(sys.argv) < 2:
        print("=== QUAN LY SKILLS CHO AGY ===")
        print("Cac lenh kha dung:")
        print("  python quan_ly_skills.py ls                                    # Liet ke tat ca skills")
        print("  python quan_ly_skills.py xem <ten-skill>                       # Xem chi tiet skill")
        print("  python quan_ly_skills.py tao <ten> <mo_ta> <huong_dan>         # Tao skill moi")
        print("  python quan_ly_skills.py cap-nhat <ten> --mo-ta <mo_ta_moi>    # Cap nhat mo ta")
        print("  python quan_ly_skills.py cap-nhat <ten> --them <quy_trinh>     # Bo sung quy trinh")
        return

    lenh = sys.argv[1].lower()
    
    if lenh in ("ls", "list"):
        ds = liet_ke_skills()
        print(f"=== DANH SACH SKILLS ({len(ds)} skills) ===")
        for i, s in enumerate(ds, 1):
            print(f"{i}. [{s['ten']}]")
            print(f"   Mo ta: {s['mo_ta']}")
        return
        
    if lenh in ("xem", "view") and len(sys.argv) >= 3:
        ten = sys.argv[2]
        tep = tm_skills / ten / "SKILL.md"
        if tep.exists():
            print(f"--- NOI DUNG SKILL: {ten} ---")
            print(tep.read_text(encoding="utf-8", errors="ignore"))
        else:
            print(f"[-] Khong tim thay skill '{ten}'")
        return
        
    if lenh == "tao" and len(sys.argv) >= 5:
        ten = sys.argv[2]
        mo_ta = sys.argv[3]
        hd = sys.argv[4]
        tao_skill_moi(ten, mo_ta, hd)
        return
        
    if lenh == "cap-nhat" and len(sys.argv) >= 4:
        ten = sys.argv[2]
        co = sys.argv[3]
        if co == "--mo-ta" and len(sys.argv) >= 5:
            mo_ta = " ".join(sys.argv[4:])
            cap_nhat_skill(ten, mo_ta_moi=mo_ta)
        elif co == "--them" and len(sys.argv) >= 5:
            nd = " ".join(sys.argv[4:])
            cap_nhat_skill(ten, them_quy_trinh=nd)
        return

    print("[-] Lenh khong hop le hoac thieu tham so.")


if __name__ == "__main__":
    main()
