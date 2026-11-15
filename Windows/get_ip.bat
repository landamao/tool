@echo off
echo 正在获取本机IP地址...
echo.
echo === IPv4 地址 ===
for /f "tokens=1,* delims=:" %%a in ('ipconfig ^| findstr /c:"IPv4"') do (
    echo%%b
)
echo.
echo === IPv6 地址 ===
for /f "tokens=1,* delims=:" %%a in ('ipconfig ^| findstr /c:"IPv6"') do (
    echo%%b
)
echo.
if "%~1"=="" pause