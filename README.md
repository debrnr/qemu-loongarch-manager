# Deepin LoongArch VM Manager

一个美观的 GUI 界面用于管理 QEMU 虚拟机，专为龙架构（LoongArch）平台上的 Deepin 系统设计。

![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)
![PyQt6](https://img.shields.io/badge/PyQt6-6.4.0+-green.svg)
![License](https://img.shields.io/badge/License-MIT-yellow.svg)

## 📚 文档

完整的文档请查看 [docs/INDEX.md](docs/INDEX.md)

**快速链接**:
- [📘 项目说明](docs/README.md) - 功能介绍、安装和使用指南
- [📗 快速开始](docs/QUICK_START.md) - Git 推送快速指南
- [📙 Git 详细指南](docs/GIT_PUSH_GUIDE.md) - 完整的 Git 操作说明
- [📕 项目总结](docs/PROJECT_SUMMARY.md) - 项目整理和统计信息
- [📔 EXE 命名规则](docs/EXE_NAMING_RULES.md) - 版本号格式说明
- [ 发布指南](docs/RELEASE_GUIDE.md) - 如何发布到各平台
- [⚡ 快速发布](docs/QUICK_RELEASE.md) - 一键发布流程
- [📊 发布检查清单](docs/PUBLISH_CHECKLIST.md) - 多平台发布状态跟踪
- [📋 发布状态报告](docs/PUBLISH_STATUS.md) - 当前发布进度
- [📝 Release 模板](docs/RELEASE_NOTES_v260521-A4.md) - v260521-A4 版本说明

---

## ✨ 功能特性

- 🖥️ **虚拟机管理**: 启动、停止、测试模式运行
- 💾 **磁盘管理**: 创建、扩容、压缩、格式转换、检查修复
- 📸 **快照管理**: 创建、恢复、删除、从快照启动
- 🌐 **远程连接**: SPICE 显示和 RDP 远程桌面支持
- ⚙️ **配置管理**: 自定义内存、CPU、磁盘大小等参数
- 📋 **日志记录**: 实时查看虚拟机运行日志
- 🎨 **现代界面**: 基于 PyQt6 的美观用户界面

## 🚀 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 运行程序

```bash
python vm_manager.py
```

### 3. 首次使用

1. 在"配置"标签页设置 QEMU 目录路径
2. 设置 ISO 镜像文件和虚拟磁盘路径
3. 调整硬件配置（内存、CPU核心数等）
4. 点击"保存配置"
5. 在"控制面板"点击"创建磁盘"初始化虚拟磁盘
6. 点击"启动虚拟机"开始使用

更多详细信息请查看 [完整文档](docs/README.md)。

## 📦 打包为可执行文件

```bash
python build_exe.py
```

打包后的文件位于 `dist/Deepin_VM_Manager.exe`

## 📋 系统要求

- **操作系统**: Windows (支持 LoongArch 架构)
- **Python**: >= 3.8
- **QEMU**: 需要预先安装 QEMU for LoongArch
- **依赖库**: PyQt6, PyInstaller (可选，用于打包)

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

## 📄 许可证

本项目采用 MIT 许可证

## 🙏 致谢

- [QEMU](https://www.qemu.org/) - 开源虚拟化平台
- [PyQt6](https://www.riverbankcomputing.com/software/pyqt/) - Python Qt 绑定
- [Deepin](https://www.deepin.org/) - 深度操作系统

---

**注意**: 本项目专为龙架构（LoongArch）平台设计，使用前请确保已安装适配的 QEMU 版本。

**完整文档**: [docs/INDEX.md](docs/INDEX.md)
