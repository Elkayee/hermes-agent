# quet_tat_ca_skills.py
# Quet toan dien tat ca cac nguon skills (User Global, AGY Builtin, Hermes Repo)

import os
import sys
import re
from pathlib import Path

# Thiet lap UTF-8 cho Windows console
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

# 3 Nguon chua skills tren he thong
CAC_NGUON_SKILLS = [
    (Path(r"C:\Users\Home33\.agents\skills"), "Toàn cục (.agents)", "huy-hieu-lam"),
    (Path(r"C:\Users\Home33\.gemini\antigravity-cli\builtin\skills"), "Mặc định (Built-in)", "huy-hieu-xanh"),
    (Path(r"C:\Tools\hermes-agent\.agents\skills"), "Hermes Repo", "huy-hieu-tim")
]


def doc_mo_ta_skill(tep_sk):
    """Doc mo ta tu YAML frontmatter cua SKILL.md, ho tro ca chuoi nhieu dong."""
    if not tep_sk.exists():
        return "Chưa có file SKILL.md"

    try:
        nd = tep_sk.read_text(encoding="utf-8", errors="ignore")
        # Tim description trong frontmatter
        khop = re.search(r"^description:\s*(?:>-\s*|\|\s*)?(.*?)(?:\n[a-zA-Z0-9_-]+:|\n---)", nd, re.DOTALL | re.MULTILINE)
        if khop:
            xau_mt = khop.group(1).strip().replace("\n", " ")
            xau_mt = re.sub(r"\s+", " ", xau_mt).strip('"\'')
            if xau_mt:
                return xau_mt[:200] + ("..." if len(xau_mt) > 200 else "")
        # Fallback neu chi co 1 dong
        for dong in nd.splitlines()[:15]:
            if dong.startswith("description:"):
                return dong.replace("description:", "").strip().strip('"\'')
    except Exception:
        pass
    return "Chưa có mô tả"


def quet_toan_bo_skills_he_thong():
    """Quet va tong hop danh sach tat ca cac skills tu ca 3 nguon thu muc."""
    ds_kn = []
    da_quet = set()

    for tm_nguon, ten_nguon, mau_tag in CAC_NGUON_SKILLS:
        if not tm_nguon.exists():
            continue

        for tm in sorted(tm_nguon.iterdir()):
            if tm.is_dir():
                ten_kn = tm.name
                tep_sk = tm / "SKILL.md"
                mo_ta = doc_mo_ta_skill(tep_sk)

                # Neu trung ten -> danh dau da co
                khoa = ten_kn.lower()
                da_co = khoa in da_quet
                da_quet.add(khoa)

                ds_kn.append({
                    "ten": ten_kn,
                    "mo_ta": mo_ta,
                    "nguon": ten_nguon,
                    "mau_tag": mau_tag,
                    "duong_dan": str(tep_sk) if tep_sk.exists() else str(tm),
                    "trung_lap": da_co
                })

    # Sap xep theo ten
    ds_kn.sort(key=lambda x: x["ten"].lower())
    return ds_kn


if __name__ == "__main__":
    ds = quet_toan_bo_skills_he_thong()
    print(f"[*] Tong so skills tim thay: {len(ds)} skills")
    print(f"[*] So skills doc nhat: {len(set(x['ten'].lower() for x in ds))} skills")
    print("\nVi du 5 skills dau tien:")
    for k in ds[:5]:
        print(f"• [{k['ten']}] ({k['nguon']}): {k['mo_ta'][:80]}...")
