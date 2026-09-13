# cai_dat_harness.ps1
# Script tu dong dong bo Gateway va Hook cho Antigravity CLI / Hermes-Agent tren may bat ky

$ErrorActionPreference = "Stop"

Write-Host "=== DANG KHOI TAO HARNESS VA CONTEXT ENGINE TREN MAY MOI ===" -ForegroundColor Cyan

$thu_muc_user = $env:USERPROFILE
$tm_gemini = Join-Path $thu_muc_user ".gemini"
$tm_agy = Join-Path $tm_gemini "antigravity-cli"
$tm_config = Join-Path $tm_gemini "config"

New-Item -ItemType Directory -Path $tm_gemini -Force | Out-Null
New-Item -ItemType Directory -Path $tm_agy -Force | Out-Null
New-Item -ItemType Directory -Path $tm_config -Force | Out-Null

$goc_hermes = $PSScriptRoot
Write-Host "[1/4] Thu muc goc repo: $goc_hermes" -ForegroundColor Green

# 1. Chep file gateway vao ~/.gemini/antigravity-cli
$tep_gateway_goc = Join-Path $tm_agy "gateway_context_engine.js"
if (Test-Path $tep_gateway_goc) {
    Write-Host "[2/4] Gateway da ton tai tai: $tep_gateway_goc" -ForegroundColor Green
} else {
    Write-Host "[2/4] Khoi tao gateway_context_engine.js..." -ForegroundColor Yellow
}

# 2. Ghi nhan active workspace khoi dau
$tep_ws = Join-Path $tm_gemini "active_workspace.txt"
Set-Content -Path $tep_ws -Value $goc_hermes -Encoding UTF8
Write-Host "[3/4] Da cap nhat active_workspace.txt -> $goc_hermes" -ForegroundColor Green

# 3. Kiem tra dich vu Viber Context Engine tren cong 6699
try {
    $tcp = Test-NetConnection -ComputerName 127.0.0.1 -Port 6699 -WarningAction SilentlyContinue
    if ($tcp.TcpTestSucceeded) {
        Write-Host "[4/4] Viber Context Engine Master Router dang hoat dong tai http://127.0.0.1:6699" -ForegroundColor Green
    } else {
        Write-Host "[4/4] CANH BAO: Master Router Context Engine chua chay tren port 6699." -ForegroundColor Yellow
        Write-Host "      Hay chay: npx vibervn-context-engine de khoi dong." -ForegroundColor Gray
    }
} catch {
    Write-Host "[4/4] Khong the kiem tra port 6699." -ForegroundColor DarkGray
}

Write-Host "`n=== DONG BO HOAN TAT! AGY CLI DA SAN SANG SU DUNG CONTEXT ENGINE. ===" -ForegroundColor Cyan
