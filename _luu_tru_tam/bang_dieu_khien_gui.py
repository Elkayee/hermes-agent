# bang_dieu_khien_gui.py
# Chuyen huong va tich hop toan bo giao dien Dashboard Context & Harness moi nhat

import sys
from pathlib import Path

# Dam bao terminal Windows ho tro UTF-8
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

# Nap va chay ma nguon dashboard moi nhat
tm_goc = Path(__file__).resolve().parent.parent
tep_moi = tm_goc / "bang_dieu_khien_context_harness.py"

if tep_moi.exists():
    import importlib.util
    dac_ta = importlib.util.spec_from_file_location("bang_dieu_khien_context_harness", str(tep_moi))
    mod = importlib.util.module_from_spec(dac_ta)
    dac_ta.loader.exec_module(mod)
    mod.khoi_chay_gui()
else:
    print(f"[!] Khong tim thay {tep_moi}")
