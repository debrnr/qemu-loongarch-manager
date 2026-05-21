# 🚀 发布指南 - 如何将 EXE 发布到 Git 平台

## 概述

本文档说明如何将打包好的 EXE 文件发布到 GitHub、Gitee 和 GitCode 平台。

**重要原则**：
- ❌ **不要**将 EXE 文件提交到 Git 仓库
- ✅ **应该**使用平台的 Releases 功能发布
- ✅ **应该**使用 Git Tags 标记版本

---

## 📋 发布流程

### 第一步：打包生成 EXE

```bash
# 运行打包脚本
python build_exe.py
```

生成的文件位于 `dist/` 目录：
- `QML_260521_A2.exe` - 带版本号的主文件
- `Deepin_VM_Manager.exe` - 无版本号文件

### 第二步：创建 Git Tag

```bash
# 根据 EXE 版本号创建 tag
git tag v260521-A2

# 推送 tag 到远程仓库
git push origin v260521-A2
git push gitee v260521-A2
git push gitcode v260521-A2
```

### 第三步：在平台上创建 Release

#### GitHub 发布步骤

1. 访问：https://github.com/你的用户名/LoongarchWorkstationManagerGui/releases
2. 点击 **"Draft a new release"**
3. 填写信息：
   - **Tag version**: `v260521-A2`（选择刚创建的 tag）
   - **Release title**: `QML_260521_A2 - 2026年05月21日更新`
   - **Description**: 添加更新说明（见下方模板）
4. 点击 **"Attach binaries"** 上传文件：
   - `QML_260521_A2.exe`
   - （可选）`Deepin_VM_Manager.exe`
5. 勾选 **"Set as the latest release"**
6. 点击 **"Publish release"**

#### Gitee 发布步骤

1. 访问：https://gitee.com/你的用户名/LoongarchWorkstationManagerGui/releases
2. 点击 **"新建发布"**
3. 填写信息：
   - **标签**: `v260521-A2`
   - **标题**: `QML_260521_A2`
   - **内容**: 更新说明
4. 上传附件：
   - `QML_260521_A2.exe`
5. 点击 **"确定"**

#### GitCode 发布步骤

1. 访问：https://gitcode.com/你的用户名/LoongarchWorkstationManagerGui/releases
2. 点击 **"新建发布"**
3. 类似 GitHub 的步骤填写信息和上传文件

---

## 📝 Release 描述模板

```markdown
## 🎉 QML_260521_A2 发布

**构建时间**: 2026-05-21 14:25  
**版本号**: QML_260521_A2

### ✨ 新功能
- 功能1描述
- 功能2描述

### 🐛 Bug 修复
- 修复问题1
- 修复问题2

### 📦 下载
- [QML_260521_A2.exe](链接) - 主程序（推荐）
- [Deepin_VM_Manager.exe](链接) - 无版本号版本

### 📋 系统要求
- Windows 操作系统
- LoongArch 架构支持
- QEMU for LoongArch

### 🔗 相关链接
- [项目主页](仓库链接)
- [完整文档](docs/INDEX.md)
- [命名规则](docs/EXE_NAMING_RULES.md)
```

---

## 🔄 自动化方案（可选）

### 使用 GitHub Actions 自动发布

创建 `.github/workflows/release.yml`：

```yaml
name: Build and Release

on:
  push:
    tags:
      - 'v*'

jobs:
  build:
    runs-on: windows-latest
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.10'
    
    - name: Install dependencies
      run: |
        pip install -r requirements.txt
        pip install pyinstaller
    
    - name: Build EXE
      run: python build_exe.py
    
    - name: Create Release
      uses: softprops/action-gh-release@v1
      with:
        files: dist/*.exe
        body: |
          自动构建版本 ${{ github.ref_name }}
          
          构建时间: ${{ github.event.head_commit.timestamp }}
      env:
        GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
```

### 使用脚本半自动发布

创建 `create_release.bat`：

