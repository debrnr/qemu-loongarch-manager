@echo off
chcp 65001 >nul
echo ========================================
echo   Deepin VM Manager - 推送到所有平台
echo ========================================
echo.

REM 检查是否有未提交的更改
git status --porcelain | findstr . >nul
if %errorlevel% equ 0 (
    echo ⚠️  检测到未提交的更改！
    echo.
    choice /C YN /M "是否先提交这些更改"
    if errorlevel 2 goto :skip_commit
    if errorlevel 1 (
        echo.
        git add .
        set /p commit_msg="请输入提交说明: "
        git commit -m "%commit_msg%"
        echo.
    )
)

:skip_commit
echo 📤 开始推送到远程仓库...
echo.

REM 推送到 GitHub
echo [1/3] 推送到 GitHub...
git push origin master
if %errorlevel% neq 0 (
    echo ❌ GitHub 推送失败！
    pause
    exit /b 1
)
echo ✅ GitHub 推送成功
echo.

REM 推送到 Gitee
echo [2/3] 推送到 Gitee...
git push gitee master
if %errorlevel% neq 0 (
    echo ⚠️  Gitee 推送失败（可能未配置）
) else (
    echo ✅ Gitee 推送成功
)
echo.

REM 推送到 GitCode
echo [3/3] 推送到 GitCode...
git push gitcode master
if %errorlevel% neq 0 (
    echo ⚠️  GitCode 推送失败（可能未配置）
) else (
    echo ✅ GitCode 推送成功
)
echo.

echo ========================================
echo   🎉 推送完成！
echo ========================================
pause
