# Git 推送指南

本文档说明如何将代码推送到 GitHub、Gitee 和 GitCode 三个平台。

## 📋 前置准备

### 1. 创建远程仓库

在以下三个平台分别创建新的空仓库（不要初始化 README、.gitignore 等）：

- **GitHub**: https://github.com/new
- **Gitee**: https://gitee.com/projects/new
- **GitCode**: https://gitcode.com/projects/new

建议仓库名称：`LoongarchWorkstationManagerGui` 或 `deepin-vm-manager`

### 2. 获取仓库地址

创建完成后，复制每个平台的 HTTPS 或 SSH 地址，例如：
- GitHub: `https://github.com/你的用户名/LoongarchWorkstationManagerGui.git`
- Gitee: `https://gitee.com/你的用户名/LoongarchWorkstationManagerGui.git`
- GitCode: `https://gitcode.com/你的用户名/LoongarchWorkstationManagerGui.git`

## 🚀 推送步骤

### 方法一：推送到单个主仓库 + 同步到其他平台（推荐）

#### 1. 添加 GitHub 为主远程仓库

```bash
# 添加 GitHub 远程仓库（替换为你的实际地址）
git remote add origin https://github.com/你的用户名/LoongarchWorkstationManagerGui.git

# 推送到 GitHub
git push -u origin master
```

#### 2. 添加其他平台为额外的远程仓库

```bash
# 添加 Gitee
git remote add gitee https://gitee.com/你的用户名/LoongarchWorkstationManagerGui.git

# 添加 GitCode
git remote add gitcode https://gitcode.com/你的用户名/LoongarchWorkstationManagerGui.git
```

#### 3. 推送到所有平台

```bash
# 推送到 Gitee
git push gitee master

# 推送到 GitCode
git push gitcode master
```

#### 4. 后续同步

每次提交后，推送到所有平台：

```bash
git push origin master
git push gitee master
git push gitcode master
```

或者使用一条命令推送所有：

```bash
git push --all
```

### 方法二：分别为每个平台设置独立的远程仓库

如果你希望在不同平台使用不同的分支或配置，可以分别管理。

## 🔐 认证方式

### HTTPS 方式
- 每次推送需要输入用户名和密码
- GitHub 需要使用 Personal Access Token 代替密码
- Gitee/GitCode 可以使用账户密码

### SSH 方式（推荐）

#### 1. 生成 SSH 密钥（如果还没有）

```bash
ssh-keygen -t ed25519 -C "your_email@example.com"
```

#### 2. 添加公钥到各平台

- **GitHub**: Settings → SSH and GPG keys → New SSH key
- **Gitee**: 设置 → SSH 公钥 → 添加公钥
- **GitCode**: 设置 → SSH Keys → 添加密钥

公钥文件位置：`C:\Users\你的用户名\.ssh\id_ed25519.pub`

#### 3. 使用 SSH 地址

```bash
# 移除旧的 HTTPS 远程仓库
git remote remove origin
git remote remove gitee
git remote remove gitcode

# 添加 SSH 地址的远程仓库
git remote add origin git@github.com:你的用户名/LoongarchWorkstationManagerGui.git
git remote add gitee git@gitee.com:你的用户名/LoongarchWorkstationManagerGui.git
git remote add gitcode git@gitcode.com:你的用户名/LoongarchWorkstationManagerGui.git
```

## 📝 常用 Git 命令

```bash
# 查看远程仓库
git remote -v

# 查看状态
git status

# 添加文件
git add .

# 提交更改
git commit -m "提交说明"

# 推送到所有远程仓库
git push --all

# 拉取最新代码
git pull origin master

# 查看提交历史
git log --oneline
```

## ⚠️ 注意事项

1. **首次推送前**确保在各平台创建的空仓库没有初始化文件
2. **敏感信息**：检查 `.gitignore` 已排除 `vm_config.json` 等配置文件
3. **大文件**：如果有大文件（ISO、磁盘镜像），考虑使用 Git LFS
4. **分支管理**：建议在开发时使用 `dev` 分支，稳定版本合并到 `master`
5. **定期备份**：建议定期推送到多个平台以防数据丢失

## 🔗 快速推送脚本

创建 `push_all.bat`（Windows）：

```batch
@echo off
echo 推送到所有远程仓库...
git push origin master
git push gitee master
git push gitcode master
echo 推送完成！
pause
```

或者创建 `push_all.sh`（Linux/Mac）：

```bash
#!/bin/bash
echo "推送到所有远程仓库..."
git push origin master
git push gitee master
git push gitcode master
echo "推送完成！"
```

## 📊 验证推送

推送完成后，访问各平台仓库页面确认文件已上传：
- ✅ 查看所有源文件
- ✅ 检查 README.md 是否正确显示
- ✅ 确认 .gitignore 生效
- ✅ 验证提交历史记录

---

**提示**：如果遇到推送失败，请检查：
1. 网络连接
2. 认证信息（用户名/密码/Token/SSH密钥）
3. 仓库权限设置
4. 是否有冲突需要先拉取
