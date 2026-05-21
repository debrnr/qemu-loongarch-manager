# Deepin LoongArch VM Manager

一个美观的 GUI 界面用于管理 QEMU 虚拟机，专为龙架构（LoongArch）平台上的 Deepin 系统设计。

![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)
![PyQt6](https://img.shields.io/badge/PyQt6-6.4.0+-green.svg)
![License](https://img.shields.io/badge/License-MIT-yellow.svg)

## ✨ 功能特性

- 🖥️ **虚拟机管理**: 启动、停止、测试模式运行
- 💾 **磁盘管理**: 创建、扩容、压缩、格式转换、检查修复
- 📸 **快照管理**: 创建、恢复、删除、从快照启动
- 🌐 **远程连接**: SPICE 显示和 RDP 远程桌面支持
- ⚙️ **配置管理**: 自定义内存、CPU、磁盘大小等参数
- 📋 **日志记录**: 实时查看虚拟机运行日志
- 🎨 **现代界面**: 基于 PyQt6 的美观用户界面

## 📋 系统要求

- **操作系统**: Windows (支持 LoongArch 架构)
- **Python**: >= 3.8
- **QEMU**: 需要预先安装 QEMU for LoongArch
- **依赖库**: PyQt6, PyInstaller (可选，用于打包)

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

## 📦 打包为可执行文件

使用 PyInstaller 将程序打包成单个 exe 文件：

```bash
python build_exe.py
```

打包后的文件位于 `dist/Deepin_VM_Manager.exe`

## 🗂️ 项目结构

```
LoongarchWorkstationManagerGui/
├── vm_manager.py           # 主程序文件
├── build_exe.py            # PyInstaller 打包脚本
├── setup.py                # Python 包安装配置
├── requirements.txt        # Python 依赖列表
├── Deepin_VM_Manager.spec  # PyInstaller 配置文件
├── icon.ico                # 应用程序图标
├── .gitignore              # Git 忽略文件配置
└── README.md               # 项目说明文档
```

## ⚙️ 配置说明

程序会自动生成 `vm_config.json` 配置文件，包含以下默认设置：

```json
{
  "qemu_dir": ".\\qemu",
  "iso_path": ".\\iso\\deepin-desktop-community-25.1.0-loong64.iso",
  "hdd_path": ".\\disk\\deepin_loong64.qcow2",
  "memory": 12288,
  "cpu_cores": 8,
  "spice_port": 5900,
  "rdp_port": 13389,
  "disk_size": 80
}
```

## 🔧 主要功能说明

### 虚拟机控制
- **正常启动**: 使用配置的磁盘和参数启动虚拟机
- **测试启动**: 临时运行，关闭时可选择保存为快照
- **从快照启动**: 选择已有快照快速恢复状态

### 磁盘管理
- 创建新的 QCOW2 格式虚拟磁盘
- 在线扩容磁盘容量
- 压缩磁盘以节省空间
- 格式转换（qcow2/raw/vmdk/vdi）
- 磁盘检查和修复

### 远程访问
- **SPICE**: 高性能图形显示协议（默认端口 5900）
- **RDP**: Windows 远程桌面协议（默认端口 13389）
- 提供 Remote Viewer 快速连接按钮

## 📝 开发说明

### 代码结构
- `VMManager`: 主窗口类，负责界面初始化和事件处理
- `VMRunner`: 后台线程类，用于异步运行 QEMU 进程
- `ModernButton`: 自定义样式按钮组件

### 添加新功能
1. 在对应的标签页设置方法中添加 UI 元素
2. 实现业务逻辑方法
3. 连接信号和槽

## 🤝 贡献指南

欢迎提交 Issue 和 Pull Request！

## 📄 许可证

本项目采用 MIT 许可证

## 🙏 致谢

- [QEMU](https://www.qemu.org/) - 开源虚拟化平台
- [PyQt6](https://www.riverbankcomputing.com/software/pyqt/) - Python Qt 绑定
- [Deepin](https://www.deepin.org/) - 深度操作系统

---

**注意**: 本项目专为龙架构（LoongArch）平台设计，使用前请确保已安装适配的 QEMU 版本。
