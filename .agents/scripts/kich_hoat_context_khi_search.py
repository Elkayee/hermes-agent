# kich_hoat_context_khi_search.py
# Hook PreToolUse: Tu dong kich hoat Context Engine bo sung moi khi AGY CLI goi grep_search hoac find_by_name

import os
import sys
import json
import time
import urllib.request
from pathlib import Path

# Dam bao terminal Windows ma hoa UTF-8
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass


def truy_van_context_engine(truy_van, duong_dan_repo):
    """Goi API cua Context Engine Master Router de lay ngu canh ngu nghia va AST."""
    if not truy_van or not str(truy_van).strip():
        return []

    url = "http://127.0.0.1:6699/api/query"
    du_lieu_gui = {
        "query": str(truy_van).strip(),
        "repo": str(Path(duong_dan_repo).resolve()).lower()
    }

    try:
        yeu_cau = urllib.request.Request(
            url,
            headers={"Content-Type": "application/json"},
            data=json.dumps(du_lieu_gui).encode("utf-8")
        )
        with urllib.request.urlopen(yeu_cau, timeout=8.0) as phan_hoi:
            if phan_hoi.status == 200:
                kq = json.loads(phan_hoi.read().decode("utf-8", errors="replace"))
                return kq.get("results", [])
    except Exception:
        pass
    return []


def ghi_nhat_ky_kich_hoat(ma_phien, ten_tool, truy_van, duong_dan, so_ket_qua):
    """Ghi lich su kich hoat context engine song hanh vao tep nhat ky."""
    tm_nhat_ky = Path(__file__).resolve().parent.parent
    tep_nk = tm_nhat_ky / "nhat_ky_harness.jsonl"
    ban_ghi = {
        "thoi_gian": round(time.time(), 2),
        "thoi_diem": time.strftime("%H:%M:%S %d/%m/%Y"),
        "ma_phien": ma_phien,
        "su_kien": "BO_SUNG_CONTEXT_ENGINE_KHI_SEARCH",
        "ten_tool": ten_tool,
        "truy_van": str(truy_van),
        "duong_dan": str(duong_dan),
        "so_ket_qua_ngu_nghia": so_ket_qua
    }
    try:
        tm_nhat_ky.mkdir(parents=True, exist_ok=True)
        with open(tep_nk, "a", encoding="utf-8") as f:
            f.write(json.dumps(ban_ghi, ensure_ascii=False) + "\n")
    except Exception:
        pass


def main():
    """Ham xu ly chinh cho hook PreToolUse cua AGY CLI."""
    xau_vao = ""
    du_lieu = {}

    try:
        if not sys.stdin.isatty():
            xau_vao = sys.stdin.read()
            if xau_vao.strip():
                du_lieu = json.loads(xau_vao)
    except Exception:
        du_lieu = {}

    cuoc_goi = du_lieu.get("toolCall", {})
    ten_tool = cuoc_goi.get("name", "")
    tham_so = cuoc_goi.get("args", {})
    ma_phien = du_lieu.get("conversationId", "phien_chua_ro")
    ds_ws = du_lieu.get("workspacePaths", [])

    # Trich xuat tu khoa tim kiem
    truy_van = tham_so.get("Query") or tham_so.get("Pattern") or ""
    # Xac dinh thu muc tim kiem
    duong_dan = (
        tham_so.get("SearchPath")
        or tham_so.get("SearchDirectory")
        or (ds_ws[0] if ds_ws else os.getcwd())
    )

    ds_ket_qua = []
    if truy_van:
        ds_ket_qua = truy_van_context_engine(truy_van, duong_dan)

    so_kq = len(ds_ket_qua)
    ghi_nhat_ky_kich_hoat(ma_phien, ten_tool, truy_van, str(duong_dan), so_kq)

    # Luu ket qua ngu nghia gan nhat vao tep de agent de dang truy xuat
    tep_luu_ngu_canh = Path(__file__).resolve().parent.parent / "last_search_context.json"
    try:
        du_lieu_luu = {
            "thoi_gian": time.time(),
            "ten_tool": ten_tool,
            "truy_van": str(truy_van),
            "duong_dan": str(duong_dan),
            "ket_qua": ds_ket_qua[:5]
        }
        with open(tep_luu_ngu_canh, "w", encoding="utf-8") as f:
            json.dump(du_lieu_luu, f, ensure_ascii=False, indent=2)
    except Exception:
        pass

    # Tao ly do phan hoi hop dong PreToolUse
    if so_kq > 0:
        mo_ta = f"[CONTEXT ENGINE BO SUNG]: Da kich hoat tu dong voi '{truy_van}', tim thay {so_kq} vi tri code phu hop."
    else:
        mo_ta = f"[CONTEXT ENGINE BO SUNG]: Da kich hoat voi '{truy_van}', tiep tuc chay grep song hanh."

    phan_hoi = {
        "decision": "allow",
        "reason": mo_ta
    }

    print(json.dumps(phan_hoi, ensure_ascii=False))


if __name__ == "__main__":
    main()
