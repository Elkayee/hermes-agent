# bang_dieu_khien_context_harness.py
# Bang dieu khien Web GUI cap nhat: Tich hop day du Context Hermes va Harness Benchmark

import os
import sys
import json
import time
import webbrowser
from pathlib import Path
from http.server import ThreadingHTTPServer, BaseHTTPRequestHandler

# Dam bao terminal Windows ho tro UTF-8
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

# Cong dich vu mac dinh
CONG_DICH_VU = 7890


def lay_thu_muc_goc():
    """Lay duong dan thu muc goc cua du an."""
    return Path(__file__).resolve().parent


def doc_nhat_ky_harness():
    """Doc nhat ky kich hoat tu cac tep log jsonl."""
    tm_goc = lay_thu_muc_goc()
    ds_nk = []
    ds_tep = [
        tm_goc / ".agents" / "nhat_ky_harness.jsonl",
        tm_goc / "_luu_tru_tam" / "nhat_ky_harness.jsonl",
        tm_goc / ".agents" / ".agents" / "nhat_ky_harness.jsonl"
    ]

    for tep in ds_tep:
        if tep.exists():
            try:
                with open(tep, "r", encoding="utf-8", errors="ignore") as f:
                    for dong in f:
                        xau = dong.strip()
                        if xau:
                            try:
                                ds_nk.append(json.loads(xau))
                            except Exception:
                                pass
            except Exception:
                pass

    ds_nk.sort(key=lambda x: x.get("thoi_gian", 0), reverse=True)
    return ds_nk


def doc_ket_qua_danh_gia():
    """Doc ket qua benchmark tu cac tep bao cao (uu tien benchmark vong doi skills moi nhat)."""
    tm_goc = lay_thu_muc_goc()
    ds_tep = [
        tm_goc / "_luu_tru_tam" / "ket_qua_benchmark_skills.json",
        tm_goc / "_luu_tru_tam" / "ket_qua_harness_song_song.json",
        tm_goc / "ket_qua_harness_song_song.json",
        tm_goc / ".agents" / "ket_qua_harness_song_song.json"
    ]
    for tep in ds_tep:
        if tep.exists():
            try:
                with open(tep, "r", encoding="utf-8", errors="ignore") as f:
                    return json.load(f)
            except Exception:
                pass
    return {}


def doc_tap_kiem_thu():
    """Doc danh sach cac cau test trong bo test mau, nang cao va vong doi skills."""
    tm_goc = lay_thu_muc_goc()
    ds_kt = []
    ds_tep = [
        (tm_goc / "_luu_tru_tam" / "tap_kiem_thu_skills_lifecycle.jsonl", "Vòng đời Skill"),
        (tm_goc / "_luu_tru_tam" / "tap_kiem_thu_mau.jsonl", "Mẫu chuẩn"),
        (tm_goc / "_luu_tru_tam" / "tap_kiem_thu_nang_cao.jsonl", "Nâng cao"),
        (tm_goc / "tap_kiem_thu_mau.jsonl", "Mẫu chuẩn"),
        (tm_goc / "tap_kiem_thu_nang_cao.jsonl", "Nâng cao")
    ]

    da_doc = set()
    for tep, loai in ds_tep:
        if tep.exists() and str(tep) not in da_doc:
            da_doc.add(str(tep))
            try:
                with open(tep, "r", encoding="utf-8", errors="ignore") as f:
                    for dong in f:
                        xau = dong.strip()
                        if xau:
                            try:
                                obj = json.loads(xau)
                                obj["loai_tap"] = loai
                                ds_kt.append(obj)
                            except Exception:
                                pass
            except Exception:
                pass
    return ds_kt


def doc_bo_nho_context():
    """Doc toan bo noi dung bo nho USER.md, MEMORY.md, CONTEXT.md va tinh thong so Hermes Context Engine."""
    tm_goc = lay_thu_muc_goc()
    tm_mem = tm_goc / ".agents" / "memory"
    
    ket_qua = {
        "user_md": "",
        "memory_md": "",
        "context_md": "",
        "context_engine": {
            "gioi_han_an_toan": 6000,
            "giu_dau": 4000,
            "giu_cuoi": 1500,
            "tong_ky_tu": 0,
            "dem_tu": 0,
            "uoc_luong_token": 0,
            "trang_thai_nen": "CHUAN_AN_TOAN",
            "ti_le_an_toan": 100.0,
            "van_ban_mo_phong": ""
        }
    }

    # 1. Doc USER.md
    tep_user = tm_mem / "USER.md"
    if tep_user.exists():
        try:
            ket_qua["user_md"] = tep_user.read_text(encoding="utf-8", errors="ignore")
        except Exception:
            pass

    # 2. Doc MEMORY.md
    tep_mem_file = tm_mem / "MEMORY.md"
    if tep_mem_file.exists():
        try:
            ket_qua["memory_md"] = tep_mem_file.read_text(encoding="utf-8", errors="ignore")
        except Exception:
            pass

    # 3. Doc CONTEXT.md
    tep_ctx = tm_mem / "CONTEXT.md"
    if tep_ctx.exists():
        try:
            ket_qua["context_md"] = tep_ctx.read_text(encoding="utf-8", errors="ignore")
        except Exception:
            pass

    # 4. Tinh toan mo phong Hermes Context Engine
    xau_gop = (
        "=== [USER PROFILE & PREFERENCES] ===\n" + ket_qua["user_md"] + "\n\n" +
        "=== [PROJECT LONG-TERM MEMORY] ===\n" + ket_qua["memory_md"] + "\n\n" +
        "=== [ACTIVE SESSION CONTEXT] ===\n" + ket_qua["context_md"]
    )
    
    dem_kt = len(xau_gop)
    dem_tu = len(xau_gop.split())
    uoc_token = int(dem_kt / 3.5)  # Uoc tinh trung binh 3.5 ky tu tren 1 token
    
    gioi_han = 6000
    giu_dau = 4000
    giu_cuoi = 1500

    if dem_kt > gioi_han:
        trang_thai = "DA_NEN_CAT_TIA"
        xau_mo_phong = xau_gop[:giu_dau] + "\n\n[... HERMES CONTEXT ENGINE ĐÃ NÉN BỚT ĐOẠN GIỮA ĐỂ TRÁNH TRÀN BỘ NHỚ ...]\n\n" + xau_gop[-giu_cuoi:]
        ti_le = round((gioi_han / dem_kt) * 100, 1)
    else:
        trang_thai = "CHUAN_AN_TOAN"
        xau_mo_phong = xau_gop
        ti_le = 100.0

    ket_qua["context_engine"]["tong_ky_tu"] = dem_kt
    ket_qua["context_engine"]["dem_tu"] = dem_tu
    ket_qua["context_engine"]["uoc_luong_token"] = uoc_token
    ket_qua["context_engine"]["trang_thai_nen"] = trang_thai
    ket_qua["context_engine"]["ti_le_an_toan"] = ti_le
    ket_qua["context_engine"]["van_ban_mo_phong"] = xau_mo_phong

    return ket_qua


