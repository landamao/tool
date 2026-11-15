@echo off
chcp 65001 >nul
echo 正在请求管理员权限...

:: 检查是否以管理员权限运行
net session >nul 2>&1
if %errorLevel% neq 0 (
    echo 请以管理员身份运行此脚本。
    pause
    exit /b
)

echo ========================================
echo 开始执行系统网络组件重置...
echo ========================================

:: 1. 重置 Winsock 目录
echo [1/3] 正在重置 Winsock 目录...
netsh winsock reset
if %errorLevel% equ 0 (echo Winsock 重置成功。) else (echo Winsock 重置失败，请检查错误。)

:: 2. 重置 TCP/IP 堆栈
echo.
echo [2/3] 正在重置 TCP/IP 堆栈...
netsh int ip reset
echo TCP/IP 重置完成。可能需要重启后生效。

:: 3. 清除 DNS 解析缓存
echo.
echo [3/3] 正在清除 DNS 缓存...
ipconfig /flushdns
echo DNS 缓存已清除。


echo.
echo 所有命令执行完毕！
echo 正在重启
shutdown /r /t 0