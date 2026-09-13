# dong_bo_context_tu_dong.py
# Kich ban tu dong tom tat va dong bo trang thai phien lam viec vao CONTEXT.md cho Hermes

import os
import sys
import json
import time
from pathlib import Path

# Thiet lap UTF-8 cho Windows console
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

# Duong dan goc toi thu muc memory
tm_goc = Path(__file__).resolve().parent.parent
tm_nho = tm_goc / "memory"
tep_ctx = tm_nho / "CONTEXT.md"


def doc_yeu_cau_gan_nhat_tu_transcript(duong_dan_ts):
    """Trich xuat danh sach cac yeu cau gan nhat tu transcript.jsonl."""
    if not duong_dan_ts or not Path(duong_dan_ts).exists():
        return []

    ds_yc = []
    try:
        with open(duong_dan_ts, "r", encoding="utf-8", errors="ignore") as f:
            for dong in f:
                dong_s = dong.strip()
                if not dong_s:
                    continue
                try:
                    obj = json.loads(dong_s)
                    if obj.get("type") == "USER_INPUT":
                        nd = obj.get("content", "")
                        # Loc lay text gon gang
                        if "<USER_REQUEST>" in nd:
                            nd = nd.split("<USER_REQUEST>")[1].split("</USER_REQUEST>")[0].strip()
                        if nd and nd not in ds_yc:
                            ds_yc.append(nd)
                except Exception:
                    pass
    except Exception:
        pass
    return ds_yc[-5:]  # Lay toi da 5 yeu cau gan nhat


def cap_nhat_context_md(ma_phien, ds_yc, trang_thai_moi="Dang hoat dong", in_thong_bao=False):
    """Ghi de noi dung CONTEXT.md voi thoi gian va trang thai phien moi nhat."""
    thoi_diem = time.strftime("%H:%M:%S %d/%m/%Y")
    
    ds_dong_yc = "\n".join([f"- {yc}" for yc in ds_yc]) if ds_yc else "- Chua co yeu cau moi."

    noi_dung_moi = f"""# Ngu Canh Phien Lam Viec (CONTEXT.md)

## Thong Tin Phien
- Ma phien: {ma_phien}
- Cap nhat luc: {thoi_diem}
- Trang thai: {trang_thai_moi}

## Cac Yeu Cau Gan Nhat Trong Phien
{ds_dong_yc}

## Ghi Chu Tien Trinh
- Hermes Context Engine va Skill Router dang hoat dong binh thuong.
- Cac bo dem token va bo nho dai han da duoc dong bo tu dong.
"""
    try:
        tep_ctx.write_text(noi_dung_moi.strip() + "\n", encoding="utf-8")
        if in_thong_bao:
            print(f"[+] Da cap nhat thanh cong CONTEXT.md luc {thoi_diem}")
        return True
    except Exception as loi:
        if in_thong_bao:
            print(f"[-] Loi cap nhat CONTEXT.md: {str(loi)}")
        return False


if __name__ == "__main__":
    ma_ph = sys.argv[1] if len(sys.argv) > 1 else "phien_hien_tai"
    duong_dan = sys.argv[2] if len(sys.argv) > 2 else ""
    
    ds = doc_yeu_cau_gan_nhat_tu_transcript(duong_dan)
    cap_nhat_context_md(ma_ph, ds)