def doc_danh_sach_ky_nang_va_telemetry():
    """Doc toan bo skills kem telemetry tan suat su dung va trang thai active/deactivated."""
    try:
        sys.path.insert(0, str(lay_thu_muc_goc() / ".agents" / "scripts"))
        from quan_ly_vong_doi_skills_telemetry import dong_bo_va_phan_tich_skills
        return dong_bo_va_phan_tich_skills()
    except Exception as loi:
        try:
            from quet_tat_ca_skills import quet_toan_bo_skills_he_thong
            ds = quet_toan_bo_skills_he_thong()
            return {"tong_skills": len(ds), "so_active": len(ds), "so_deactivated": 0, "top_skills": [], "danh_sach": ds}
        except Exception:
            return {"tong_skills": 0, "so_active": 0, "so_deactivated": 0, "top_skills": [], "danh_sach": []}


# Giao dien HTML, CSS, Javascript truc quan
TRANG_GIAO_DIEN = """<!DOCTYPE html>
<html lang="vi">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Hermes & AGY Context Harness Dashboard</title>
    <style>
        :root {
            --nen: #090d16;
            --nen-phu: #0f172a;
            --hop: #1e293b;
            --hop-sang: #273549;
            --chu: #f8fafc;
            --mo: #94a3b8;
            --xanh: #10b981;
            --lam: #3b82f6;
            --tim: #8b5cf6;
            --cam: #f59e0b;
            --do: #ef4444;
            --vien: #334155;
            --bong: 0 8px 24px rgba(0, 0, 0, 0.4);
        }
        * { box-sizing: border-box; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", sans-serif;
            background: radial-gradient(circle at top right, #1e1b4b 0%, var(--nen) 60%);
            color: var(--chu);
            margin: 0;
            padding: 24px;
            min-height: 100vh;
        }
        .khung {
            max-width: 1360px;
            margin: 0 auto;
        }
        .dau-trang {
            display: flex;
            justify-content: space-between;
            align-items: center;
            border-bottom: 1px solid var(--vien);
            padding-bottom: 20px;
            margin-bottom: 24px;
            flex-wrap: wrap;
            gap: 16px;
        }
        .tieu-de {
            font-size: 24px;
            font-weight: 800;
            display: flex;
            align-items: center;
            gap: 12px;
            letter-spacing: -0.5px;
        }
        .tieu-de .chu-sang {
            background: linear-gradient(135deg, #60a5fa 0%, #c084fc 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }
        .den-bao {
            width: 12px;
            height: 12px;
            background-color: var(--xanh);
            border-radius: 50%;
            display: inline-block;
            box-shadow: 0 0 14px var(--xanh);
            animation: nhap_nhay 1.8s infinite ease-in-out;
        }
        @keyframes nhap_nhay {
            0%, 100% { opacity: 0.3; transform: scale(0.9); }
            50% { opacity: 1; transform: scale(1.1); }
        }
        .thanh-nut {
            display: flex;
            align-items: center;
            gap: 12px;
        }
        .nut-bam {
            background-color: var(--hop);
            border: 1px solid var(--vien);
            color: var(--chu);
            padding: 8px 16px;
            border-radius: 8px;
            cursor: pointer;
            font-size: 13px;
            font-weight: 600;
            transition: all 0.2s;
            display: inline-flex;
            align-items: center;
            gap: 6px;
        }
        .nut-bam:hover {
            background-color: var(--hop-sang);
            border-color: var(--lam);
            transform: translateY(-1px);
        }
        .nut-lam {
            background: linear-gradient(135deg, #2563eb, #3b82f6);
            border: none;
        }
        .nut-lam:hover {
            background: linear-gradient(135deg, #1d4ed8, #2563eb);
        }
        
        /* Grid KPI Cards */
        .the-chi-so {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(210px, 1fr));
            gap: 16px;
            margin-bottom: 24px;
        }
        .hop-chi-so {
            background: rgba(30, 41, 59, 0.7);
            backdrop-filter: blur(12px);
            border: 1px solid var(--vien);
            border-radius: 12px;
            padding: 18px;
            box-shadow: var(--bong);
            transition: transform 0.2s, border-color 0.2s;
        }
        .hop-chi-so:hover {
            transform: translateY(-2px);
            border-color: var(--lam);
        }
        .ten-chi-so {
            color: var(--mo);
            font-size: 12px;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            margin-bottom: 6px;
        }
        .gia-tri-chi-so {
            font-size: 26px;
            font-weight: 800;
            color: var(--chu);
            display: flex;
            align-items: baseline;
            gap: 6px;
        }
        .gia-tri-chi-so small {
            font-size: 13px;
            font-weight: 500;
            color: var(--mo);
        }

        /* Tabs */
        .dieu-huong-tab {
            display: flex;
            gap: 8px;
            border-bottom: 1px solid var(--vien);
            margin-bottom: 20px;
            overflow-x: auto;
            padding-bottom: 2px;
        }
        .nut-tab {
            background: transparent;
            border: none;
            color: var(--mo);
            padding: 10px 18px;
            font-size: 14px;
            font-weight: 600;
            cursor: pointer;
            border-bottom: 2px solid transparent;
            transition: all 0.2s;
            display: flex;
            align-items: center;
            gap: 8px;
            white-space: nowrap;
        }
        .nut-tab:hover {
            color: var(--chu);
        }
        .nut-tab.kich-hoat {
            color: var(--lam);
            border-bottom-color: var(--lam);
            background: rgba(59, 130, 246, 0.08);
            border-radius: 6px 6px 0 0;
        }
        .noi-dung-tab {
            display: none;
            animation: hien_dan 0.25s ease-out;
        }
        .noi-dung-tab.kich-hoat {
            display: block;
        }
        @keyframes hien_dan {
            from { opacity: 0; transform: translateY(6px); }
            to { opacity: 1; transform: translateY(0); }
        }

        /* Panel Boxes */
        .hop-panel {
            background: rgba(30, 41, 59, 0.6);
            border: 1px solid var(--vien);
            border-radius: 12px;
            padding: 20px;
            margin-bottom: 20px;
            box-shadow: var(--bong);
        }
        .tieu-de-panel {
            font-size: 16px;
            font-weight: 700;
            margin-top: 0;
            margin-bottom: 16px;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }

        /* Tables */
        table {
            width: 100%;
            border-collapse: collapse;
            font-size: 13px;
        }
        th, td {
            padding: 12px 14px;
            text-align: left;
            border-bottom: 1px solid var(--vien);
        }
        th {
            background-color: rgba(15, 23, 42, 0.8);
            color: var(--mo);
            font-weight: 600;
            text-transform: uppercase;
            font-size: 11px;
            letter-spacing: 0.5px;
        }
        tr:hover td {
            background-color: rgba(51, 65, 85, 0.3);
        }

        /* Badges */
        .huy-hieu {
            display: inline-flex;
            align-items: center;
            gap: 4px;
            padding: 4px 8px;
            border-radius: 6px;
            font-size: 11px;
            font-weight: 700;
            letter-spacing: 0.3px;
        }
        .huy-hieu-xanh { background: rgba(16, 185, 129, 0.15); color: #34d399; border: 1px solid rgba(16, 185, 129, 0.3); }
        .huy-hieu-do { background: rgba(239, 68, 68, 0.15); color: #f87171; border: 1px solid rgba(239, 68, 68, 0.3); }
        .huy-hieu-lam { background: rgba(59, 130, 246, 0.15); color: #60a5fa; border: 1px solid rgba(59, 130, 246, 0.3); }
        .huy-hieu-tim { background: rgba(139, 92, 246, 0.15); color: #c084fc; border: 1px solid rgba(139, 92, 246, 0.3); }
        .huy-hieu-cam { background: rgba(245, 158, 11, 0.15); color: #fbbf24; border: 1px solid rgba(245, 158, 11, 0.3); }

        /* Code & Pre Blocks */
        pre {
            background-color: #0b0f19;
            border: 1px solid var(--vien);
            border-radius: 8px;
            padding: 14px;
            font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace;
            font-size: 12px;
            line-height: 1.5;
            color: #e2e8f0;
            overflow-x: auto;
            white-space: pre-wrap;
            word-break: break-word;
            max-height: 420px;
        }

        /* Subgrids */
        .luoi-3-cot {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(360px, 1fr));
            gap: 16px;
        }
        .ma_phien {
            font-family: monospace;
            color: var(--mo);
            font-size: 12px;
        }
        .thanh-tien-do-khung {
            background-color: rgba(51, 65, 85, 0.5);
            border-radius: 999px;
            height: 8px;
            width: 100%;
            overflow: hidden;
            margin-top: 8px;
        }
        .thanh-tien-do {
            height: 100%;
            background: linear-gradient(90deg, #10b981, #3b82f6);
            border-radius: 999px;
            transition: width 0.4s ease;
        }
    </style>
</head>
<body>
    <div class="khung">
        <!-- Header -->
        <div class="dau-trang">
            <div class="tieu-de">
                <span class="den-bao"></span>
                <span class="chu-sang">Hermes & AGY</span>
                <span>Context & Harness Dashboard</span>
            </div>
            <div class="thanh-nut">
                <span id="nhan_trang_thai" class="huy-hieu huy-hieu-xanh">ĐANG HOẠT ĐỘNG (PORT 7890)</span>
                <button class="nut-bam nut-lam" onclick="cap_nhat_du_lieu()">🔄 Làm Mới</button>
            </div>
        </div>

        <!-- KPI Cards -->
        <div class="the-chi-so">
            <div class="hop-chi-so">
                <div class="ten-chi-so">Tỷ Lệ Đạt Benchmark</div>
                <div class="gia-tri-chi-so" id="chi_so_ti_le">--%</div>
                <div class="thanh-tien-do-khung">
                    <div class="thanh-tien-do" id="thanh_ti_le" style="width: 0%"></div>
                </div>
            </div>
            <div class="hop-chi-so">
                <div class="ten-chi-so">Thời Gian Trung Bình</div>
                <div class="gia-tri-chi-so" id="chi_so_thoi_gian">--s</div>
                <small id="chi_so_tong_tg" style="color: var(--mo);">Tổng: --s</small>
            </div>
            <div class="hop-chi-so">
                <div class="ten-chi-so">Tổng Token Tiêu Thụ</div>
                <div class="gia-tri-chi-so" id="chi_so_token">--</div>
                <small style="color: var(--mo);">In/Out/Thinking/Cache</small>
            </div>
            <div class="hop-chi-so">
                <div class="ten-chi-so">Chi Phí Ước Tính</div>
                <div class="gia-tri-chi-so" id="chi_so_chi_phi">$0.00</div>
                <small style="color: var(--mo);">Tối ưu hóa token</small>
            </div>
            <div class="hop-chi-so">
                <div class="ten-chi-so">Lần Trigger Harness</div>
                <div class="gia-tri-chi-so" id="chi_so_trigger">--</div>
                <small style="color: var(--mo);">Nhật ký AGY tự động</small>
            </div>
            <div class="hop-chi-so">
                <div class="ten-chi-so">Hermes Context Engine</div>
                <div class="gia-tri-chi-so" id="chi_so_context">-- kt</div>
                <small id="chi_so_trang_thai_ctx" class="huy-hieu huy-hieu-xanh">CHUẨN AN TOÀN</small>
            </div>
            <div class="hop-chi-so">
                <div class="ten-chi-so">Kho Dữ Liệu Brain</div>
                <div class="gia-tri-chi-so" id="chi_so_brain" style="color: #38bdf8;">-- MB</div>
                <small id="chi_so_phien_brain" style="color: var(--mo);">-- phiên / -- tệp</small>
            </div>
        </div>

        <!-- Navigation Tabs -->
        <div class="dieu-huong-tab">
            <button class="nut-tab kich-hoat" onclick="chuyen_tab('tab_benchmark', this)">📊 Harness Benchmark</button>
            <button class="nut-tab" onclick="chuyen_tab('tab_context', this)">🧠 Hermes Context & Memory</button>
            <button class="nut-tab" onclick="chuyen_tab('tab_brain', this)">🚀 Kho Tri Thức Brain & Tối Ưu</button>
            <button class="nut-tab" onclick="chuyen_tab('tab_test_suites', this)">🧪 Tập Bài Kiểm Thử</button>
            <button class="nut-tab" onclick="chuyen_tab('tab_nhat_ky', this)">⚡ Nhật Ký Trigger Realtime</button>
            <button class="nut-tab" onclick="chuyen_tab('tab_ky_nang', this)">🛠️ Kỹ Năng AGY (Skills)</button>
        </div>

        <!-- TAB 1: BENCHMARK -->
        <div id="tab_benchmark" class="noi-dung-tab kich-hoat">
            <div class="hop-panel">
                <div class="tieu-de-panel">
                    <span>Kết Quả Kiểm Thử Đa Luồng Song Song (Harness Benchmark)</span>
                    <span id="nhan_tong_so_test" class="huy-hieu huy-hieu-lam">-- bài test</span>
                </div>
                <div style="overflow-x: auto;">
                    <table>
                        <thead>
                            <tr>
                                <th>Mã Test (ID)</th>
                                <th>Kết Quả</th>
                                <th>Thời Gian</th>
                                <th>Token Vào</th>
                                <th>Token Ra</th>
                                <th>Token Suy Nghĩ</th>
                                <th>Tổng Token</th>
                                <th>Chi Phí</th>
                                <th>Phản Hồi Mẫu</th>
                            </tr>
                        </thead>
                        <tbody id="bang_benchmark">
                            <tr><td colspan="9" style="text-align: center; color: var(--mo);">Đang tải dữ liệu benchmark...</td></tr>
                        </tbody>
                    </table>
                </div>
            </div>
        </div>

        <!-- TAB 2: CONTEXT & MEMORY -->
        <div id="tab_context" class="noi-dung-tab">
            <div class="hop-panel">
                <div class="tieu-de-panel">
                    <span>🛡️ Giám Sát Hermes Context Engine (Giới hạn: 6.000 ký tự | Giữ 4.000 đầu + 1.500 cuối)</span>
                    <span id="nhan_tinh_trang_ctx" class="huy-hieu huy-hieu-xanh">AN TOÀN</span>
                </div>
                <p style="color: var(--mo); font-size: 13px; margin-top: 0;">
                    Hermes Context Engine tự động kiểm soát dung lượng để ngăn chặn tràn token và suy giảm độ chú ý của mô hình lớn. Đoạn văn bản dưới đây thể hiện chính xác nội dung được hook <code>PreInvocation</code> nạp tự động vào mỗi lượt gọi của AGY:
                </p>
                <pre id="khoi_mo_phong_ctx">Đang đọc context...</pre>
            </div>

            <div class="luoi-3-cot">
                <div class="hop-panel">
                    <div class="tieu-de-panel">
                        <span>👤 Hồ Sơ Người Dùng (USER.md)</span>
                        <span class="huy-hieu huy-hieu-lam">Quy tắc cốt lõi</span>
                    </div>
                    <pre id="khoi_user_md">Đang tải...</pre>
                </div>
                <div class="hop-panel">
                    <div class="tieu-de-panel">
                        <span>📚 Bộ Nhớ Dài Hạn (MEMORY.md)</span>
                        <span class="huy-hieu huy-hieu-tim">Trí thức dự án</span>
                    </div>
                    <pre id="khoi_memory_md">Đang tải...</pre>
                </div>
                <div class="hop-panel">
                    <div class="tieu-de-panel">
                        <span>🔄 Phiên Làm Việc (CONTEXT.md)</span>
                        <span class="huy-hieu huy-hieu-cam">Trạng thái hiện tại</span>
                    </div>
                    <pre id="khoi_context_md">Đang tải...</pre>
                </div>
            </div>
        </div>

        <!-- TAB BRAIN: KHO TRI THUC & TOI UU -->
        <div id="tab_brain" class="noi-dung-tab">
            <div class="the-chi-so" style="margin-bottom: 20px;">
                <div class="hop-chi-so">
                    <div class="ten-chi-so">Số Phiên Làm Việc</div>
                    <div class="gia-tri-chi-so" id="brain_phien">--</div>
                    <small style="color: var(--mo);">152 phiên lịch sử AGY</small>
                </div>
                <div class="hop-chi-so">
                    <div class="ten-chi-so">Tổng Số Tệp Tin</div>
                    <div class="gia-tri-chi-so" id="brain_tep">--</div>
                    <small style="color: var(--mo);">Quản lý trong brain/</small>
                </div>
                <div class="hop-chi-so">
                    <div class="ten-chi-so">Tệp Steps / Output Rác</div>
                    <div class="gia-tri-chi-so" id="brain_steps" style="color: var(--cam);">--</div>
                    <small style="color: var(--cam);">Có thể dọn dẹp an toàn</small>
                </div>
                <div class="hop-chi-so">
                    <div class="ten-chi-so">Dung Lượng Chiếm Dụng</div>
                    <div class="gia-tri-chi-so" id="brain_dung_luong">-- MB</div>
                    <small style="color: var(--mo);">Dung lượng thực tế trên đĩa</small>
                </div>
            </div>

            <div class="hop-panel">
                <div class="tieu-de-panel">
                    <span>⚡ Bảng Điều Khiển Tác Vụ 1-Click (Hermes Brain Action Hub)</span>
                    <span id="nhan_trang_thai_tac_vu" class="huy-hieu huy-hieu-xanh">SẴN SÀNG</span>
                </div>
                <p style="color: var(--mo); font-size: 13px; margin-top: 0;">
                    Sử dụng Hermes Context Engine để tự động khai thác bài học từ các phiên cũ vào bộ nhớ dài hạn, hoặc dọn dẹp các tệp output tạm thời mà vẫn bảo tồn 100% lịch sử trò chuyện.
                </p>
                <div style="display: flex; gap: 12px; flex-wrap: wrap; margin-bottom: 8px;">
                    <button class="nut-bam nut-lam" onclick="goi_tac_vu('thu_hoach', this)">📥 Thu Hoạch Tri Thức (Harvest Brain)</button>
                    <button class="nut-bam" style="background: linear-gradient(135deg, #d97706, #f59e0b); border: none; color: white;" onclick="goi_tac_vu('don_dep', this)">🧹 Dọn Dẹp File Rác (Prune Steps)</button>
                    <button class="nut-bam" style="background: linear-gradient(135deg, #059669, #10b981); border: none; color: white;" onclick="goi_tac_vu('dong_bo', this)">🔄 Đồng Bộ Ngữ Cảnh CONTEXT.md</button>
                </div>
                <div id="thong_bao_tac_vu" style="margin-top: 10px; font-size: 13px; font-weight: 600; display: none;"></div>
            </div>

            <div class="hop-panel">
                <div class="tieu-de-panel">
                    <span>📚 Tri Thức Lịch Sử Đã Thu Hoạch Từ Brain (Trong MEMORY.md)</span>
                    <span class="huy-hieu huy-hieu-tim">Tự động nạp vào AGY</span>
                </div>
                <pre id="khoi_tri_thuc_brain" style="max-height: 400px; overflow-y: auto;">Đang tải tri thức thu hoạch...</pre>
            </div>
        </div>

        <!-- TAB 3: TEST SUITES -->
        <div id="tab_test_suites" class="noi-dung-tab">
            <div class="hop-panel">
                <div class="tieu-de-panel">
                    <span>Danh Sách Bài Kiểm Thử Benchmark Có Sẵn (Test Suites)</span>
                    <span id="nhan_tong_test_suites" class="huy-hieu huy-hieu-lam">-- bài</span>
                </div>
                <div style="overflow-x: auto;">
                    <table>
                        <thead>
                            <tr>
                                <th>Loại Tập</th>
                                <th>Mã Bài (ID)</th>
                                <th>Yêu Cầu (Prompt Test)</th>
                                <th>Đáp Án Kỳ Vọng (Expected)</th>
                            </tr>
                        </thead>
                        <tbody id="bang_test_suites">
                            <tr><td colspan="4" style="text-align: center; color: var(--mo);">Đang tải tập kiểm thử...</td></tr>
                        </tbody>
                    </table>
                </div>
            </div>
        </div>

        <!-- TAB 4: REALTIME TRIGGER LOGS -->
        <div id="tab_nhat_ky" class="noi-dung-tab">
            <div class="hop-panel">
                <div class="tieu-de-panel">
                    <span>Nhật Ký Kích Hoạt Tự Động [HARNESS TRIGGERED]</span>
                    <span id="nhan_dem_nhat_ky" class="huy-hieu huy-hieu-xanh">-- sự kiện</span>
                </div>
                <div style="overflow-x: auto; max-height: 540px;">
                    <table>
                        <thead>
                            <tr>
                                <th>Thời Gian</th>
                                <th>Lượt (Turn)</th>
                                <th>Mã Phiên (Session ID)</th>
                                <th>Skill Kích Hoạt</th>
                                <th>Trạng Thái</th>
                            </tr>
                        </thead>
                        <tbody id="bang_nhat_ky">
                            <tr><td colspan="5" style="text-align: center; color: var(--mo);">Đang tải nhật ký...</td></tr>
                        </tbody>
                    </table>
                </div>
            </div>
        </div>

        <!-- TAB 5: SKILLS -->
        <div id="tab_ky_nang" class="noi-dung-tab">
            <!-- Telemetry KPI Mini-Cards -->
            <div class="the-chi-so" style="margin-bottom: 18px;">
                <div class="hop-chi-so">
                    <div class="ten-chi-so">Đang Hoạt Động (Active)</div>
                    <div class="gia-tri-chi-so" id="kn_so_active" style="color: #34d399;">--</div>
                    <small style="color: var(--mo);">Sẵn sàng định tuyến</small>
                </div>
                <div class="hop-chi-so">
                    <div class="ten-chi-so">Đã Tạm Ngưng (Deactivated)</div>
                    <div class="gia-tri-chi-so" id="kn_so_deact" style="color: #f87171;">--</div>
                    <small style="color: var(--mo);">Giảm nhiễu context</small>
                </div>
                <div class="hop-chi-so">
                    <div class="ten-chi-so">Tỷ Lệ Từng Dùng</div>
                    <div class="gia-tri-chi-so" id="kn_ti_le_dung" style="color: #60a5fa;">--%</div>
                    <small id="kn_so_da_dung" style="color: var(--mo);">--/-- skills đã gọi</small>
                </div>
                <div class="hop-chi-so">
                    <div class="ten-chi-so">Kỹ Năng Ngủ Đông (Dormant)</div>
                    <div class="gia-tri-chi-so" id="kn_so_dormant" style="color: #fbbf24;">--</div>
                    <small style="color: var(--mo);">0 lượt dùng lịch sử</small>
                </div>
            </div>

            <!-- Top Skills Card -->
            <div class="hop-panel" style="margin-bottom: 20px;">
                <div class="tieu-de-panel">
                    <span>🔥 Top Kỹ Năng Được AGY Kích Hoạt Nhiều Nhất (Harness Telemetry)</span>
                    <span class="huy-hieu huy-hieu-lam">Dữ liệu từ 153 phiên AGY</span>
                </div>
                <div id="hop_top_skills" style="display: flex; gap: 10px; flex-wrap: wrap;">
                    <span style="color: var(--mo); font-size: 13px;">Đang tải xếp hạng...</span>
                </div>
            </div>

            <!-- Main Skills Table Panel -->
            <div class="hop-panel">
                <div class="tieu-de-panel">
                    <span>Hệ Sinh Thái Kỹ Năng & Quản Lý Vòng Đời (Skills Lifecycle)</span>
                    <div style="display: flex; gap: 8px;">
                        <button class="nut-bam" style="background: rgba(245, 158, 11, 0.15); border: 1px solid rgba(245, 158, 11, 0.4); color: #fbbf24; font-size: 12px; padding: 6px 12px;" onclick="deactive_ctf_ngu_dong()">🧹 Tạm Ngưng Nhóm CTF Ngủ Đông</button>
                        <span id="nhan_dem_skills" class="huy-hieu huy-hieu-tim">-- skills</span>
                    </div>
                </div>

                <div style="display: flex; gap: 12px; margin-bottom: 16px; flex-wrap: wrap; align-items: center;">
                    <div style="flex: 1; min-width: 280px;">
                        <input type="text" id="tim_kiem_skill" placeholder="🔍 Tìm nhanh kỹ năng (ví dụ: reverse, ida, pentest, api, design, tdd, find-skills...)" 
                               oninput="loc_danh_sach_skills()"
                               style="width: 100%; background: rgba(15, 23, 42, 0.8); border: 1px solid var(--vien); color: var(--chu); padding: 10px 14px; border-radius: 8px; font-size: 13px; outline: none;">
                    </div>
                    <div style="display: flex; gap: 6px;">
                        <button class="nut-bam" id="loc_tat_ca" onclick="dat_bo_loc_trang_thai('TAT_CA', this)" style="font-size: 12px; padding: 8px 12px; border-color: var(--lam);">Tất Cả</button>
                        <button class="nut-bam" id="loc_active" onclick="dat_bo_loc_trang_thai('ACTIVE', this)" style="font-size: 12px; padding: 8px 12px;">Đang Hoạt Động</button>
                        <button class="nut-bam" id="loc_deact" onclick="dat_bo_loc_trang_thai('DEACTIVATED', this)" style="font-size: 12px; padding: 8px 12px;">Đã Tạm Ngưng</button>
                    </div>
                </div>

                <div style="overflow-x: auto; max-height: 600px;">
                    <table>
                        <thead>
                            <tr>
                                <th style="width: 200px;">Tên Kỹ Năng</th>
                                <th style="width: 105px;">Lượt Dùng</th>
                                <th style="width: 120px;">Trạng Thái</th>
                                <th style="width: 150px;">Nguồn Cung Cấp</th>
                                <th>Mô Tả Chức Năng</th>
                                <th style="width: 110px; text-align: center;">Thao Tác</th>
                            </tr>
                        </thead>
                        <tbody id="bang_skills">
                            <tr><td colspan="6" style="text-align: center; color: var(--mo);">Đang tải danh sách kỹ năng...</td></tr>
                        </tbody>
                    </table>
                </div>
            </div>
        </div>
    </div>

    <!-- Javascript xu ly du lieu Realtime -->
    <script>
        function chuyen_tab(idTab, nutEl) {
            document.querySelectorAll('.noi-dung-tab').forEach(el => el.classList.remove('kich-hoat'));
            document.querySelectorAll('.nut-tab').forEach(el => el.classList.remove('kich-hoat'));
            document.getElementById(idTab).classList.add('kich-hoat');
            nutEl.classList.add('kich-hoat');
        }

        let tat_ca_skills_cache = [];
        let che_do_loc_trang_thai = 'TAT_CA';

        function dat_bo_loc_trang_thai(loai, nutEl) {
            che_do_loc_trang_thai = loai;
            document.querySelectorAll('#loc_tat_ca, #loc_active, #loc_deact').forEach(el => {
                el.style.borderColor = 'var(--vien)';
            });
            nutEl.style.borderColor = 'var(--lam)';
            loc_danh_sach_skills();
        }

        function hien_thi_skills(ds) {
            const tbodySk = document.getElementById('bang_skills');
            if (!tbodySk) return;
            if (!ds || ds.length === 0) {
                tbodySk.innerHTML = '<tr><td colspan="6" style="text-align: center; color: var(--mo); padding: 20px;">Không tìm thấy kỹ năng phù hợp</td></tr>';
                return;
            }
            tbodySk.innerHTML = ds.map(kn => {
                const mauTag = kn.mau_tag || 'huy-hieu-tim';
                const laActive = kn.trang_thai === 'ACTIVE';
                const mauTrangThai = laActive ? 'huy-hieu-xanh' : 'huy-hieu-do';
                const chuTrangThai = laActive ? '● ACTIVE' : '○ TẠM DỪNG';
                const soLan = kn.so_lan_dung || 0;
                const mauSoLan = soLan > 0 ? 'huy-hieu-lam' : 'huy-hieu-tim';

                let nutThaoTac = '';
                if (kn.co_the_deactivate) {
                    if (laActive) {
                        nutThaoTac = `<button class="nut-bam" style="padding: 4px 8px; font-size: 11px; background: rgba(239, 68, 68, 0.15); border: 1px solid rgba(239, 68, 68, 0.3); color: #f87171;" onclick="thao_tac_skill('deactivate_skill', '${kn.ten}')">⏸️ Tạm ngưng</button>`;
                    } else {
                        nutThaoTac = `<button class="nut-bam" style="padding: 4px 8px; font-size: 11px; background: rgba(16, 185, 129, 0.15); border: 1px solid rgba(16, 185, 129, 0.3); color: #34d399;" onclick="thao_tac_skill('reactivate_skill', '${kn.ten}')">▶️ Bật lại</button>`;
                    }
                } else {
                    nutThaoTac = `<span style="color: var(--mo); font-size: 11px;">Hệ thống cố định</span>`;
                }

                return `
                    <tr style="${laActive ? '' : 'opacity: 0.65;'}">
                        <td><strong><span class="huy-hieu huy-hieu-tim" style="font-family: monospace;">${kn.ten}</span></strong></td>
                        <td><span class="huy-hieu ${mauSoLan}">${soLan} lần</span></td>
                        <td><span class="huy-hieu ${mauTrangThai}">${chuTrangThai}</span></td>
                        <td><span class="huy-hieu ${mauTag}">${kn.nguon || 'Mặc định'}</span></td>
                        <td style="color: var(--chu); font-size: 12px; line-height: 1.4;">${kn.mo_ta || ''}</td>
                        <td style="text-align: center;">${nutThaoTac}</td>
                    </tr>
                `;
            }).join('');
        }

        function loc_danh_sach_skills() {
            const o_nhap = document.getElementById('tim_kiem_skill');
            const tu_khoa = (o_nhap ? o_nhap.value : '').trim().toLowerCase();
            
            let ds_loc = tat_ca_skills_cache;
            
            // 1. Loc theo trang thai Active / Deactivated
            if (che_do_loc_trang_thai === 'ACTIVE') {
                ds_loc = ds_loc.filter(kn => kn.trang_thai === 'ACTIVE');
            } else if (che_do_loc_trang_thai === 'DEACTIVATED') {
                ds_loc = ds_loc.filter(kn => kn.trang_thai === 'DEACTIVATED');
            }

            // 2. Loc theo tu khoa tim kiem
            if (tu_khoa) {
                ds_loc = ds_loc.filter(kn => {
                    const ten = (kn.ten || '').toLowerCase();
                    const mo_ta = (kn.mo_ta || '').toLowerCase();
                    const nguon = (kn.nguon || '').toLowerCase();
                    const dd = (kn.duong_dan || '').toLowerCase();
                    return ten.includes(tu_khoa) || mo_ta.includes(tu_khoa) || nguon.includes(tu_khoa) || dd.includes(tu_khoa);
                });
            }

            hien_thi_skills(ds_loc);
            const nhanDem = document.getElementById('nhan_dem_skills');
            if (nhanDem) nhanDem.innerText = `${ds_loc.length}/${tat_ca_skills_cache.length} skills`;
        }

        async function thao_tac_skill(hanhDong, tenSkill) {
            try {
                const res = await fetch(`/api/action/${hanhDong}?ten=${encodeURIComponent(tenSkill)}`, { method: 'POST' });
                const data = await res.json();
                await cap_nhat_du_lieu();
            } catch (e) {
                alert("Lỗi thao tác skill: " + e.message);
            }
        }

        async function deactive_ctf_ngu_dong() {
            if (!confirm("Bạn có chắc muốn tạm ngưng các kỹ năng CTF Sandbox chưa từng sử dụng để giải phóng tài nguyên và tăng tốc độ định tuyến?")) return;
            try {
                const res = await fetch('/api/action/deactivate_dormant_ctf', { method: 'POST' });
                const data = await res.json();
                alert(data.thong_bao);
                await cap_nhat_du_lieu();
            } catch (e) {
                alert("Lỗi: " + e.message);
            }
        }

        async function cap_nhat_du_lieu() {
            try {
                const phan_hoi = await fetch('/api/du_lieu');
                const dl = await phan_hoi.json();

                // 1. Cap nhat KPI
                if (dl.bao_cao) {
                    const bc = dl.bao_cao;
                    const tiLe = bc.ti_le_dat !== undefined ? bc.ti_le_dat : 100;
                    document.getElementById('chi_so_ti_le').innerText = tiLe + '%';
                    document.getElementById('thanh_ti_le').style.width = tiLe + '%';
                    document.getElementById('chi_so_thoi_gian').innerText = (bc.tong_thoi_gian ? (bc.tong_thoi_gian / (bc.tong_so || 1)).toFixed(2) : 0) + 's';
                    document.getElementById('chi_so_tong_tg').innerText = 'Tổng: ' + (bc.tong_thoi_gian || 0) + 's';
                    document.getElementById('chi_so_token').innerText = (bc.tong_token || 0).toLocaleString();
                    document.getElementById('chi_so_chi_phi').innerText = '$' + (bc.tong_chi_phi ? bc.tong_chi_phi.toFixed(4) : '0.0000');
                    document.getElementById('nhan_tong_so_test').innerText = (bc.so_dat || 0) + '/' + (bc.tong_so || 0) + ' bài đạt';
                }

                // 2. Trigger count
                const tongTrigger = dl.ds_nk ? dl.ds_nk.length : 0;
                document.getElementById('chi_so_trigger').innerText = tongTrigger;
                document.getElementById('nhan_dem_nhat_ky').innerText = tongTrigger + ' sự kiện';

                // 3. Context metrics
                if (dl.bo_nho && dl.bo_nho.context_engine) {
                    const ce = dl.bo_nho.context_engine;
                    document.getElementById('chi_so_context').innerText = ce.tong_ky_tu.toLocaleString() + ' kt';
                    const theTrangThai = document.getElementById('chi_so_trang_thai_ctx');
                    theTrangThai.innerText = ce.trang_thai_nen === 'DA_NEN_CAT_TIA' ? 'ĐÃ NÉN' : 'CHUẨN AN TOÀN';
                    theTrangThai.className = 'huy-hieu ' + (ce.trang_thai_nen === 'DA_NEN_CAT_TIA' ? 'huy-hieu-cam' : 'huy-hieu-xanh');
                    
                    document.getElementById('khoi_mo_phong_ctx').innerText = ce.van_ban_mo_phong || 'Trống';
                    document.getElementById('khoi_user_md').innerText = dl.bo_nho.user_md || 'Trống';
                    document.getElementById('khoi_memory_md').innerText = dl.bo_nho.memory_md || 'Trống';
                    document.getElementById('khoi_context_md').innerText = dl.bo_nho.context_md || 'Trống';
                }

                // 4. Bang Benchmark
                const tbodyBm = document.getElementById('bang_benchmark');
                if (dl.bao_cao && dl.bao_cao.chi_tiet && dl.bao_cao.chi_tiet.length > 0) {
                    tbodyBm.innerHTML = dl.bao_cao.chi_tiet.map(bm => {
                        const mauDat = bm.dat ? 'huy-hieu-xanh' : 'huy-hieu-do';
                        const chuDat = bm.dat ? '✓ PASS' : '✗ FAIL';
                        return `
                            <tr>
                                <td><strong>${bm.id}</strong></td>
                                <td><span class="huy-hieu ${mauDat}">${chuDat}</span></td>
                                <td>${bm.thoi_gian}s</td>
                                <td>${(bm.token_vao || 0).toLocaleString()}</td>
                                <td>${(bm.token_ra || 0).toLocaleString()}</td>
                                <td>${(bm.token_suy_nghi || 0).toLocaleString()}</td>
                                <td><strong>${(bm.tong_token || bm.so_token || 0).toLocaleString()}</strong></td>
                                <td>$${bm.chi_phi ? bm.chi_phi.toFixed(5) : '0.00'}</td>
                                <td style="color: var(--mo); max-width: 260px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap;" title="${(bm.phan_hoi || '').replace(/"/g, '&quot;')}">${bm.phan_hoi || ''}</td>
                            </tr>
                        `;
                    }).join('');
                } else {
                    tbodyBm.innerHTML = '<tr><td colspan="9" style="text-align: center; color: var(--mo);">Chưa có dữ liệu benchmark</td></tr>';
                }

                // 5. Bang Test Suites
                const tbodyTs = document.getElementById('bang_test_suites');
                if (dl.tap_kiem_thu && dl.tap_kiem_thu.length > 0) {
                    document.getElementById('nhan_tong_test_suites').innerText = dl.tap_kiem_thu.length + ' bài';
                    tbodyTs.innerHTML = dl.tap_kiem_thu.map(tc => {
                        const mauTag = tc.loai_tap === 'Mẫu chuẩn' ? 'huy-hieu-lam' : 'huy-hieu-tim';
                        return `
                            <tr>
                                <td><span class="huy-hieu ${mauTag}">${tc.loai_tap}</span></td>
                                <td><code>${tc.id}</code></td>
                                <td style="max-width: 480px; word-break: break-word;">${tc.prompt}</td>
                                <td><span class="huy-hieu huy-hieu-xanh">${tc.expected || 'Tùy biến'}</span></td>
                            </tr>
                        `;
                    }).join('');
                }

                // 6. Bang Nhat Ky Realtime
                const tbodyNk = document.getElementById('bang_nhat_ky');
                if (dl.ds_nk && dl.ds_nk.length > 0) {
                    tbodyNk.innerHTML = dl.ds_nk.slice(0, 50).map(item => {
                        const tg = item.thoi_diem || (item.thoi_gian ? new Date(item.thoi_gian * 1000).toLocaleTimeString('vi-VN') : '--');
                        return `
                            <tr>
                                <td>${tg}</td>
                                <td><span class="huy-hieu huy-hieu-lam">Lượt #${item.so_luot !== undefined ? item.so_luot : 0}</span></td>
                                <td><span class="ma_phien">${item.ma_phien || 'N/A'}</span></td>
                                <td><span class="huy-hieu huy-hieu-tim">${item.skill_kich_hoat || 'find-skills'}</span></td>
                                <td><span class="huy-hieu huy-hieu-xanh">● ${item.trang_thai || 'DA_KICH_HOAT'}</span></td>
                            </tr>
                        `;
                    }).join('');
                }

                // 7. Bang Skills & Telemetry
                if (dl.thong_ke_skills) {
                    const tk = dl.thong_ke_skills;
                    if (document.getElementById('kn_so_active')) {
                        document.getElementById('kn_so_active').innerText = tk.so_active || 0;
                        document.getElementById('kn_so_deact').innerText = tk.so_deactivated || 0;
                        document.getElementById('kn_ti_le_dung').innerText = (tk.ti_le_su_dung || 0) + '%';
                        document.getElementById('kn_so_da_dung').innerText = `${tk.top_skills ? tk.top_skills.length : 0}/${tk.tong_skills || 0} skills đã gọi`;
                        document.getElementById('kn_so_dormant').innerText = tk.so_dormant || 0;
                    }

                    // Render Top 6 Skills Widget
                    const hopTop = document.getElementById('hop_top_skills');
                    if (hopTop && tk.top_skills && tk.top_skills.length > 0) {
                        hopTop.innerHTML = tk.top_skills.slice(0, 6).map((ts, idx) => {
                            return `
                                <div style="background: rgba(15, 23, 42, 0.8); border: 1px solid var(--vien); border-radius: 8px; padding: 6px 12px; display: flex; align-items: center; gap: 8px;">
                                    <span class="huy-hieu huy-hieu-lam" style="font-weight: 800; font-size: 11px;">#${idx + 1}</span>
                                    <span style="font-size: 12px; font-weight: 600; font-family: monospace;">${ts.ten}</span>
                                    <span class="huy-hieu huy-hieu-xanh" style="font-size: 11px;">${ts.so_lan_dung} lần</span>
                                </div>
                            `;
                        }).join('');
                    }
                }

                if (dl.ky_nang && dl.ky_nang.length > 0) {
                    tat_ca_skills_cache = dl.ky_nang;
                    const o_nhap = document.getElementById('tim_kiem_skill');
                    if (o_nhap && o_nhap.value.trim() !== '') {
                        loc_danh_sach_skills();
                    } else if (che_do_loc_trang_thai !== 'TAT_CA') {
                        loc_danh_sach_skills();
                    } else {
                        const nhanDem = document.getElementById('nhan_dem_skills');
                        if (nhanDem) nhanDem.innerText = tat_ca_skills_cache.length + ' skills';
                        hien_thi_skills(tat_ca_skills_cache);
                    }
                }

                // 8. Du Lieu Kho Brain & Tri Thuc
                if (dl.brain) {
                    if (document.getElementById('chi_so_brain')) {
                        document.getElementById('chi_so_brain').innerText = (dl.brain.tong_mb || 0) + ' MB';
                    }
                    if (document.getElementById('chi_so_phien_brain')) {
                        document.getElementById('chi_so_phien_brain').innerText = (dl.brain.so_phien || 0) + ' phiên / ' + (dl.brain.so_tep || 0) + ' tệp';
                    }
                    if (document.getElementById('brain_phien')) {
                        document.getElementById('brain_phien').innerText = dl.brain.so_phien || 0;
                    }
                    if (document.getElementById('brain_tep')) {
                        document.getElementById('brain_tep').innerText = (dl.brain.so_tep || 0).toLocaleString();
                    }
                    if (document.getElementById('brain_steps')) {
                        document.getElementById('brain_steps').innerText = (dl.brain.so_steps || 0).toLocaleString();
                    }
                    if (document.getElementById('brain_dung_luong')) {
                        document.getElementById('brain_dung_luong').innerText = (dl.brain.tong_mb || 0) + ' MB';
                    }
                }
                if (dl.bo_nho && dl.bo_nho.memory_md) {
                    const elTt = document.getElementById('khoi_tri_thuc_brain');
                    if (elTt) {
                        elTt.innerText = dl.bo_nho.memory_md;
                    }
                }

            } catch (loi) {
                console.error("Lỗi cập nhật dữ liệu:", loi);
                document.getElementById('nhan_trang_thai').innerText = "MẤT KẾT NỐI SERVER";
                document.getElementById('nhan_trang_thai').className = "huy-hieu huy-hieu-do";
            }
        }

        async function goi_tac_vu(tenTacVu, nutEl) {
            const nhanEl = document.getElementById('thong_bao_tac_vu');
            const nhanTrangThai = document.getElementById('nhan_trang_thai_tac_vu');
            const ndGoc = nutEl.innerHTML;
            nutEl.innerHTML = "⏳ Đang xử lý...";
            nutEl.disabled = true;
            nhanTrangThai.className = "huy-hieu huy-hieu-cam";
            nhanTrangThai.innerText = "ĐANG CHẠY...";

            try {
                const res = await fetch(`/api/action/${tenTacVu}`, { method: 'POST' });
                const kq = await res.json();
                nhanEl.style.display = "block";
                if (kq.thanh_cong) {
                    nhanEl.style.color = "#10b981";
                    nhanEl.innerText = "✓ " + kq.thong_bao;
                    nhanTrangThai.className = "huy-hieu huy-hieu-xanh";
                    nhanTrangThai.innerText = "HOÀN TẤT";
                } else {
                    nhanEl.style.color = "#ef4444";
                    nhanEl.innerText = "✗ " + kq.thong_bao;
                    nhanTrangThai.className = "huy-hieu huy-hieu-do";
                    nhanTrangThai.innerText = "LỖI";
                }
                await cap_nhat_du_lieu();
            } catch (err) {
                nhanEl.style.display = "block";
                nhanEl.style.color = "#ef4444";
                nhanEl.innerText = "✗ Lỗi kết nối server: " + err.message;
            } finally {
                nutEl.innerHTML = ndGoc;
                nutEl.disabled = false;
                setTimeout(() => { nhanEl.style.display = "none"; }, 5000);
            }
        }

        // Tu dong nap va lap lai chu ky 2 giay
        cap_nhat_du_lieu();
        setInterval(cap_nhat_du_lieu, 2000);
    </script>
</body>
</html>
"""


