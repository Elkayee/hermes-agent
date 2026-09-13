# thuc_thi_quy_trinh_matt_pocock.py
# Tu dong kich hoat va thiet lap bo quy trinh Matt Pocock cho du an

import os
import sys
import json
from pathlib import Path

# Dam bao terminal Windows khong bi loi font
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

# Import module dinh tuyen skills
sys.path.insert(0, str(Path(__file__).resolve().parent))
from bo_dinh_tuyen_skills import dinh_tuyen_skills


def tu_kich_hoat_va_thiet_lap():
    # 1. Duong dan thu muc goc cua repo
    tm_goc = Path(r"C:\Tools\hermes-agent")
    tm_docs_agents = tm_goc / "docs" / "agents"
    tm_scratch = tm_goc / ".scratch"

    # 2. Tao cac thu muc neu chua ton tai
    tm_docs_agents.mkdir(parents=True, exist_ok=True)
    tm_scratch.mkdir(parents=True, exist_ok=True)

    print("[BUOC 1] Da khoi tao thu muc 'docs/agents/' va '.scratch/'.")

    # 3. Thiet lap issue-tracker.md (Chuan Local Markdown ket hop GitHub)
    tep_it = tm_docs_agents / "issue-tracker.md"
    nd_it = """# Issue Tracker: Local Markdown & GitHub Hybrid

Issues and specs for this repo live primarily as markdown files in `.scratch/`.
When pushing upstream or syncing team tasks, GitHub Issues are also supported via `gh`.

## Conventions

- One feature per directory: `.scratch/<feature-slug>/`
- The spec is `.scratch/<feature-slug>/spec.md`
- Implementation issues are one file per ticket at `.scratch/<feature-slug>/issues/<NN>-<slug>.md`, numbered from `01`
- Triage state is recorded as a `Status:` line near the top of each issue file
- Comments append under a `## Comments` heading
"""
    tep_it.write_text(nd_it, encoding="utf-8")
    print(f"[BUOC 2] Da tao tep cau hinh: {tep_it.name}")

    # 4. Thiet lap triage-labels.md (5 vai tro chuan cua Matt Pocock)
    tep_tl = tm_docs_agents / "triage-labels.md"
    nd_tl = """# Triage Labels

| Label in mattpocock/skills | Label in our tracker | Meaning |
| -------------------------- | -------------------- | ------- |
| `needs-triage`             | `needs-triage`       | Maintainer needs to evaluate this issue |
| `needs-info`               | `needs-info`         | Waiting on reporter for more information |
| `ready-for-agent`          | `ready-for-agent`    | Fully specified, ready for an AFK agent |
| `ready-for-human`          | `ready-for-human`    | Requires human implementation |
| `wontfix`                  | `wontfix`            | Will not be actioned |
"""
    tep_tl.write_text(nd_tl, encoding="utf-8")
    print(f"[BUOC 3] Da tao tep cau hinh: {tep_tl.name}")

    # 5. Thiet lap domain.md (Single-context doc layout)
    tep_dm = tm_docs_agents / "domain.md"
    nd_dm = """# Domain Docs

## File Structure: Single-context Repo

- `CONTEXT.md`: High-level domain overview at repo root.
- `docs/adr/`: Architecture Decision Records.
"""
    tep_dm.write_text(nd_dm, encoding="utf-8")
    print(f"[BUOC 4] Da tao tep cau hinh: {tep_dm.name}")

    # 6. Cap nhat AGENTS.md voi khoi ## Agent skills
    tep_ag = tm_goc / "AGENTS.md"
    if tep_ag.exists():
        nd_ag = tep_ag.read_text(encoding="utf-8")
        if "## Agent skills" not in nd_ag:
            khoi_sk = """
---

## Agent skills

### Issue tracker

Local markdown files under `.scratch/`. See `docs/agents/issue-tracker.md`.

### Triage labels

Canonical five roles (`needs-triage`, `needs-info`, `ready-for-agent`, `ready-for-human`, `wontfix`). See `docs/agents/triage-labels.md`.

### Domain docs

Single-context (`CONTEXT.md` + `docs/adr/`). See `docs/agents/domain.md`.
"""
            tep_ag.write_text(nd_ag.strip() + "\n" + khoi_sk, encoding="utf-8")
            print("[BUOC 5] Da bo sung khoi '## Agent skills' vao AGENTS.md.")
        else:
            print("[BUOC 5] Khoi '## Agent skills' da ton tai trong AGENTS.md.")

    # 7. Thu nghiem tu dong trigger qua ham dinh tuyen cua Router
    print("\n" + "=" * 65)
    print("[BUOC 6] Kiem tra Router tu dong nhan dien va kich hoat:")
    cau_lenh_thu = "Hãy chia nhỏ task tích hợp harness thành các tracer bullet tickets và lưu vào .scratch"
    
    # Tao payload gia lap
    du_lieu = {"transcriptPath": ""}
    # Ghi tam vao transcript ao
    tep_ts_tam = tm_scratch / "transcript_tam.jsonl"
    dong_ts = {"type": "USER_INPUT", "content": f"<USER_REQUEST>{cau_lenh_thu}</USER_REQUEST>"}
    tep_ts_tam.write_text(json.dumps(dong_ts, ensure_ascii=False) + "\n", encoding="utf-8")
    
    du_lieu_pl = {"transcriptPath": str(tep_ts_tam)}
    chi_thi, ten_sk = dinh_tuyen_skills(du_lieu_pl)
    
    print(f"• Cau yeu cau : '{cau_lenh_thu}'")
    print(f"• Skill trigger: '{ten_sk}'")
    print("• Chi thi sinh ra:")
    print(chi_thi)
    
    # Don dep tep tam
    if tep_ts_tam.exists():
        tep_ts_tam.unlink()
        
    print("=" * 65)
    print("Quy trinh setup da hoan tat 100%!")


if __name__ == "__main__":
    tu_kich_hoat_va_thiet_lap()
