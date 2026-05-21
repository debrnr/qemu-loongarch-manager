# 📁 项目文件结构说明

## 📂 根目录文件

### 核心程序文件
- `vm_manager.py` - 主程序入口（GUI）
- `version.py` - 版本管理模块

### 配置文件
- `.gitignore` - Git 忽略规则
- `README.md` - 项目说明（链接到文档索引）
- `LICENSE` - MIT 开源许可证

### 临时文件（不提交到 Git）
- `RELEASE_NOTES_*.md` - 自动生成的 Release 说明
- `*.spec` - PyInstaller 构建配置
- `dist/` - 打包输出目录
- `build/` - 构建临时文件

---

## 📂 docs/ - 文档目录

所有项目文档统一存放在此目录。

### 📘 基础文档
- `README.md` - 项目详细说明
- `INDEX.md` - **文档导航中心** 
- `QUICK_START.md` - Git 快速开始指南
- `GIT_PUSH_GUIDE.md` - Git 详细操作指南
- `PROJECT_SUMMARY.md` - 项目总结

### 📔 发布相关文档
- `EXE_NAMING_RULES.md` - EXE 文件命名规范
- `RELEASE_GUIDE.md` - 完整发布指南
- `QUICK_RELEASE.md` - 快速发布流程
- `PUBLISH_CHECKLIST.md` - 发布检查清单
- `PUBLISH_STATUS.md` - 发布状态报告
- `PUBLISH_REPORT.md` - 发布完成报告
- `RELEASE_NOTES_v260521-A4.md` - v260521-A4 Release 模板

---

## 📂 scripts/ - 脚本目录

所有辅助脚本和工具存放在此目录。

###  自动化脚本
- `auto_release.py` - Python 自动发布助手
- `release_helper.bat` - Windows 发布助手
- `setup_gitcode_token.bat` - GitCode Token 配置助手

### 🔧 构建脚本
- `build_exe.py` - EXE 打包脚本
- `push_all.bat` - 批量推送脚本（Windows）
- `push_all.sh` - 批量推送脚本（Linux/Mac）

---

## 📂 archive/ - 归档目录

存放旧版本的配置文件和依赖声明。

- `requirements.txt` - Python 依赖包列表
- `setup.py` - 旧的 setup 配置

---

## 📂 运行时目录（由程序生成）

这些目录在首次运行时自动创建，不提交到 Git。

- `qemu/` - QEMU 程序和固件
- `disk/` - 虚拟机磁盘文件
- `iso/` - 系统镜像文件
- `loongshare/` - 主机与虚拟机共享文件夹
- `snapshots/` - 快照目录
- `temp/` - 临时文件目录

---

## 🎯 快速导航

### 查看文档
→ [docs/INDEX.md](docs/INDEX.md) - 所有文档的导航中心

### 运行程序
```bash
python vm_manager.py
```

### 打包 EXE
```bash
cd scripts
python build_exe.py
```

### 发布到平台
```bash
# 方法 1: Python 脚本
python scripts/auto_release.py

# 方法 2: Windows 批处理
scripts\release_helper.bat
```

### 配置 GitCode
```bash
# 双击运行
scripts\setup_gitcode_token.bat
```

---

## 📊 文件统计

| 类型 | 数量 | 说明 |
|------|------|------|
| Python 文件 | 3 | 核心程序和脚本 |
| Markdown 文档 | 12 | 完整的项目文档 |
| 批处理脚本 | 3 | Windows 辅助工具 |
| Shell 脚本 | 1 | Linux/Mac 辅助工具 |
| 配置文件 | 2 | .gitignore, LICENSE |

---

## 💡 使用建议

1. **阅读文档**: 先从 [docs/INDEX.md](docs/INDEX.md) 开始
2. **运行程序**: 直接运行 `vm_manager.py`
3. **打包发布**: 使用 `scripts/` 目录中的自动化脚本
4. **保持整洁**: 不要将 `dist/`, `build/` 等临时目录提交到 Git

---

**最后更新**: 2026-05-21  
**维护者**: debrnr