class BoXuLyYeuCau(BaseHTTPRequestHandler):
    """Xu ly yeu cau HTTP cho Dashboard."""

    def do_GET(self):
        if self.path == "/" or self.path == "/index.html":
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            self.wfile.write(TRANG_GIAO_DIEN.encode("utf-8"))
        elif self.path == "/api/du_lieu":
            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.end_headers()
            
            # Lay thong ke brain tu script api
            tk_brain = {}
            try:
                sys.path.insert(0, str(lay_thu_muc_goc() / ".agents" / "scripts"))
                from api_dashboard_brain import lay_thong_ke_brain_nhanh
                tk_brain = lay_thong_ke_brain_nhanh()
            except Exception:
                pass

            # Lay thong ke skills va telemetry
            tk_skills = doc_danh_sach_ky_nang_va_telemetry()

            du_lieu = {
                "ds_nk": doc_nhat_ky_harness(),
                "bao_cao": doc_ket_qua_danh_gia(),
                "tap_kiem_thu": doc_tap_kiem_thu(),
                "bo_nho": doc_bo_nho_context(),
                "ky_nang": tk_skills.get("danh_sach", []),
                "thong_ke_skills": tk_skills,
                "brain": tk_brain
            }
            self.wfile.write(json.dumps(du_lieu, ensure_ascii=False).encode("utf-8"))
        else:
            self.send_response(404)
            self.end_headers()

    def do_POST(self):
        sys.path.insert(0, str(lay_thu_muc_goc() / ".agents" / "scripts"))
        kq = {"thanh_cong": False, "thong_bao": "Đường dẫn không hợp lệ"}

        if self.path == "/api/action/thu_hoach":
            try:
                from api_dashboard_brain import xu_ly_thu_hoach_tri_thuc
                kq = xu_ly_thu_hoach_tri_thuc()
            except Exception as loi:
                kq = {"thanh_cong": False, "thong_bao": str(loi)}
        elif self.path == "/api/action/don_dep":
            try:
                from api_dashboard_brain import xu_ly_don_dep_steps_rac
                kq = xu_ly_don_dep_steps_rac()
            except Exception as loi:
                kq = {"thanh_cong": False, "thong_bao": str(loi)}
        elif self.path == "/api/action/dong_bo":
            try:
                from api_dashboard_brain import xu_ly_dong_bo_context_moi_nhat
                kq = xu_ly_dong_bo_context_moi_nhat()
            except Exception as loi:
                kq = {"thanh_cong": False, "thong_bao": str(loi)}
        elif self.path.startswith("/api/action/deactivate_skill"):
            try:
                from urllib.parse import urlparse, parse_qs
                parsed = urlparse(self.path)
                params = parse_qs(parsed.query)
                ten_sk = params.get("ten", [""])[0]
                from quan_ly_vong_doi_skills_telemetry import tam_ngung_skill
                thanh_cong, thong_bao = tam_ngung_skill(ten_sk)
                kq = {"thanh_cong": thanh_cong, "thong_bao": thong_bao}
            except Exception as loi:
                kq = {"thanh_cong": False, "thong_bao": str(loi)}
        elif self.path.startswith("/api/action/reactivate_skill"):
            try:
                from urllib.parse import urlparse, parse_qs
                parsed = urlparse(self.path)
                params = parse_qs(parsed.query)
                ten_sk = params.get("ten", [""])[0]
                from quan_ly_vong_doi_skills_telemetry import kich_hoat_lai_skill
                thanh_cong, thong_bao = kich_hoat_lai_skill(ten_sk)
                kq = {"thanh_cong": thanh_cong, "thong_bao": thong_bao}
            except Exception as loi:
                kq = {"thanh_cong": False, "thong_bao": str(loi)}
        elif self.path == "/api/action/deactivate_dormant_ctf":
            try:
                from quan_ly_vong_doi_skills_telemetry import tu_dong_tam_ngung_skills_dormant_ctf
                dem = tu_dong_tam_ngung_skills_dormant_ctf()
                kq = {"thanh_cong": True, "thong_bao": f"Đã tạm ngưng {dem} kỹ năng CTF Sandbox ngủ đông."}
            except Exception as loi:
                kq = {"thanh_cong": False, "thong_bao": str(loi)}

        self.send_response(200)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.end_headers()
        self.wfile.write(json.dumps(kq, ensure_ascii=False).encode("utf-8"))

    def log_message(self, format, *args):
        # Khong ghi log ranh roi de tranh lam nghen man hinh
        pass


class MayChuDaLuong(ThreadingHTTPServer):
    allow_reuse_address = True
    daemon_threads = True


def khoi_chay_gui():
    """Khoi dong may chu HTTP tren cong 7890."""
    dia_chi = ("127.0.0.1", CONG_DICH_VU)
    may_chu = MayChuDaLuong(dia_chi, BoXuLyYeuCau)
    duong_dan_web = f"http://127.0.0.1:{CONG_DICH_VU}"

    print(f"[*] DA KHOI CHAY DASHBOARD TAI: {duong_dan_web}")
    print("[*] Dashboard tich hop day du Hermes Context Engine & Harness Benchmark.")
    print("[*] Nhan Ctrl+C de dung.")

    try:
        webbrowser.open(duong_dan_web)
    except Exception:
        pass

    while True:
        try:
            may_chu.serve_forever()
        except KeyboardInterrupt:
            print("\n[*] Da dung may chu Dashboard.")
            may_chu.server_close()
            break
        except Exception:
            time.sleep(0.5)
            continue


if __name__ == "__main__":
    khoi_chay_gui()
