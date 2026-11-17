@echo off
setlocal EnableDelayedExpansion

:: ============================================================
:: vpn.bat  Windows 系统代理开关
:: ------------------------------------------------------------
::   vpn                    切换代理开关
::   vpn on                 开启代理（并同步排除规则）
::   vpn off                关闭代理
::   vpn zt                 查看当前状态
::   vpn ip:端口            只改服务器，开关状态不变
::   vpn on ip:端口         改服务器并开启
::   vpn off ip:端口        改服务器并关闭
::   vpn r                  把规则文件写进系统排除规则
::   vpn rl                 列出当前的排除规则
::   vpn rs                 把当前排除规则反存回规则文件
::   vpn re                 记事本编辑规则文件，关掉后自动套用
::   vpn k                  本次不同步排除规则（可和其它参数同用）
::   vpn y                  执行完不等待 2 秒（也可写 -y）
:: ------------------------------------------------------------
:: 规则文件：Q:\排除规则.txt
::   一行一条，也支持分号分隔；# 开头的行当注释跳过
::   <local> 不用手写，脚本会自动补上（= 勿将代理用于本地地址）
:: ============================================================

set "REGKEY=HKCU\Software\Microsoft\Windows\CurrentVersion\Internet Settings"
set "RULESFILE=Q:\排除规则.txt"
set "ACTION="
set "NEWSERVER="
set "NODELAY=0"
set "NOBYPASS=0"