```batch
@echo off
chcp 65001 >nul
echo ========================================
echo   创建 Release 辅助工具
echo ========================================
echo.

REM 获取最新 exe 文件名
for %%f in (dist\QML_*.exe) do set LATEST_EXE=%%f

if not defined LATEST_EXE (
    echo ❌ 未找到版本化的 EXE 文件
    echo 请先运行: python build_exe.py
    pause
    exit /b 1
)

echo 📦 找到最新 EXE: %LATEST_EXE%
echo.

REM 提取版本号
for %%A in ("%LATEST_EXE%") do (
    set FILENAME=%%~nA
)
set VERSION=%FILENAME:QML_=%

echo 🏷️  版本号: v%VERSION%
echo.

REM 创建 git tag
git tag v%VERSION%
echo ✅ Git tag 已创建: v%VERSION%
echo.

echo 📤 推送 tag 到远程仓库...
git push origin v%VERSION%
git push gitee v%VERSION%
git push gitcode v%VERSION%
echo.

echo ========================================
echo   ✅ 完成！
echo ========================================
echo.
echo 下一步：
echo 1. 访问各平台 Releases 页面
echo 2. 创建新 Release，选择 tag: v%VERSION%
echo 3. 上传文件: %LATEST_EXE%
echo.
pause
```

---

## 📊 版本管理策略

### Tag 命名规范

```
格式: vYYMMDD-HM
示例: v260521-A2

对应 EXE: QML_260521_A2.exe
```

### Release 分类

- **Latest Release**: 最新版本（自动标记）
- **Pre-release**: 测试版本（勾选"这是预发布版本"）
- **Stable**: 稳定版本（默认）

### 保留策略

- ✅ 保留最近 10 个 Release
- ✅ 保留所有主要版本（每月第一个）
- ❌ 删除失败的构建
- 📦 归档旧版本到网盘（可选）

---

## 🎯 最佳实践

### ✅ 推荐做法

1. **每次打包后立即创建 Release**
   ```bash
   python build_exe.py
   git tag v260521-A2
   git push --tags
   # 然后手动或通过脚本上传到 Releases
   ```

2. **编写清晰的更新日志**
   - 列出新功能
   - 说明 Bug 修复
   - 标注已知问题

3. **提供多个下载选项**
   - 带版本号的主文件（必选）
   - 无版本号文件（可选）
   - 校验文件（SHA256，高级）

4. **定期清理旧版本**
   - 保留最近 10 个版本
   - 归档更早的版本

### ❌ 避免做法

1. **不要将 dist/ 加入 Git**
   ```gitignore
   # .gitignore 中已有
   dist/
   build/
   ```

2. **不要忘记创建 Tag**
   - Tag 是版本的永久标记
   - 便于回溯和引用

3. **不要跳过更新日志**
   - 用户需要知道变化
   - 便于问题追踪

---

## 📈 统计数据

### 查看下载统计

**GitHub**:
- 访问 Release 页面
- 查看每个文件的下载次数

**Gitee**:
- 类似 GitHub
- 在 Release 详情页查看

**GitCode**:
- 同样提供下载统计

### 分析数据

- 📊 哪个版本最受欢迎
- 🌍 用户分布情况
- 📅 下载趋势分析

---

## 🔗 相关资源

- [GitHub Releases 文档](https://docs.github.com/en/repositories/releasing-projects-on-github/about-releases)
- [Gitee 发布说明](https://gitee.com/help/articles/4227)
- [GitCode 发布指南](https://gitcode.com/help)
- [EXE 命名规则](EXE_NAMING_RULES.md)
- [Git 推送指南](GIT_PUSH_GUIDE.md)

---

## 💡 常见问题

### Q: 可以同时发布到三个平台吗？
A: 是的，建议同时发布，确保用户有多个下载源。

### Q: Release 和 Tag 有什么区别？
A: 
- **Tag**: Git 的标记，指向某个 commit
- **Release**: 平台的发布页面，包含 Tag + 文件 + 说明

### Q: 可以修改已发布的 Release 吗？
A: 可以编辑 Release 的描述和附件，但不建议修改 Tag。

### Q: 如何处理紧急 Bug 修复？
A: 
1. 修复 Bug
2. 重新打包（生成新版本号）
3. 创建新 Release
4. 标记为 Latest
5. 在旧 Release 中添加注释

---

**最后更新**: 2026-05-21  
**维护者**: LoongarchWorkstationManagerGui Team
