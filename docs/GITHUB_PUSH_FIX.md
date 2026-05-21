# 🔧 GitHub 推送问题解决指南

##  当前问题

GitHub HTTPS 推送失败，错误信息：
```
fatal: unable to access 'https://github.com/debrnr/qemu-loongarch-manager.git/': 
Failed to connect to github.com port 443 after 21055 ms: Could not connect to server
```

---

## ✅ 解决方案

### 方案 1: 使用 SSH 方式（推荐）⭐

#### 步骤 1: 生成 SSH 密钥

```bash
# 打开 PowerShell 或 Git Bash
ssh-keygen -t ed25519 -C "debrnr@github.com"

# 按 Enter 使用默认路径
# 输入 passphrase（可选，直接按 Enter 跳过）
```

生成的文件：
- 私钥: `C:\Users\你的用户名\.ssh\id_ed25519`
- 公钥: `C:\Users\你的用户名\.ssh\id_ed25519.pub`

#### 步骤 2: 添加公钥到 GitHub

1. 复制公钥内容：
   ```bash
   # PowerShell
   Get-Content $env:USERPROFILE\.ssh\id_ed25519.pub | clip
   
   # Git Bash
   cat ~/.ssh/id_ed25519.pub | clip
   ```

2. 访问 GitHub: https://github.com/settings/keys
3. 点击 **"New SSH key"**
4. 粘贴公钥内容
5. Title: `Windows Desktop`
6. 点击 **"Add SSH key"**

#### 步骤 3: 测试 SSH 连接

```bash
ssh -T git@github.com

# 应该看到: Hi debrnr! You've successfully authenticated...
```

#### 步骤 4: 更改远程仓库为 SSH

```bash
git remote set-url origin git@github.com:debrnr/qemu-loongarch-manager.git
```

#### 步骤 5: 重新推送

```bash
git push origin master
git push origin v260521-A4
```

---

### 方案 2: 配置 Git 代理（如果有代理）

如果你使用代理软件（如 Clash、V2Ray 等）：

```bash
# 设置 HTTP 代理
git config --global http.proxy http://127.0.0.1:7890
git config --global https.proxy http://127.0.0.1:7890

# 或者 SOCKS5 代理
git config --global http.proxy socks5://127.0.0.1:7890
git config --global https.proxy socks5://127.0.0.1:7890

# 测试推送
git push origin master

# 如果不需要了，取消代理
git config --global --unset http.proxy
git config --global --unset https.proxy
```

**注意**: 将 `7890` 替换为你的代理端口号。

---

### 方案 3: 使用 GitHub Desktop

1. 下载 GitHub Desktop: https://desktop.github.com/
2. 登录你的 GitHub 账号
3. 克隆仓库: `https://github.com/debrnr/qemu-loongarch-manager`
4. 在 GitHub Desktop 中推送更改

---

### 方案 4: 稍后重试

有时是临时的网络问题，可以：

```bash
# 等待 5-10 分钟后重试
Start-Sleep -Seconds 300
git push origin master
```

---

## 📊 当前状态

| 平台 | 状态 | 备注 |
|------|------|------|
| **GitHub** | ❌ 推送失败 | HTTPS 连接超时 |
| **Gitee** | ✅ 成功 | 所有代码已推送 |
| **GitCode** | ⚠️ 待配置 | 需要 Personal Access Token |

---

## 🎯 推荐操作

**立即执行**（选择其中一个方案）：

### 如果使用 SSH（最佳方案）：

```bash
# 1. 生成 SSH 密钥
ssh-keygen -t ed25519 -C "debrnr@github.com"

# 2. 复制公钥
Get-Content $env:USERPROFILE\.ssh\id_ed25519.pub | clip

# 3. 添加到 GitHub: https://github.com/settings/keys

# 4. 更改远程仓库
git remote set-url origin git@github.com:debrnr/qemu-loongarch-manager.git

# 5. 推送
git push origin master
git push origin v260521-A4
```

### 如果使用代理：

```bash
# 1. 设置代理（根据你的代理软件调整端口）
git config --global http.proxy http://127.0.0.1:7890
git config --global https.proxy http://127.0.0.1:7890

# 2. 推送
git push origin master
git push origin v260521-A4

# 3. 成功后取消代理（可选）
git config --global --unset http.proxy
git config --global --unset https.proxy
```

---

##  验证推送成功

推送后检查：

```bash
# 查看 GitHub 上的最新提交
git ls-remote origin HEAD

# 应该看到最新的 commit hash
```

访问: https://github.com/debrnr/qemu-loongarch-manager

应该看到所有文件（包括最新的文档整理）。

---

## 🔗 相关资源

- [GitHub SSH 指南](https://docs.github.com/cn/authentication/connecting-to-github-with-ssh)
- [Git 代理配置](https://git-scm.com/docs/git-config)
- [GitHub Desktop](https://desktop.github.com/)

---

**需要帮助？** 

如果以上方案都无法解决，请：
1. 检查防火墙设置
2. 尝试更换网络环境
3. 使用 Gitee 作为主要平台（已推送成功）
4. 稍后再试 GitHub
