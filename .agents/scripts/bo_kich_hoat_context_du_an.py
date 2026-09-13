# bo_kich_hoat_context_du_an.py
# Module tu dong phat hien va kich hoat AGENTS.md, plan.md, task.md / Frontier Tickets cho Hermes Harness

import os
import sys
import re
from pathlib import Path

# Dam bao terminal Windows ho tro UTF-8
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass


def lay_thu_muc_workspace(du_lieu_payload=None):
    """Xac dinh thu muc workspace hien tai tu payload hoac active_workspace.txt."""
    # 1. Thu tu du lieu payload truyen vao
    if du_lieu_payload:
        ws_payload = du_lieu_payload.get("workspaceDir") or du_lieu_payload.get("cwd")
        if ws_payload and os.path.isdir(ws_payload):
            return Path(ws_payload)

    # 2. Thu tu active_workspace.txt cua gemini
    tep_ws = Path(r"C:\Users\Home33\.gemini\active_workspace.txt")
    if tep_ws.exists():
        try:
            ws_txt = tep_ws.read_text(encoding="utf-8").strip()
            if ws_txt and os.path.isdir(ws_txt):
                return Path(ws_txt)
        except Exception:
            pass

    # 3. Thu tu thu muc cha cua .agents (mac dinh la hermes-agent)
    tm_hien_tai = Path(__file__).resolve().parent.parent.parent
    if tm_hien_tai.exists():
        return tm_hien_tai

    return Path(os.getcwd())


def nap_agents_md(tm_ws):
    """Doc va trich xuat cac quy tac quan trong tu AGENTS.md cua workspace."""
    tep_ag = tm_ws / "AGENTS.md"
    if not tep_ag.exists():
        return ""

    txt = tep_ag.read_text(encoding="utf-8", errors="ignore")
    # Neu file ngan (< 3500 ky tu), lay toan bo noi dung
    if len(txt) <= 3500:
        return f"[{tep_ag.name}]:\n" + txt.strip()

    # Neu file dai, trich xuat tieu de dau va cac khoi quy tac quan trong
    cac_khoi = [f"[{tep_ag.name} - Trich doan quy tac chinh]:"]
    cac_khoi.append(txt[:1200].strip())

    # Tim cac heading quan trong ve Git, Context Engine, Agent skills
    cac_muc = [
        r"## Git Architecture.*?(?=\n## |\Z)",
        r"## Context Engine.*?(?=\n## |\Z)",
        r"## Agent skills.*?(?=\n## |\Z)",
        r"## Routing Table.*?(?=\n## |\Z)"
    ]
    for mau in cac_muc:
        m = re.search(mau, txt, re.DOTALL)
        if m:
            cac_khoi.append(m.group(0).strip()[:1500])

    return "\n\n---\n\n".join(cac_khoi)


def nap_plan_md(tm_ws):
    """Doc ban ke hoach plan.md hoac spec.md cua du an."""
    # 1. Tim plan.md hoac spec.md o thu muc goc
    for ten in ["plan.md", "PLAN.md", "spec.md", "SPEC.md"]:
        tep = tm_ws / ten
        if tep.exists():
            nd = tep.read_text(encoding="utf-8", errors="ignore")[:3000].strip()
            return f"[{tep.name}]:\n{nd}"

    # 2. Tim trong .scratch/*/spec.md
    tm_scratch = tm_ws / ".scratch"
    if tm_scratch.exists():
        for spec in sorted(tm_scratch.glob("*/spec.md")):
            nd = spec.read_text(encoding="utf-8", errors="ignore")[:3000].strip()
            rel = spec.relative_to(tm_ws)
            return f"[{rel}]:\n{nd}"

    # 3. Tim trong plan/*.md
    tm_plan = tm_ws / "plan"
    if tm_plan.exists():
        for p in sorted(tm_plan.glob("*.md")):
            nd = p.read_text(encoding="utf-8", errors="ignore")[:3000].strip()
            rel = p.relative_to(tm_ws)
            return f"[{rel}]:\n{nd}"

    return ""


