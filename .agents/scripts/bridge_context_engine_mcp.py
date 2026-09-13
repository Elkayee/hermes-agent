# bridge_context_engine_mcp.py
# Cau noi MCP Stdio cho Context Engine phuc vu AGY CLI

import os
import sys
import json
import urllib.request
from pathlib import Path

# Dam bao terminal Windows ma hoa UTF-8
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass


def tim_thu_muc_goc(duong_dan):
    """Tim thu muc goc cua repo dua tren .git, Cargo.toml, package.json."""
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


def tim_repo_hien_tai(goi_y_tep=None):
    """Xac dinh thu muc repo dang lam viec dua tren goi y tep, runtime state hoac CWD."""
    if goi_y_tep:
        return tim_thu_muc_goc(goi_y_tep)

    # 1. Kiem tra active_workspace.txt tu hook
    tep_ws = Path(os.environ.get("USERPROFILE", "C:/Users/Home33")) / ".gemini" / "active_workspace.txt"
    if tep_ws.exists():
        try:
            nd = tep_ws.read_text(encoding="utf-8").strip()
            if nd and Path(nd).exists():
                return tim_thu_muc_goc(nd)
        except Exception:
            pass

    # 2. Kiem tra active_repo.txt
    tep_repo = Path(r"C:\Tools\hermes-agent\.agents\active_repo.txt")
    if tep_repo.exists():
        try:
            nd = tep_repo.read_text(encoding="utf-8").strip()
            if nd and Path(nd).exists():
                return tim_thu_muc_goc(nd)
        except Exception:
            pass

    cwd = str(Path.cwd().resolve()).lower()
    if "chatcmd" in cwd:
        return r"c:\tools\chatcmd"
    if "hermes" in cwd:
        return r"c:\tools\hermes-agent"

    return tim_thu_muc_goc(cwd)


def goi_api_context_engine(truy_van, tm_repo):
    """Goi API Context Engine Master Router."""
    url = "http://127.0.0.1:6699/api/query"
    du_lieu = {
        "query": str(truy_van).strip(),
        "repo": str(tm_repo).lower()
    }
    try:
        yeu_cau = urllib.request.Request(
            url,
            headers={"Content-Type": "application/json"},
            data=json.dumps(du_lieu).encode("utf-8")
        )
        with urllib.request.urlopen(yeu_cau, timeout=10.0) as phan_hoi:
            if phan_hoi.status == 200:
                kq = json.loads(phan_hoi.read().decode("utf-8", errors="replace"))
                return kq.get("results", [])
    except Exception as loi:
        return f"[Loi ket noi Context Engine: {str(loi)}]"
    return []


def dinh_dang_ket_qua(ds_kq):
    """Dinh dang danh sach ket qua thanh van ban markdown de model de doc."""
    if isinstance(ds_kq, str):
        return ds_kq
    if not ds_kq:
        return "Khong tim thay ket qua ngu nghia phu hop trong repository."

    cac_dong = []
    for muc in ds_kq[:10]:
        tep = muc.get("file", "")
        bd = muc.get("line_start", 1)
        kt = muc.get("line_end", 1)
        diem = round(muc.get("score", 0.0), 3)
        ky_hieu = muc.get("symbol")
        nd = muc.get("content", "")

        tieu_de = f"### {tep} (dong {bd}-{kt}, diem: {diem})"
        if ky_hieu:
            tieu_de += f" [symbol: {ky_hieu}]"
        cac_dong.append(tieu_de)
        cac_dong.append("```")
        cac_dong.append(nd)
        cac_dong.append("```\n")

    return "\n".join(cac_dong)


