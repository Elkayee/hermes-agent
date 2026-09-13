# kich_hoat_context_khi_search.py
# Hook PreToolUse: Tu dong kich hoat Context Engine bo sung moi khi AGY CLI goi grep_search hoac find_by_name

import os
import sys
import json
import time
import re
import urllib.request
from pathlib import Path

# Dam bao terminal Windows ma hoa UTF-8
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass


def tim_goc_repo(duong_dan):
    """Tim thu muc goc cua repo dua vao cac dau hieu .git, Cargo.toml, package.json."""
    try:
        p = Path(duong_dan).resolve()
        if p.is_file():
            p = p.parent
        for cha in [p] + list(p.parents):
            if any((cha / m).exists() for m in [".git", "Cargo.toml", "package.json", "pyproject.toml", "pom.xml"]):
                return str(cha)
        return str(p)
    except Exception:
        return str(duong_dan)


def dam_bao_context_engine_hoat_dong():
    """Watchdog tu dong kiem tra va khoi dong lai Context Engine neu bi tat."""
    import socket
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(0.25)
            if s.connect_ex(('127.0.0.1', 6699)) == 0:
                return True
    except Exception:
        pass

    tep_bin = Path(r"C:\Tools\vibervn-context-engine\target\release\context-engine-rs.exe")
    if not tep_bin.exists():
        return False

    import subprocess
    try:
        DETACHED_PROCESS = 0x00000008
        CREATE_NO_WINDOW = 0x08000000
        subprocess.Popen(
            [str(tep_bin), "--port", "6699", "--bind", "127.0.0.1"],
            creationflags=DETACHED_PROCESS | CREATE_NO_WINDOW,
            close_fds=True
        )
        for _ in range(10):
            time.sleep(0.35)
            try:
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                    s.settimeout(0.2)
                    if s.connect_ex(('127.0.0.1', 6699)) == 0:
                        return True
            except Exception:
                pass
    except Exception:
        pass
    return False


def dam_bao_repo_da_index(goc_repo):
    """Tu dong dang ky va index kho moi vao Context Engine qua REST API neu chua co."""
    dam_bao_context_engine_hoat_dong()
    try:
        goc_chuan = str(Path(goc_repo).resolve())
        # 1. Doc danh sach repos tu /api/config
        yeu_cau_cfg = urllib.request.Request("http://127.0.0.1:6699/api/config")
        with urllib.request.urlopen(yeu_cau_cfg, timeout=3.0) as res:
            cfg = json.loads(res.read().decode("utf-8"))
            ds_repos = cfg.get("repos", [])

        # 2. Neu chua co, them vao va PUT /api/config
        if not any(r.lower() == goc_chuan.lower() for r in ds_repos):
            cfg["repos"].append(goc_chuan)
            yeu_cau_put = urllib.request.Request(
                "http://127.0.0.1:6699/api/config",
                method="PUT",
                headers={"Content-Type": "application/json"},
                data=json.dumps(cfg).encode("utf-8")
            )
            urllib.request.urlopen(yeu_cau_put, timeout=5.0)

            # 3. Kich hoat index cho kho moi
            import base64
            ma_id = base64.urlsafe_b64encode(goc_chuan.encode("utf-8")).decode("utf-8").rstrip("=")
            yeu_cau_idx = urllib.request.Request(
                f"http://127.0.0.1:6699/api/repos/{ma_id}/index",
                method="POST"
            )
            urllib.request.urlopen(yeu_cau_idx, timeout=5.0)
    except Exception:
        pass