:: <local> 令牌：尖括号要拆开构造，否则会被当成重定向
set BYP1=^<
set BYP2=^>
set "LOCALTOK=!BYP1!local!BYP2!"

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
if /i "!ARG!"=="k" (
    set "NOBYPASS=1"
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
if /i "!ARG!"=="r" (
    set "ACTION=rules"
    goto parse
)
if /i "!ARG!"=="rl" (
    set "ACTION=rulelist"
    goto parse
)
if /i "!ARG!"=="rs" (
    set "ACTION=rulesave"
    goto parse
)
if /i "!ARG!"=="re" (
    set "ACTION=ruleedit"
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
echo   vpn on                 开启代理（并同步排除规则）
echo   vpn off                关闭代理
echo   vpn zt                 查看当前状态
echo   vpn ip:端口            只改服务器，开关状态不变
echo   vpn on ip:端口         改服务器并开启，例如 vpn on 127.0.0.1:7890
echo   vpn off ip:端口        改服务器并关闭
echo   vpn r                  把 !RULESFILE! 写进系统排除规则
echo   vpn rl                 列出当前的排除规则
echo   vpn rs                 把当前排除规则反存回 !RULESFILE!
echo   vpn re                 记事本编辑规则文件，关掉后自动套用
echo   vpn k                  本次不同步排除规则
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
if /i "!ACTION!"=="rules" goto do_rules
if /i "!ACTION!"=="rulelist" goto do_rulelist
if /i "!ACTION!"=="rulesave" goto do_rulesave
if /i "!ACTION!"=="ruleedit" goto do_ruleedit
goto fail

:: ---------------- 开启 ----------------
:do_on
call :get_state
call :set_server
call :get_state
if "!PS!"=="" (
    echo [错误] 还没设置过服务器，请指定：vpn on ip:端口
    goto fail
)
reg add "%REGKEY%" /v ProxyEnable /t REG_DWORD /d 1 /f >nul
call :apply_rules
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
call :apply_rules
call :refresh
call :show
goto done

:: ---------------- 只同步排除规则 ----------------
:do_rules
call :get_state
call :apply_rules
call :refresh
call :show
goto done

:: ---------------- 列出排除规则 ----------------
:do_rulelist
call :get_state
if "!PO!"=="" (
    echo 排除规则：（未设置）
    goto done
)
echo 当前排除规则：
set "R=!PO!"
:rulelist_loop
if not defined R goto done
for /f "tokens=1* delims=;" %%a in ("!R!") do (
    set "ONE=%%a"
    set "R=%%b"
)
if defined ONE echo   !ONE!
goto rulelist_loop

:: ---------------- 注册表里的规则反存回文件 ----------------
:do_rulesave
call :get_state
if "!PO!"=="" (
    echo [提示] 系统里还没有排除规则，未生成文件
    goto done
)
if exist "!RULESFILE!" copy /y "!RULESFILE!" "!RULESFILE!.bak" >nul
del /f /q "!RULESFILE!" >nul 2>&1
set "R=!PO!"
:rulesave_loop
if not defined R goto rulesave_end
for /f "tokens=1* delims=;" %%a in ("!R!") do (
    set "ONE=%%a"
    set "R=%%b"
)
if defined ONE if not "!ONE!"=="!LOCALTOK!" >>"!RULESFILE!" echo !ONE!
goto rulesave_loop
:rulesave_end
echo 已保存到：!RULESFILE!
if exist "!RULESFILE!.bak" echo 原文件备份：!RULESFILE!.bak
goto done

:: ---------------- 编辑规则文件并套用 ----------------
:do_ruleedit
if not exist "!RULESFILE!" (
    >"!RULESFILE!" echo # 一行一条，也支持分号分隔；# 开头的行是注释
    >>"!RULESFILE!" echo localhost
    >>"!RULESFILE!" echo 127.*
    >>"!RULESFILE!" echo 192.168.*
    >>"!RULESFILE!" echo 10.*
)
start /wait "" notepad "!RULESFILE!"
call :get_state
call :apply_rules
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

:: ---------------- 子过程：读取注册表 ----------------
:get_state
set "PE="
set "PS="
set "PO="
for /f "tokens=1,2,*" %%a in ('reg query "%REGKEY%" 2^>nul') do (
    if /i "%%a"=="ProxyEnable" set "PE=%%c"
    if /i "%%a"=="ProxyServer" set "PS=%%c"
    if /i "%%a"=="ProxyOverride" set "PO=%%c"
)
exit /b 0

:set_server
if "!NEWSERVER!"=="" exit /b 0
reg add "%REGKEY%" /v ProxyServer /t REG_SZ /d "!NEWSERVER!" /f >nul
exit /b 0

:: ---------------- 子过程：把规则文件写进注册表 ----------------
:apply_rules
if "!NOBYPASS!"=="1" exit /b 0
if not exist "!RULESFILE!" (
    echo [提示] 规则文件不存在，跳过同步：!RULESFILE!
    exit /b 0
)
set "RULES="
for /f "usebackq eol=# delims=" %%a in ("!RULESFILE!") do (
    set "L=%%a"
    call :add_rule_line
)
if not defined RULES (
    echo [提示] 规则文件里没有有效条目，跳过同步
    exit /b 0
)
set "RULES=!RULES:~1!"
call :tidy_rules
call set "CHK=%%RULES:!LOCALTOK!=%%"
if "!CHK!"=="!RULES!" set "RULES=!RULES!;!LOCALTOK!"
call :tidy_rules
:: 和系统里现有的规则一致就不动，也不吭声
call :get_state
if /i "!RULES!"=="!PO!" exit /b 0
reg add "%REGKEY%" /v ProxyOverride /t REG_SZ /d "!RULES!" /f >nul
if errorlevel 1 (
    echo [错误] 写入排除规则失败
    exit /b 0
)
echo [规则] 检测到变化，排除规则已更新（含本地直连）
exit /b 0

:add_rule_line
if not defined L exit /b 0
set "C=!L:~0,1!"
if "!C!"==" " ( set "L=!L:~1!" & goto add_rule_line )
if "!C!"=="	" ( set "L=!L:~1!" & goto add_rule_line )
if "!C!"==";" ( set "L=!L:~1!" & goto add_rule_line )
set "C=!L:~-1!"
if "!C!"==" " ( set "L=!L:~0,-1!" & goto add_rule_line )
if "!C!"=="	" ( set "L=!L:~0,-1!" & goto add_rule_line )
if "!C!"==";" ( set "L=!L:~0,-1!" & goto add_rule_line )
if not defined L exit /b 0
set "RULES=!RULES!;!L!"
exit /b 0

:tidy_rules
if not defined RULES exit /b 0
set "R2=!RULES:;;=;!"
if not "!R2!"=="!RULES!" (
    set "RULES=!R2!"
    goto tidy_rules
)
if "!RULES:~0,1!"==";" set "RULES=!RULES:~1!"
if not defined RULES exit /b 0
if "!RULES:~-1!"==";" set "RULES=!RULES:~0,-1!"
exit /b 0

:: ---------------- 子过程：显示 ----------------
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
if exist "!RULESFILE!" (
    echo 规则文件：!RULESFILE!
) else (
    echo 规则文件：!RULESFILE!（未找到）
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
