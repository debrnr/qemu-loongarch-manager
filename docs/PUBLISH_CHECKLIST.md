# 📋 多平台发布检查清单

## ✅ 已完成项

### GitHub (origin)
- [x] 远程仓库配置: `https://github.com/debrnr/qemu-loongarch-manager`
- [x] 代码推送: 23 个文件已推送
- [x] Tag 推送: `v260521-A4` 已推送
- [ ] **Release 创建**: 待手动创建并上传 EXE

### Gitee
- [x] 远程仓库配置: `https://gitee.com/debrnr/qemu-loongarch-manager`
- [x] 代码推送: 23 个文件已推送
- [x] Tag 推送: `v260521-A4` 已推送
- [ ] **Release 创建**: 待手动创建并上传 EXE

### GitCode
- [x] 远程仓库配置: `https://gitcode.com/debrnr/qemu-loongarch-manager`
- [ ] 代码推送: 需要配置 Personal Access Token
- [ ] Tag 推送: 需要配置 Personal Access Token
- [ ] **Release 创建**: 待配置后创建并上传 EXE

---

## 🚀 待完成操作

### 步骤 1: 配置 GitCode Personal Access Token

#### 方法 A: 使用配置脚本（推荐）

```batch
# 双击运行
setup_gitcode_token.bat

# 按提示输入 Token
```

#### 方法 B: 手动配置

1. **获取 Token**:
   - 访问: https://gitcode.com
   - 登录 → 设置 → 个人访问令牌
   - 创建新令牌，勾选: `read_repository`, `write_repository`, `api`
   - 复制生成的 Token

2. **配置 Git**:
   ```bash
   # 方式 1: URL 嵌入 Token
   git remote set-url gitcode https://你的Token@gitcode.com/debrnr/qemu-loongarch-manager.git
   
   # 方式 2: 使用凭据管理器（更安全）
   git remote set-url gitcode https://gitcode.com/debrnr/qemu-loongarch-manager.git
   # 推送时会弹出窗口让你输入用户名和密码（密码用 Token）
   ```

3. **推送到 GitCode**:
   ```bash
   git push gitcode master
   git push gitcode v260521-A4
   ```

4. **验证**:
   ```bash
   git ls-remote gitcode --tags
   # 应该看到: 42eb3be... refs/tags/v260521-A4
   ```

---

### 步骤 2: 在各平台创建 Release

#### GitHub Release

**链接**: https://github.com/debrnr/qemu-loongarch-manager/releases/new

**操作步骤**:
1. Tag version: 选择 `v260521-A4`
2. Release title: `QML_260521_A4`
3. 粘贴以下内容为描述:

```markdown
## 🎉 QML_260521_A4 发布

**构建时间**: 2026-05-21  
**版本号**: 260521-A4

###  更新内容
- 项目结构优化，脚本文件整理到 scripts/ 目录
- 添加版本管理系统 (version.py)
- 完善自动化发布流程
- 优化文档组织结构

###  Bug 修复
- 修复文件路径问题
- 改进脚本执行逻辑

###  下载
- [QML_260521_A4.exe](附件) - 主程序（推荐）

### 📋 系统要求
- Windows 操作系统
- LoongArch 架构支持
- QEMU for LoongArch

### 🔗 相关链接
- [项目主页](https://github.com/debrnr/qemu-loongarch-manager)
- [完整文档](docs/INDEX.md)
- [命名规则](docs/EXE_NAMING_RULES.md)
- [发布指南](docs/RELEASE_GUIDE.md)
```

4. **上传附件**: 点击 "Attach binaries"，选择 `dist/QML_260521_A4.exe`
5. 勾选 **"Set as the latest release"**
6. 点击 **"Publish release"**

---

#### Gitee Release

**链接**: https://gitee.com/debrnr/qemu-loongarch-manager/releases/new

**操作步骤**:
1. 标签: 选择 `v260521-A4`
2. 标题: `QML_260521_A4`
3. 内容: 粘贴上面的 Release 说明
4. **上传附件**: 点击"添加附件"，选择 `dist/QML_260521_A4.exe`
5. 点击"确定"

---

#### GitCode Release

**链接**: https://gitcode.com/debrnr/qemu-loongarch-manager/releases/new

**操作步骤**:
1. 类似 GitHub/Gitee 的步骤
2. 选择 Tag: `v260521-A4`
3. 填写标题和说明
4. 上传附件: `QML_260521_A4.exe`
5. 点击发布

---

## 📊 最终验证清单

完成后检查以下项目：

### GitHub
- [ ] 访问 https://github.com/debrnr/qemu-loongarch-manager/releases
- [ ] 看到 Release `v260521-A4`
- [ ] 可以下载 `QML_260521_A4.exe`
- [ ] 显示为 "Latest release"

### Gitee
- [ ] 访问 https://gitee.com/debrnr/qemu-loongarch-manager/releases
- [ ] 看到 Release `v260521-A4`
- [ ] 可以下载 `QML_260521_A4.exe`

### GitCode
- [ ] 访问 https://gitcode.com/debrnr/qemu-loongarch-manager/releases
- [ ] 看到 Release `v260521-A4`
- [ ] 可以下载 `QML_260521_A4.exe`

---

## 💡 常见问题

### Q1: GitHub 上看不到所有文件？
**A**: 刷新页面或清除浏览器缓存。文件已经推送成功（23个文件）。

### Q2: GitCode Token 配置后仍然推送失败？
**A**: 
1. 检查 Token 是否正确复制（没有多余空格）
2. 确认 Token 权限包含 `write_repository`
3. 尝试使用 SSH 方式替代 HTTPS

### Q3: Release 上传 EXE 时出错？
**A**: 
1. 确认 EXE 文件存在: `dist/QML_260521_A4.exe`
2. 文件大小约 35.4 MB，确保网络连接稳定
3. 如果上传失败，稍后重试或使用分片上传

### Q4: 如何删除错误的 Release？
**A**: 
- GitHub: Releases 页面 → 编辑 → Delete release
- Gitee: Releases 页面 → 管理 → 删除
- GitCode: 类似上述步骤

---

## 🎯 快速命令参考

```bash
# 查看所有远程仓库
git remote -v

# 查看本地 Tags
git tag -l

# 查看远程 Tags
git ls-remote origin --tags
git ls-remote gitee --tags
git ls-remote gitcode --tags

# 重新推送所有 Tags
git push origin --tags
git push gitee --tags
git push gitcode --tags

# 检查某个平台的推送状态
git ls-remote <platform> --heads
git ls-remote <platform> --tags
```

---

##  总结

当前状态：
- ✅ GitHub: 代码和 Tag 已推送，待创建 Release
- ✅ Gitee: 代码和 Tag 已推送，待创建 Release
- ⚠️ GitCode: 需配置 Token 后推送代码和 Tag，然后创建 Release

下一步：
1. 运行 `setup_gitcode_token.bat` 配置 GitCode
2. 在三个平台分别创建 Release 并上传 EXE
3. 验证所有平台的 Release 是否正常

祝发布顺利！
