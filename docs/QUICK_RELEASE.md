# 🚀 快速发布指南

## 一键发布流程

### 步骤 1: 打包 EXE

```bash
python build_exe.py
```

### 步骤 2: 运行发布助手

**Windows 用户（推荐）**:
```batch
release_helper.bat
```

**或使用 Python 脚本**:
```bash
python auto_release.py
```

### 步骤 3: 访问平台创建 Release

脚本会自动：
- ✅ 检测最新 EXE
- ✅ 创建 Git Tag
- ✅ 推送到远程仓库
- ✅ 生成 Release 说明

你只需要：
1. 点击脚本提供的链接
2. 选择对应的 Tag
3. 粘贴 Release 说明
4. 上传 EXE 文件
5. 点击发布

---

## 📝 完整示例

```bash
# 1. 打包
python build_exe.py

# 输出: dist/QML_260521_A2.exe

# 2. 运行发布助手
python auto_release.py

# 输出:
# ✅ 找到: QML_260521_A2.exe
# 🏷️  版本号: v260521-A2
# ✅ Tag 创建成功
# ✅ 推送成功
# 💾 Release 说明已保存

# 3. 访问链接创建 Release
# - GitHub: https://github.com/.../releases/new
# - Gitee: https://gitee.com/.../releases/new
# - GitCode: https://gitcode.com/.../releases/new
```

---

## 💡 常见问题

### Q: 如何指定自定义版本号？
```bash
python auto_release.py v260522-B3
```

### Q: 忘记添加远程仓库怎么办？
```bash
git remote add origin https://github.com/用户名/仓库名.git
git remote add gitee https://gitee.com/用户名/仓库名.git
git remote add gitcode https://gitcode.com/用户名/仓库名.git
```

### Q: 可以只推送到部分平台吗？
是的，脚本会检测已配置的远程仓库，只推送到存在的平台。

### Q: Release 说明保存在哪里？
当前目录下会生成 `RELEASE_NOTES_v260521-A2.md` 文件。

---

## 🔗 相关文档

- [完整发布指南](RELEASE_GUIDE.md)
- [EXE 命名规则](EXE_NAMING_RULES.md)
- [Git 推送指南](GIT_PUSH_GUIDE.md)
