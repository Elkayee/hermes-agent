# api_dashboard_brain.py
# Module backend xu ly cac tac vu 1-click tren Dashboard Web GUI cho Hermes & Brain

import os
import sys
import json
from pathlib import Path

# Dam bao terminal Windows ho tro UTF-8
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

# Nap cac ham toi uu tu toi_uu_brain_hermes.py
sys.path.insert(0, str(Path(__file__).resolve().parent))
try:
    from toi_uu_brain_hermes import (
        phan_tich_kho_brain,
        thu_hoach_tri_thuc_tu_brain,
        don_dep_rac_brain
    )
except ImportError:
    pass

try:
    from dong_bo_context_tu_dong import cap_nhat_context_md, doc_yeu_cau_gan_nhat_tu_transcript
except ImportError:
    pass


_bo_nho_dem_brain = {
    "thoi_gian": 0,
    "du_lieu": None
}


def lay_thong_ke_brain_nhanh():
    """Lay so lieu phan tich kho du lieu brain cho Dashboard (cache 60 giay)."""
    global _bo_nho_dem_brain
    bay_gio = time.time()
    if _bo_nho_dem_brain["du_lieu"] and (bay_gio - _bo_nho_dem_brain["thoi_gian"] < 60):
        return _bo_nho_dem_brain["du_lieu"]

    try:
        from toi_uu_brain_hermes import phan_tich_kho_brain
        dl = phan_tich_kho_brain()
        _bo_nho_dem_brain["du_lieu"] = dl
        _bo_nho_dem_brain["thoi_gian"] = bay_gio
        return dl
    except Exception as loi:
        return {"loi": str(loi)}


def xu_ly_thu_hoach_tri_thuc():
    """Kich hoat thu hoach 10 chu de tri thuc moi nhat tu Brain vao MEMORY.md."""
    try:
        from toi_uu_brain_hermes import thu_hoach_tri_thuc_tu_brain
        ok = thu_hoach_tri_thuc_tu_brain(gioi_han_phien=10)
        return {"thanh_cong": ok, "thong_bao": "Đã thu hoạch thành công tri thức vào MEMORY.md"}
    except Exception as loi:
        return {"thanh_cong": False, "thong_bao": f"Lỗi thu hoạch: {str(loi)}"}


def xu_ly_don_dep_steps_rac():
    """Kich hoat don dep cac tep output.txt lon cua cac phien cu trong steps/."""
    try:
        from toi_uu_brain_hermes import don_dep_rac_brain
        # Thuc thi don dep that su (chi_kiem_tra=False)
        don_dep_rac_brain(giu_lai_phien_gan_nhat=10, chi_kiem_tra=False)
        return {"thanh_cong": True, "thong_bao": "Đã dọn dẹp các tệp output.txt rác thành công"}
    except Exception as loi:
        return {"thanh_cong": False, "thong_bao": f"Lỗi dọn dẹp: {str(loi)}"}


def xu_ly_dong_bo_context_moi_nhat():
    """Kich hoat dong bo cac yeu cau moi nhat vao CONTEXT.md."""
    try:
        from dong_bo_context_tu_dong import doc_yeu_cau_gan_nhat_tu_transcript, cap_nhat_context_md
        # Tim transcript moi nhat trong brain
        tm_brain = Path(r"C:\Users\Home33\.gemini\antigravity-cli\brain")
        ds_tm = []
        if tm_brain.exists():
            for tm in tm_brain.iterdir():
                if tm.is_dir():
                    try:
                        ds_tm.append((tm.stat().st_mtime, tm))
                    except Exception:
                        pass
        ds_tm.sort(key=lambda x: x[0], reverse=True)
        if ds_tm:
            tm_moi = ds_tm[0][1]
            tep_ts = tm_moi / ".system_generated" / "logs" / "transcript.jsonl"
            ds_yc = doc_yeu_cau_gan_nhat_tu_transcript(str(tep_ts))
            cap_nhat_context_md(tm_moi.name, ds_yc, in_thong_bao=False)
            return {"thanh_cong": True, "thong_bao": f"Đã đồng bộ phiên '{tm_moi.name[:8]}' vào CONTEXT.md"}
        return {"thanh_cong": False, "thong_bao": "Không tìm thấy phiên gần nhất"}
    except Exception as loi:
        return {"thanh_cong": False, "thong_bao": f"Lỗi đồng bộ: {str(loi)}"}
