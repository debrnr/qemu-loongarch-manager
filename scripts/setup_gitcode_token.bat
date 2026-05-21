@echo off
chcp 65001 >nul
echo ========================================
echo   GitCode Token 配置助手
echo ========================================
echo.
echo 请按照以下步骤配置 GitCode Personal Access Token:
echo.
echo 1. 访问 https://gitcode.com 并登录
echo 2. 点击右上角头像 ^> 设置 ^> 个人访问令牌
echo 3. 创建新令牌，勾选 read_repository, write_repository, api
echo 4. 复制生成的 Token
echo.
echo ========================================
set /p TOKEN="请输入你的 GitCode Personal Access Token: "
echo.

if "%TOKEN%"=="" (
    echo ❌ Token 不能为空
    pause
    exit /b 1
)

echo  正在配置 GitCode 远程仓库...
git remote set-url gitcode https://%TOKEN%@gitcode.com/debrnr/qemu-loongarch-manager.git

if %errorlevel% neq 0 (
    echo ❌ 配置失败
    pause
    exit /b 1
)

echo ✅ GitCode URL 已更新
echo.

echo 📤 正在推送代码到 GitCode...
git push gitcode master

if %errorlevel% equ 0 (
    echo ✅ 代码推送成功
) else (
    echo ❌ 代码推送失败
    pause
    exit /b 1
)

echo.
echo 📤 正在推送 Tag 到 GitCode...
git push gitcode v260521-A4

if %errorlevel% equ 0 (
    echo ✅ Tag 推送成功
) else (
    echo ❌ Tag 推送失败
    pause
    exit /b 1
)

echo.
echo ========================================
echo   ✅ GitCode 配置完成！
echo ========================================
echo.
echo 下一步：
echo 1. 访问 https://gitcode.com/debrnr/qemu-loongarch-manager/releases/new
echo 2. 选择 Tag: v260521-A4
echo 3. 上传文件: dist\QML_260521_A4.exe
echo 4. 点击发布
echo.

pause