def nap_task_md(tm_ws):
    """Doc danh sach task tu task.md va cac frontier tickets trong .scratch."""
    ket_qua = []

    # 1. Tim task.md o thu muc goc
    for ten in ["task.md", "TASK.md", "tasks.md"]:
        tep = tm_ws / ten
        if tep.exists():
            txt = tep.read_text(encoding="utf-8", errors="ignore")
            # Loc cac dong task checklist (- [ ] hoac - [x])
            dong_tasks = [d for d in txt.splitlines() if re.match(r"^\s*-\s*\[[ xX]\]", d)]
            if dong_tasks:
                ket_qua.append(f"[{tep.name} (Tien do task)]:\n" + "\n".join(dong_tasks[:20]))
            else:
                ket_qua.append(f"[{tep.name}]:\n" + txt[:2000].strip())
            break

    # 2. Quet frontier tickets tu .scratch (theo chuan Wayfinder Matt Pocock)
    tm_scratch = tm_ws / ".scratch"
    if tm_scratch.exists():
        for tm_feature in sorted(tm_scratch.iterdir()):
            if tm_feature.is_dir():
                tm_issues = tm_feature / "issues"
                if tm_issues.exists():
                    try:
                        ds_tk = []
                        for issue in sorted(tm_issues.glob("*.md")):
                            nd = issue.read_text(encoding="utf-8", errors="ignore")
                            st = re.search(r"^Status:\s*([\w-]+)", nd, re.MULTILINE)
                            status = st.group(1).strip() if st else "chua_ro"
                            bl = re.search(r"^Blocked by:\s*(.+)$", nd, re.MULTILINE)
                            blocked = bl.group(1).strip() if bl else "none"
                            ds_tk.append((issue.name, status, blocked))

                        # Loc cac ticket san sang thuc thi
                        ready = [t for t in ds_tk if t[1] in ["ready-for-agent", "needs-triage"]]
                        if ready:
                            ds_ready_str = "\n".join([f"- {t[0]} (Status: {t[1]}, Blocked by: {t[2]})" for t in ready])
                            ket_qua.append(f"[Frontier Tickets - {tm_feature.name} (San sang)]: \n{ds_ready_str}")
                        else:
                            da_xong = sum(1 for t in ds_tk if t[1] == "resolved")
                            ket_qua.append(f"[Tickets - {tm_feature.name}]: {da_xong}/{len(ds_tk)} tickets da RESOLVED.")
                    except Exception:
                        pass

    return "\n\n".join(ket_qua)


def tao_khoi_du_an_harness(du_lieu_payload=None):
    """Tong hop va dong goi toan bo thong tin AGENTS.md, plan.md, task.md thanh khoi context."""
    tm_ws = lay_thu_muc_workspace(du_lieu_payload)

    xau_ag = nap_agents_md(tm_ws)
    xau_plan = nap_plan_md(tm_ws)
    xau_task = nap_task_md(tm_ws)

    # Neu khong co bat ky thanh phan nao
    if not xau_ag and not xau_plan and not xau_task:
        return ""

    cac_phan = ["<project-context>", f"Workspace Root: {tm_ws}"]

    if xau_ag:
        cac_phan.append(f"=== [PROJECT AGENTS.MD RULES] ===\n{xau_ag}")

    if xau_plan:
        cac_phan.append(f"=== [ACTIVE PLAN (plan.md / spec.md)] ===\n{xau_plan}")

    if xau_task:
        cac_phan.append(f"=== [ACTIVE TASKS (task.md / Frontier Tickets)] ===\n{xau_task}")

    cac_phan.append("</project-context>")
    return "\n\n".join(cac_phan)


if __name__ == "__main__":
    print(tao_khoi_du_an_harness())
