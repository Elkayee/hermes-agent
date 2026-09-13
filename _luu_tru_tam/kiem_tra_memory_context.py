# kiem_tra_memory_context.py
# Kiem tra toan dien he thong Memory Context trong Hermes Agent

import os
import sys
from pathlib import Path

# Dam bao hien thi UTF-8 tren Windows
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

duong_dan_goc = Path(__file__).resolve().parent

def kiem_tra_he_thong_memory():
    print("================ KIEM TRA MEMORY CONTEXT TRONG HERMES AGENT ================")
    
    # 1. Kiem tra agent/memory_manager.py va build_memory_context_block
    tep_quan_ly = duong_dan_goc / "agent" / "memory_manager.py"
    co_quan_ly = tep_quan_ly.exists()
    print(f"[1] agent/memory_manager.py: {'Co mat' if co_quan_ly else 'Khong tim thay'}")
    if co_quan_ly:
        noi_dung = tep_quan_ly.read_text(encoding="utf-8", errors="ignore")
        co_block = "def build_memory_context_block" in noi_dung
        co_tag = "<memory-context>" in noi_dung
        print(f"    - Ham build_memory_context_block(): {'Co' if co_block else 'Khong'}")
        print(f"    - The danh dau <memory-context>   : {'Co' if co_tag else 'Khong'}")

    # 2. Kiem tra tools/memory_tool.py (MEMORY.md va USER.md)
    tep_cong_cu = duong_dan_goc / "tools" / "memory_tool.py"
    co_cong_cu = tep_cong_cu.exists()
    print(f"\n[2] tools/memory_tool.py: {'Co mat' if co_cong_cu else 'Khong tim thay'}")
    if co_cong_cu:
        noi_dung_tool = tep_cong_cu.read_text(encoding="utf-8", errors="ignore")
        co_store = "MemoryStore" in noi_dung_tool
        co_user_md = "USER.md" in noi_dung_tool
        co_mem_md = "MEMORY.md" in noi_dung_tool
        print(f"    - Ho tro USER.md (ho so nguoi dung): {'Co' if co_user_md else 'Khong'}")
        print(f"    - Ho tro MEMORY.md (ghi chu dai han): {'Co' if co_mem_md else 'Khong'}")

    # 3. Kiem tra agent/context_engine.py (Compaction & Memory handoff)
    tep_engine = duong_dan_goc / "agent" / "context_engine.py"
    co_engine = tep_engine.exists()
    print(f"\n[3] agent/context_engine.py: {'Co mat' if co_engine else 'Khong tim thay'}")
    if co_engine:
        noi_dung_eng = tep_engine.read_text(encoding="utf-8", errors="ignore")
        co_sanitize = "def sanitize_memory_context" in noi_dung_eng
        co_handoff = "memory_context: str" in noi_dung_eng
        print(f"    - Ham sanitize_memory_context()   : {'Co' if co_sanitize else 'Khong'}")
        print(f"    - Truyen memory_context vao nen   : {'Co' if co_handoff else 'Khong'}")

    # 4. Kiem tra thu muc luu tru thuc te ~/.hermes/memories
    tm_home = Path.home() / ".hermes"
    tm_mem = tm_home / "memories"
    print(f"\n[4] Thu muc du lieu nguoi dung: {tm_home}")
    print(f"    - ~/.hermes ton tai               : {'Co' if tm_home.exists() else 'Chua khoi tao'}")
    print(f"    - ~/.hermes/memories ton tai      : {'Co' if tm_mem.exists() else 'Chua co'}")

    # 5. Kiem tra cac provider bo nho ngoai (plugins/memory)
    tm_plugins_mem = duong_dan_goc / "plugins" / "memory"
    print(f"\n[5] Plugins Memory (plugins/memory):")
    if tm_plugins_mem.exists():
        ds_ncc = [p.name for p in tm_plugins_mem.iterdir() if p.is_dir()]
        print(f"    - Cac provider tren o dia         : {', '.join(ds_ncc)}")
    else:
        print("    - Trang thai                      : Da bi script don dep truoc do xoa khoi o dia (van con trong Git)")

    print("============================================================================")

if __name__ == "__main__":
    kiem_tra_he_thong_memory()