def truy_van_context_engine(truy_van, duong_dan_repo):
    """Goi API cua Context Engine Master Router de lay ngu canh ngu nghia va AST."""
    if not truy_van or not str(truy_van).strip():
        return []

    goc_repo = tim_goc_repo(duong_dan_repo)
    dam_bao_repo_da_index(goc_repo)

    url = "http://127.0.0.1:6699/api/query"
    du_lieu_gui = {
        "query": str(truy_van).strip(),
        "repo": goc_repo.lower()
    }

    try:
        yeu_cau = urllib.request.Request(
            url,
            headers={"Content-Type": "application/json"},
            data=json.dumps(du_lieu_gui).encode("utf-8")
        )
        with urllib.request.urlopen(yeu_cau, timeout=14.0) as phan_hoi:
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

    # Trich xuat tu khoa tim kiem tu Query (grep_search) hoac Pattern (find_by_name)
    truy_van_goc = tham_so.get("Query") or tham_so.get("Pattern") or ""
    # Lam sach neu la Pattern dang glob (vi du: *benchmark*.py -> benchmark)
    truy_van = re.sub(r'[*?]+', ' ', str(truy_van_goc)).strip()
    if "." in truy_van:
        truy_van = re.sub(r'\.(py|js|ts|json|md|rs|go|java|c|cpp|h|txt)$', '', truy_van, flags=re.IGNORECASE).strip()
    if not truy_van:
        truy_van = str(truy_van_goc).strip()

    # Xac dinh thu muc tim kiem
    duong_dan = (
        tham_so.get("SearchPath")
        or tham_so.get("SearchDirectory")
        or (ds_ws[0] if ds_ws else os.getcwd())
    )

    goc_repo = tim_goc_repo(duong_dan)
    # Tu dong cap nhat active workspace cho MCP Gateway va Bridge
    try:
        tep_ws = Path(os.environ.get("USERPROFILE", "C:/Users/Home33")) / ".gemini" / "active_workspace.txt"
        tep_ws.parent.mkdir(parents=True, exist_ok=True)
        tep_ws.write_text(goc_repo, encoding="utf-8")
        tep_ws2 = Path(__file__).resolve().parent.parent / "active_repo.txt"
        tep_ws2.write_text(goc_repo, encoding="utf-8")
    except Exception:
        pass

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

    # Tao ly do phan hoi hop dong PreToolUse kem toan bo code snippets de Agent doc truc tiep
    if so_kq > 0:
        cac_doan_ma = []
        for i, item in enumerate(ds_ket_qua[:5], 1):
            tep = item.get("file", "")
            d_dau = item.get("line_start", "")
            d_cuoi = item.get("line_end", "")
            diem = item.get("score")
            diem_str = f"{diem:.3f}" if isinstance(diem, (int, float)) else "N/A"
            nd = item.get("content", "").strip()
            if len(nd) > 1200:
                nd = nd[:1200] + "\n... [con tiep]"
            cac_doan_ma.append(f"--- [Snippet #{i}] Tep: {tep} (Dong {d_dau}-{d_cuoi}) [Score: {diem_str}] ---\n{nd}")

        chuoi_snippets = "\n\n".join(cac_doan_ma)
        mo_ta = (
            f"[CONTEXT ENGINE DA KICH HOAT - AGENT BAT BUOC DOC VA PHAN TICH NGAY]:\n"
            f"Khi goi {ten_tool} ('{truy_van}'), Context Engine da tu dong tim thay {so_kq} vi tri code lien quan trong kho [{goc_repo}].\n"
            f"Duoi day la Top {len(cac_doan_ma)} doan ma ngu nghia quan trong nhat duoc trich xuat san de Agent doc truc tiep:\n\n"
            f"{chuoi_snippets}\n\n"
            f"=> CHI THI: Agent phai doc, doi chieu truc tiep cac doan ma tren va trich dan so dong, tep cu the khi phan hoi."
        )
    else:
        mo_ta = (
            f"[CONTEXT ENGINE]: Da kich hoat tim kiem ngu nghia cho '{truy_van}' trong kho [{goc_repo}] "
            f"nhung khong tim thay doan ma phu hop (0 ket qua). Tiep tuc thuc thi {ten_tool} song hanh."
        )

    phan_hoi = {
        "decision": "allow",
        "reason": mo_ta
    }

    print(json.dumps(phan_hoi, ensure_ascii=False))


if __name__ == "__main__":
    main()
