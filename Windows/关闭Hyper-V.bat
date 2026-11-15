@echo off
:: 检查管理员权限
net session >nul 2>&1
if %errorLevel% neq 0 (
    echo 请右键以管理员身份运行此脚本
    pause
    exit /b
)

:: 检测Hyper-V功能状态
set "hyperv_state=Disabled"
for /f "tokens=3" %%i in ('DISM /Online /Get-FeatureInfo:Microsoft-Hyper-V-All /English 2^>nul ^| findstr /i "State"') do (
    set "hyperv_state=%%i"
)

:: 检测虚拟化固件支持
set "vtx_enabled=未检测到"
for /f "skip=1 tokens=2 delims==" %%i in ('wmic cpu get VirtualizationFirmwareEnabled /value 2^>nul') do (
    if "%%i"=="TRUE" (set "vtx_enabled=已启用") else (set "vtx_enabled=未启用")
)

:: 显示信息
cls
echo [Hyper-V状态检测]
echo.
echo Hyper-V功能状态：%hyperv_state%
echo BIOS虚拟化支持：%vtx_enabled%
echo.
echo 注意：
echo 1. BIOS设置需要手动进入BIOS界面修改
echo 2. 关闭Hyper-V需要重启计算机
echo.

:: 关闭功能选项
:choice
set /p choice=是否要关闭Hyper-V功能？(Y/N):
if /i "%choice%"=="Y" goto disable_hyperv
if /i "%choice%"=="N" goto exit
echo 无效的选择，请输入 Y 或 N。
goto choice

:disable_hyperv
echo 正在关闭Hyper-V...
DISM /Online /Disable-Feature:Microsoft-Hyper-V-All /NoRestart >nul
if %errorLevel% equ 0 (
    echo Hyper-V 功能已成功禁用。
) else (
    echo 无法禁用 Hyper-V 功能，请检查系统状态。
    pause
    exit /b
)

DISM /Online /Disable-Feature:VirtualMachinePlatform /NoRestart >nul
if %errorLevel% equ 0 (
    echo 虚拟机平台已成功禁用。
) else (
    echo 无法禁用虚拟机平台，请检查系统状态。
    pause
    exit /b
)

bcdedit /set hypervisorlaunchtype off >nul
if %errorLevel% equ 0 (
    echo Hypervisor 启动类型已成功设置为 off。
) else (
    echo 无法设置 Hypervisor 启动类型，请检查系统状态。
    pause
    exit /b
)

echo.
echo 操作成功！需要重启使更改生效。

:restart_choice
set /p restart=是否立即重启？(Y/N):
if /i "%restart%"=="Y" goto restart
if /i "%restart%"=="N" goto exit
echo 无效的选择，请输入 Y 或 N。
goto restart_choice

:restart
shutdown /r /t 0
goto exit

:exit
exit