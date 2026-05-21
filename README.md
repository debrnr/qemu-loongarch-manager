# Deepin LoongArch VM Manager

一个美观的 GUI 界面用于管理 QEMU 虚拟机，专为龙架构（LoongArch）平台上的 Deepin 系统设计。

![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)
![PyQt6](https://img.shields.io/badge/PyQt6-6.4.0+-green.svg)
![License](https://img.shields.io/badge/License-MIT-yellow.svg)

## 📦 必备软件

### QEMU for LoongArch + VirtViewer

**下载链接**: https://www.alipan.com/s/icTCzEKRXQJ

包含：
- QEMU for LoongArch64
- VirtViewer (SPICE 客户端)

---

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

1. 设置配置路径（见下方目录说明）
2. 点击"创建磁盘"初始化虚拟磁盘
3. 点击"启动虚拟机"开始使用

---

## 📁 目录结构

```
LoongarchWorkstationManagerGui/
├── vm_manager.py              # 主程序入口
├── version.py                 # 版本管理
├── README.md                  # 项目说明
── .gitignore                 # Git 忽略规则
├── LICENSE                    # MIT 许可证
│
├── docs/                      # 📚 文档目录
│   ├── README.md             # 详细使用说明
│   └── INDEX.md              # 文档导航
│
├── scripts/                   #  脚本工具
│   ├── auto_release.py       # 自动发布助手
│   └── release_helper.bat    # Windows 发布助手
│
├── iso/                       # 💿 镜像文件目录
│   └── *.iso                 # 系统安装镜像
│
├── qemu/                      # ⚙️ QEMU 安装目录
│   ├── qemu-system-loongarch64.exe
│   └── share/                # UEFI 固件等
│
├── display/                   # 🖥️ VirtViewer 安装目录
│   └── remote-viewer.exe     # SPICE 客户端
│
├── disk/                      # 💾 虚拟磁盘目录
│   └── *.qcow2               # QCOW2 格式磁盘文件
│
├── loongshare/                # 📂 共享文件夹
│   └── (与虚拟机共享的文件)
│
└── dist/                      # 📦 打包输出目录
    └── QML_YYMMDD_HM.exe     # 生成的可执行文件
```

### 目录说明

| 目录 | 用途 |
|------|------|
| `iso/` | 存放系统安装镜像（*.iso） |
| `loongshare/` | 与虚拟机共享文件的目录 |
| `qemu/` | QEMU 程序安装目录 |
| `display/` | VirtViewer (SPICE 客户端) 安装目录 |
| `disk/` | 虚拟磁盘文件（*.qcow2）存放目录 |

---

## ✨ 功能特性

- 🖥️ **虚拟机管理**: 启动、停止、测试模式运行
- 💾 **磁盘管理**: 创建、扩容、压缩、格式转换
- 📸 **快照管理**: 创建、恢复、删除、从快照启动
- 🌐 **远程连接**: SPICE 显示和 RDP 远程桌面支持
- ⚙️ **配置管理**: 自定义内存、CPU、磁盘大小等参数
-  **日志记录**: 实时查看虚拟机运行日志
- 🎨 **现代界面**: 基于 PyQt6 的美观用户界面

---

##  打包为可执行文件

```bash
python build_exe.py
```

打包后的文件位于 `dist/QML_YYMMDD_HM.exe`

**命名规则**: `QML_日期_时间.exe`  
示例: `QML_260521_C5.exe`

---

## 📋 系统要求

- **操作系统**: Windows (支持 LoongArch 架构)
- **Python**: >= 3.8
- **QEMU**: 需要预先安装 QEMU for LoongArch
- **VirtViewer**: SPICE 客户端（可选，用于远程连接）
- **依赖库**: PyQt6, PyInstaller (可选，用于打包)

---

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

---

## 📄 许可证

本项目采用 MIT 许可证

---

##  致谢

- [QEMU](https://www.qemu.org/) - 开源虚拟化平台
- [PyQt6](https://www.riverbankcomputing.com/software/pyqt/) - Python Qt 绑定
- [Deepin](https://www.deepin.org/) - 深度操作系统

---

**注意**: 本项目专为龙架构（LoongArch）平台设计，使用前请确保已安装适配的 QEMU 版本。

**完整文档**: [docs/README.md](docs/README.md)
