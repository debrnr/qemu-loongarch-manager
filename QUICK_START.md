# 🚀 快速开始 - 推送到 Git 平台

## ✅ 已完成的工作

1. ✅ 初始化 Git 仓库
2. ✅ 创建 `.gitignore` 文件（排除不必要的文件）
3. ✅ 创建详细的 `README.md` 文档
4. ✅ 创建 `GIT_PUSH_GUIDE.md` 推送指南
5. ✅ 创建一键推送脚本（`push_all.bat` 和 `push_all.sh`）
6. ✅ 完成两次 Git 提交

## 📋 接下来的步骤

### 第一步：在三个平台创建仓库

访问以下链接创建新的空仓库（**不要勾选**"添加 README"、"添加 .gitignore"等选项）：

1. **GitHub**: https://github.com/new
   - 仓库名: `LoongarchWorkstationManagerGui`
   - 可见性: Public（公开）或 Private（私有）

2. **Gitee**: https://gitee.com/projects/new
   - 项目名称: `LoongarchWorkstationManagerGui`
   - 是否开源: 是/否

3. **GitCode**: https://gitcode.com/projects/new
   - 项目名: `LoongarchWorkstationManagerGui`
   - 可见性: 公开/私有

### 第二步：获取仓库地址

创建完成后，复制每个平台的 HTTPS 地址，格式如下：
- GitHub: `https://github.com/你的用户名/LoongarchWorkstationManagerGui.git`
- Gitee: `https://gitee.com/你的用户名/LoongarchWorkstationManagerGui.git`
- GitCode: `https://gitcode.com/你的用户名/LoongarchWorkstationManagerGui.git`

### 第三步：添加远程仓库并推送

#### 方法 A：使用命令行（推荐首次设置）

```bash
# 1. 添加 GitHub 为主仓库
git remote add origin https://github.com/你的用户名/LoongarchWorkstationManagerGui.git

# 2. 添加 Gitee
git remote add gitee https://gitee.com/你的用户名/LoongarchWorkstationManagerGui.git

# 3. 添加 GitCode
git remote add gitcode https://gitcode.com/你的用户名/LoongarchWorkstationManagerGui.git

# 4. 推送到所有平台
git push -u origin master
git push gitee master
git push gitcode master
```

#### 方法 B：使用一键推送脚本

先手动添加远程仓库（只需做一次）：

```bash
git remote add origin https://github.com/你的用户名/LoongarchWorkstationManagerGui.git
git remote add gitee https://gitee.com/你的用户名/LoongarchWorkstationManagerGui.git
git remote add gitcode https://gitcode.com/你的用户名/LoongarchWorkstationManagerGui.git
```

然后每次需要推送时，双击运行：
- Windows: `push_all.bat`
- Linux/Mac: `./push_all.sh`

### 第四步：验证推送

访问各平台仓库页面，确认文件已上传成功：
- ✅ vm_manager.py
- ✅ README.md（应该渲染为美观的文档）
- ✅ 其他项目文件

## 🔐 认证问题处理

### 如果使用 HTTPS

**GitHub**: 需要使用 Personal Access Token
1. 访问: https://github.com/settings/tokens
2. 点击 "Generate new token (classic)"
3. 选择权限: `repo` (完整仓库权限)
4. 生成后复制 Token
5. 推送时使用 Token 代替密码

**Gitee/GitCode**: 直接使用账户密码

### 如果使用 SSH（推荐）

1. 生成 SSH 密钥（如果没有）:
   ```bash
   ssh-keygen -t ed25519 -C "your_email@example.com"
   ```

2. 查看公钥:
   ```bash
   type C:\Users\你的用户名\.ssh\id_ed25519.pub
   ```

3. 将公钥添加到各平台:
   - GitHub: Settings → SSH and GPG keys
   - Gitee: 设置 → SSH 公钥
   - GitCode: 设置 → SSH Keys

4. 使用 SSH 地址替换 HTTPS 地址:
   ```bash
   git remote set-url origin git@github.com:你的用户名/LoongarchWorkstationManagerGui.git
   git remote set-url gitee git@gitee.com:你的用户名/LoongarchWorkstationManagerGui.git
   git remote set-url gitcode git@gitcode.com:你的用户名/LoongarchWorkstationManagerGui.git
   ```

## 📊 常用命令速查

```bash
# 查看远程仓库
git remote -v

# 查看状态
git status

# 添加并提交
git add .
git commit -m "提交说明"

# 推送到所有平台
git push --all

# 或使用脚本
.\push_all.bat      # Windows
./push_all.sh       # Linux/Mac

# 拉取最新代码
git pull origin master
```

## ⚠️ 注意事项

1. **配置文件**: `vm_config.json` 已被 `.gitignore` 排除，不会上传到 Git
2. **大文件**: ISO 镜像和虚拟磁盘文件也被排除
3. **依赖目录**: `venv/`, `build/`, `dist/` 等目录不会上传
4. **首次推送**: 确保远程仓库是空的，否则需要先拉取再合并

## 🎯 后续开发流程

```bash
# 1. 修改代码
# ... 编辑文件 ...

# 2. 查看更改
git status

# 3. 添加并提交
git add .
git commit -m "描述你的更改"

# 4. 推送到所有平台
.\push_all.bat
```

## 📞 需要帮助？

详细指南请查看: `GIT_PUSH_GUIDE.md`

---

**准备好了吗？** 现在就去三个平台创建仓库，然后开始推送吧！🚀
