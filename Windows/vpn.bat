@echo off
setlocal EnableDelayedExpansion

:: ============================================================
:: vpn.bat  Windows 系统代理开关
:: ------------------------------------------------------------
::   vpn                    切换代理开关
::   vpn on                 开启代理
::   vpn off                关闭代理
::   vpn zt                 查看当前状态
::   vpn ip:端口            只改服务器，开关状态不变
::   vpn on ip:端口         改服务器并开启
::   vpn off ip:端口        改服务器并关闭
::   vpn y                  执行完不等待 2 秒（也可写 -y）
:: ============================================================

set "REGKEY=HKCU\Software\Microsoft\Windows\CurrentVersion\Internet Settings"
set "ACTION="
set "NEWSERVER="
set "NODELAY=0"

:: ---------------- 参数解析 ----------------
:parse
if "%~1"=="" goto dispatch
set "ARG=%~1"
shift

if /i "!ARG!"=="y" (
    set "NODELAY=1"
    goto parse
)
if /i "!ARG!"=="-y" (
    set "NODELAY=1"
    goto parse
)
if /i "!ARG!"=="on" (
    set "ACTION=on"
    goto parse
)
if /i "!ARG!"=="off" (
    set "ACTION=off"
    goto parse
)
if /i "!ARG!"=="zt" (
    set "ACTION=zt"
    goto parse
)

:: 先去 http:// https:// 前缀，再判断是否 ip:端口
set "SRV=!ARG!"
if /i "!SRV:~0,7!"=="http://" set "SRV=!SRV:~7!"
if /i "!SRV:~0,8!"=="https://" set "SRV=!SRV:~8!"

if not "!SRV::=!"=="!SRV!" (
    set "NEWSERVER=!SRV!"
    goto parse
)

if "!ARG:~0,1!"=="-" (
    echo [错误] 参数不用带短横线，直接写：!ARG:~1!
    goto usage
)

echo [错误] 无法识别的参数：!ARG!

:usage
echo.
echo 用法：
echo   vpn                    切换代理开关
echo   vpn on                 开启代理
echo   vpn off                关闭代理
echo   vpn zt                 查看当前状态
echo   vpn ip:端口            只改服务器，开关状态不变
echo   vpn on ip:端口         改服务器并开启，例如 vpn on 127.0.0.1:7890
echo   vpn off ip:端口        改服务器并关闭
echo   vpn y                  执行完不等待 2 秒（也可写 -y）
goto fail

:: ---------------- 分发 ----------------
:dispatch
if "!ACTION!"=="" (
    if "!NEWSERVER!"=="" (
        call :get_state
        if "!PE!"=="0x1" (
            set "ACTION=off"
        ) else (
            set "ACTION=on"
        )
    ) else (
        set "ACTION=keep"
    )
)

if /i "!ACTION!"=="zt" goto do_status
if /i "!ACTION!"=="on" goto do_on
if /i "!ACTION!"=="off" goto do_off
if /i "!ACTION!"=="keep" goto do_keep
goto fail

:: ---------------- 开启 ----------------
:do_on
call :get_state
call :set_server
if "!PS!"=="" (
    echo [错误] 还没设置过服务器，请指定：vpn on ip:端口
    goto fail
)
reg add "%REGKEY%" /v ProxyEnable /t REG_DWORD /d 1 /f >nul
call :refresh
call :show
goto done

:: ---------------- 关闭 ----------------
:do_off
call :set_server
reg add "%REGKEY%" /v ProxyEnable /t REG_DWORD /d 0 /f >nul
call :refresh
call :show
goto done

:: ---------------- 只改服务器，状态不变 ----------------
:do_keep
call :set_server
call :refresh
call :show
goto done

:: ---------------- 状态 ----------------
:do_status
if not "!NEWSERVER!"=="" (
    echo [错误] zt 只查状态，不能同时指定服务器
    goto usage
)
call :show
goto done

:: ---------------- 子过程 ----------------
:get_state
set "PE="
set "PS="
for /f "tokens=1,2,*" %%a in ('reg query "%REGKEY%" 2^>nul') do (
    if /i "%%a"=="ProxyEnable" set "PE=%%c"
    if /i "%%a"=="ProxyServer" set "PS=%%c"
)
exit /b 0

:set_server
if "!NEWSERVER!"=="" exit /b 0
reg add "%REGKEY%" /v ProxyServer /t REG_SZ /d "!NEWSERVER!" /f >nul
exit /b 0

:show
call :get_state
if "!PE!"=="0x1" (
    echo 代理已【开启】
) else (
    echo 代理已【关闭】
)
if "!PS!"=="" (
    echo 服务器：（未设置）
) else (
    echo 服务器：!PS!
)
exit /b 0

:refresh
rundll32.exe wininet.dll,InternetSetOption 0 39
rundll32.exe wininet.dll,InternetSetOption 0 37
exit /b 0

:done
if "!NODELAY!"=="0" timeout /t 2 /nobreak >nul 2>&1
endlocal
exit /b 0

:fail
if "!NODELAY!"=="0" timeout /t 2 /nobreak >nul 2>&1
endlocal
exit /b 1
