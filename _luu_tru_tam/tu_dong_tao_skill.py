# tu_dong_tao_skill.py
# Cong cu tu dong dong goi va tao Skill moi cho he thong AGY

import os
import sys
from pathlib import Path

# Dam bao ma hoa UTF-8 tren Windows
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass


def tao_skill_moi(ten_skill, xau_mo_ta, xau_huong_dan):
    """Tu dong tao thu muc va tep SKILL.md chuan cho AGY."""
    # 1. Chuan hoa ten thu muc skill
    ten_thu_muc = ten_skill.strip().lower().replace(" ", "-")
    duong_dan_skill = Path(".agents/skills") / ten_thu_muc
    duong_dan_skill.mkdir(parents=True, exist_ok=True)

    # 2. Xay dung noi dung tep SKILL.md voi YAML frontmatter
    noi_dung_tep = f"""---
name: {ten_thu_muc}
description: {xau_mo_ta}
---

# Huong Dan Kỹ Năng: {ten_skill}

## Muc Dinh
{xau_mo_ta}

## Quy Trinh Thuc Hien
{xau_huong_dan}
"""

    tep_skill = duong_dan_skill / "SKILL.md"
    with open(tep_skill, "w", encoding="utf-8") as f:
        f.write(noi_dung_tep.strip() + "\n")

    print(f"[+] DA TAO THANH CONG SKILL: '{ten_thu_muc}'")
    print(f"[+] Vi tri luu tep        : {tep_skill}")
    print("[+] AGY se tu dong nhan dien skill nay o cac luot prompt tiep theo!")
    return str(tep_skill)


if __name__ == "__main__":
    # Vi du mau: Tu dong tao mot skill chuyen xu ly du lieu CSV
    ten = "xu-ly-csv-nhanh"
    mo_ta = "Chuyen xu ly, doc va trich xuat du lieu tu cac tep CSV lon mot cach toi uu."
    huong_dan = (
        "1. Kiem tra dinh dang tep CSV bang ma utf-8.\\n"
        "2. Su dung thu vien csv hoac pandas de loc du lieu.\\n"
        "3. Xuat ket qua tong hop ra JSON de bao cao nguoi dung."
    )

    tao_skill_moi(ten, mo_ta, huong_dan)