def xu_ly_yeu_cau(yeu_cau):
    """Xu ly cac ban tin JSON-RPC 2.0 cua giao thuc MCP."""
    phuong_thuc = yeu_cau.get("method")
    ma_id = yeu_cau.get("id")
    tham_so = yeu_cau.get("params", {})

    if phuong_thuc == "initialize":
        return {
            "jsonrpc": "2.0",
            "id": ma_id,
            "result": {
                "protocolVersion": "2024-11-05",
                "capabilities": {
                    "tools": {}
                },
                "serverInfo": {
                    "name": "context-engine-bridge",
                    "version": "1.0.0"
                }
            }
        }

    if phuong_thuc == "notifications/initialized":
        return None

    if phuong_thuc == "ping":
        return {"jsonrpc": "2.0", "id": ma_id, "result": {}}

    if phuong_thuc == "tools/list":
        return {
            "jsonrpc": "2.0",
            "id": ma_id,
            "result": {
                "tools": [
                    {
                        "name": "codebase-retrieval",
                        "description": "Tim kiem ngu nghia (semantic code search) va AST symbols toan bo repository bang Context Engine.",
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                "information_request": {
                                    "type": "string",
                                    "description": "Mo ta tu nhien doan code hoac thong tin can tim."
                                }
                            },
                            "required": ["information_request"]
                        }
                    },
                    {
                        "name": "file-retrieval",
                        "description": "Trich xuat doan ma (snippets) kem so dong tu 1 file cu the bang Context Engine.",
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                "file_path": {
                                    "type": "string",
                                    "description": "Duong dan tuong doi hoac tuyet doi den file."
                                },
                                "information_request": {
                                    "type": "string",
                                    "description": "Mo ta thong tin can trich xuat trong file nay."
                                },
                                "top_k": {
                                    "type": "integer",
                                    "description": "So doan ma can trich xuat (mac dinh 5)."
                                }
                            },
                            "required": ["file_path", "information_request"]
                        }
                    }
                ]
            }
        }

    if phuong_thuc == "tools/call":
        ten_tool = tham_so.get("name")
        doi_so = tham_so.get("arguments", {})
        tm_repo = tim_repo_hien_tai()

        if ten_tool == "codebase-retrieval":
            yeu_cau_tt = doi_so.get("information_request", "")
            kq = goi_api_context_engine(yeu_cau_tt, tm_repo)
            van_ban = dinh_dang_ket_qua(kq)
            return {
                "jsonrpc": "2.0",
                "id": ma_id,
                "result": {
                    "content": [
                        {
                            "type": "text",
                            "text": van_ban
                        }
                    ]
                }
            }

        if ten_tool == "file-retrieval":
            tep = doi_so.get("file_path", "")
            yeu_cau_tt = doi_so.get("information_request", "")
            tm_repo_tep = tim_repo_hien_tai(goi_y_tep=tep)
            truy_van_hop_nhat = f"{tep} {yeu_cau_tt}"
            kq = goi_api_context_engine(truy_van_hop_nhat, tm_repo_tep)
            # Loc ket qua theo file neu co
            if isinstance(kq, list):
                kq_loc = [m for m in kq if tep.lower() in m.get("file", "").lower()]
                kq = kq_loc if kq_loc else kq
            van_ban = dinh_dang_ket_qua(kq)
            return {
                "jsonrpc": "2.0",
                "id": ma_id,
                "result": {
                    "content": [
                        {
                            "type": "text",
                            "text": van_ban
                        }
                    ]
                }
            }

        return {
            "jsonrpc": "2.0",
            "id": ma_id,
            "error": {
                "code": -32601,
                "message": f"Method not found: {ten_tool}"
            }
        }

    return {
        "jsonrpc": "2.0",
        "id": ma_id,
        "error": {
            "code": -32601,
            "message": f"Method not found: {phuong_thuc}"
        }
    }


def main():
    """Vong lap doc stdin va ghi stdout theo chuan JSON-RPC 2.0."""
    for dong in sys.stdin:
        dong = dong.strip()
        if not dong:
            continue
        try:
            yeu_cau = json.loads(dong)
            tra_loi = xu_ly_yeu_cau(yeu_cau)
            if tra_loi is not None:
                print(json.dumps(tra_loi, ensure_ascii=False), flush=True)
        except Exception as loi:
            loi_json = {
                "jsonrpc": "2.0",
                "id": None,
                "error": {
                    "code": -32700,
                    "message": f"Parse error: {str(loi)}"
                }
            }
            print(json.dumps(loi_json, ensure_ascii=False), flush=True)


if __name__ == "__main__":
    main()
