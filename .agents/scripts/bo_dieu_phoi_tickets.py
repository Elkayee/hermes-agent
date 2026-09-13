# bo_dieu_phoi_tickets.py
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


def chuyen_trang_thai_ticket(tep_ticket, tt_moi):
    """Cap nhat trang thai Status trong file markdown cua ticket."""
    tep = Path(tep_ticket)
    if not tep.exists():
        return False
    nd = tep.read_text(encoding="utf-8", errors="ignore")
    nd_moi = re.sub(r"^Status:\s*[\w-]+", f"Status: {tt_moi}", nd, flags=re.MULTILINE)
    tep.write_text(nd_moi, encoding="utf-8")
    return True
