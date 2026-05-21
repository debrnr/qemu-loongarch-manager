@echo off
chcp 65001 >nul
echo ========================================
echo   Deepin VM Manager - 发布助手
echo ========================================
echo.

REM 检查 dist 目录是否存在
if not exist "dist" (
    echo ❌ dist 目录不存在
    echo 💡 请先运行: python build_exe.py
    pause
    exit /b 1
)

REM 查找最新的 QML_*.exe 文件
set LATEST_EXE=
for %%f in (dist\QML_*.exe) do (
    set LATEST_EXE=%%f
    goto :found
)

:found
if "%LATEST_EXE%"=="" (
    echo ❌ 未找到版本化的 EXE 文件
    echo 💡 请先运行: python build_exe.py
    pause
    exit /b 1
)

echo 📦 找到最新 EXE: %LATEST_EXE%
echo.

REM 提取版本号
for %%A in ("%LATEST_EXE%") do set FILENAME=%%~nA
set VERSION=%FILENAME:QML_=%
set VERSION=v%VERSION:_=-%

echo 🏷️  版本号: %VERSION%
echo.

REM 检查 Git 状态
git status --porcelain | findstr . >nul
if %errorlevel% equ 0 (
    echo ⚠️  检测到未提交的更改
    choice /C YN /M "是否继续"
    if errorlevel 2 exit /b 1
)

echo.
echo 📤 创建并推送 Git Tag...
git tag -a %VERSION% -m "Release %VERSION%"
if %errorlevel% neq 0 (
    echo ❌ 创建 Tag 失败
    pause
    exit /b 1
)

echo ✅ Tag 创建成功
echo.

echo 📤 推送 Tag 到远程仓库...
git push origin %VERSION% 2>nul
if %errorlevel% equ 0 echo ✅ GitHub 推送成功

git push gitee %VERSION% 2>nul
if %errorlevel% equ 0 echo ✅ Gitee 推送成功

git push gitcode %VERSION% 2>nul
if %errorlevel% equ 0 echo ✅ GitCode 推送成功

echo.
echo ========================================
echo   ✅ Git Tag 推送完成！
echo ========================================
echo.

REM 生成 Release 说明文件
set RELEASE_NOTES=RELEASE_NOTES_%VERSION%.md
echo ## 🎉 %VERSION:v=QML_% 发布 > %RELEASE_NOTES%
echo. >> %RELEASE_NOTES%
echo **构建时间**: %date% %time% >> %RELEASE_NOTES%
echo **版本号**: %VERSION:v=% >> %RELEASE_NOTES%
echo. >> %RELEASE_NOTES%
echo ### ✨ 更新内容 >> %RELEASE_NOTES%
echo - （请在此处添加新功能说明） >> %RELEASE_NOTES%
echo. >> %RELEASE_NOTES%
echo ### 🐛 Bug 修复 >> %RELEASE_NOTES%
echo - （请在此处添加修复的问题） >> %RELEASE_NOTES%
echo. >> %RELEASE_NOTES%
echo ### 📦 下载 >> %RELEASE_NOTES%
echo - [%LATEST_EXE:dist\=%](附件) - 主程序（推荐） >> %RELEASE_NOTES%
echo. >> %RELEASE_NOTES%
echo ### 📋 系统要求 >> %RELEASE_NOTES%
echo - Windows 操作系统 >> %RELEASE_NOTES%
echo - LoongArch 架构支持 >> %RELEASE_NOTES%
echo - QEMU for LoongArch >> %RELEASE_NOTES%
echo. >> %RELEASE_NOTES%
echo ### 🔗 相关链接 >> %RELEASE_NOTES%
echo - [项目主页](仓库URL) >> %RELEASE_NOTES%
echo - [完整文档](docs/INDEX.md) >> %RELEASE_NOTES%
echo - [命名规则](docs/EXE_NAMING_RULES.md) >> %RELEASE_NOTES%
echo - [发布指南](docs/RELEASE_GUIDE.md) >> %RELEASE_NOTES%

echo 💾 Release 说明已保存到: %RELEASE_NOTES%
echo.

echo ========================================
echo   📋 下一步操作
echo ========================================
echo.
echo 1. 访问各平台 Releases 页面
echo    - GitHub: https://github.com/你的用户名/LoongarchWorkstationManagerGui/releases/new
echo    - Gitee: https://gitee.com/你的用户名/LoongarchWorkstationManagerGui/releases/new
echo    - GitCode: https://gitcode.com/你的用户名/LoongarchWorkstationManagerGui/releases/new
echo.
echo 2. 选择 Tag: %VERSION%
echo.
echo 3. 复制以下内容作为 Release 说明：
type %RELEASE_NOTES%
echo.
echo 4. 上传文件: %LATEST_EXE%
echo.
echo 5. 点击发布
echo.

pause
