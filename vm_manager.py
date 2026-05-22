#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Deepin LoongArch VM 管理器
美观的 GUI 界面用于管理 QEMU 虚拟机
"""

import sys
import os
import subprocess
import threading
import json
from pathlib import Path

# 导入版本信息
try:
    from version import VERSION_STR
except ImportError:
    VERSION_STR = "QML v1.0"


def get_resource_path(relative_path):
    """获取资源文件路径（支持开发和打包后的环境）"""
    if hasattr(sys, '_MEIPASS'):
        # PyInstaller 打包后的临时目录
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)

try:
    from PyQt6.QtWidgets import (
        QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
        QLabel, QPushButton, QSpinBox, QLineEdit, QTextEdit, QGroupBox,
        QGridLayout, QMessageBox, QFileDialog, QStatusBar, QProgressBar,
        QTabWidget, QCheckBox, QComboBox, QInputDialog, QProgressDialog
    )
    from PyQt6.QtCore import Qt, QThread, pyqtSignal, QTimer
    from PyQt6.QtGui import QFont, QIcon, QColor, QPalette
    PYQT6_AVAILABLE = True
except ImportError:
    PYQT6_AVAILABLE = False

if not PYQT6_AVAILABLE:
    try:
        from PyQt5.QtWidgets import (
            QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
            QLabel, QPushButton, QSpinBox, QLineEdit, QTextEdit, QGroupBox,
            QGridLayout, QMessageBox, QFileDialog, QStatusBar, QProgressBar,
            QTabWidget, QCheckBox, QComboBox, QInputDialog, QProgressDialog
        )
        from PyQt5.QtCore import Qt, QThread, pyqtSignal, QTimer
        from PyQt5.QtGui import QFont, QIcon, QColor
        PYQT5_AVAILABLE = True
    except ImportError:
        PYQT5_AVAILABLE = False

if not PYQT6_AVAILABLE and not PYQT5_AVAILABLE:
    print("错误: 需要安装 PyQt6 或 PyQt5")
    print("请运行: pip install PyQt6")
    sys.exit(1)


class VMRunner(QThread):
    """在后台线程中运行虚拟机"""
    output_signal = pyqtSignal(str)
    finished_signal = pyqtSignal(int)

    def __init__(self, command):
        super().__init__()
        self.command = command
        self.process = None
        self.running = False

    def run(self):
        self.running = True
        try:
            self.process = subprocess.Popen(
                self.command,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                universal_newlines=True,
                creationflags=subprocess.CREATE_NO_WINDOW
            )

            for line in iter(self.process.stdout.readline, ''):
                if not self.running:
                    break
                if line:
                    self.output_signal.emit(line.strip())

            self.process.wait()
            self.finished_signal.emit(self.process.returncode)
        except Exception as e:
            self.output_signal.emit(f"错误: {str(e)}")
            self.finished_signal.emit(-1)

    def stop(self):
        self.running = False
        if self.process:
            try:
                self.process.terminate()
                self.process.wait(timeout=5)
            except:
                try:
                    self.process.kill()
                except:
                    pass


class BackupThread(QThread):
    """在后台线程中执行备份操作"""
    progress_signal = pyqtSignal(str)
    finished_signal = pyqtSignal(bool, str)

    def __init__(self, qemu_img, source, target, backup_type="full"):
        super().__init__()
        self.qemu_img = qemu_img
        self.source = source
        self.target = target
        self.backup_type = backup_type
        self.process = None
        self.running = False

    def run(self):
        self.running = True
        try:
            if self.backup_type == "full":
                # 完整备份：使用 convert -c 进行压缩复制
                cmd = [
                    self.qemu_img,
                    "convert", "-O", "qcow2", "-c",
                    "-p",  # 显示进度
                    self.source, self.target
                ]
            else:
                # 增量备份：创建外部快照
                cmd = [
                    self.qemu_img,
                    "create", "-f", "qcow2",
                    "-b", self.source,
                    "-F", "qcow2",
                    self.target
                ]

            self.process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                universal_newlines=True,
                creationflags=subprocess.CREATE_NO_WINDOW
            )

            # 读取输出并发送进度信号
            for line in iter(self.process.stdout.readline, ''):
                if not self.running:
                    break
                if line:
                    self.progress_signal.emit(line.strip())

            self.process.wait()

            if self.process.returncode == 0:
                self.finished_signal.emit(True, "备份成功")
            else:
                self.finished_signal.emit(False, f"备份失败，返回码: {self.process.returncode}")

        except Exception as e:
            self.finished_signal.emit(False, f"备份出错: {str(e)}")

    def stop(self):
        self.running = False
        if self.process:
            try:
                self.process.terminate()
                self.process.wait(timeout=5)
            except:
                try:
                    self.process.kill()
                except:
                    pass


class ModernButton(QPushButton):
    """自定义现代风格按钮"""
    def __init__(self, text, color="#2196F3", parent=None):
        super().__init__(text, parent)
        self.setStyleSheet(f"""
            QPushButton {{
                background-color: {color};
                color: white;
                border: none;
                padding: 10px 20px;
                font-size: 14px;
                font-weight: bold;
                border-radius: 6px;
                min-width: 120px;
            }}
            QPushButton:hover {{
                background-color: {self._darken_color(color)};
            }}
            QPushButton:pressed {{
                background-color: {self._darken_color(color, 0.3)};
            }}
            QPushButton:disabled {{
                background-color: #cccccc;
                color: #666666;
            }}
        """)

    def _darken_color(self, color, factor=0.1):
        """使颜色变暗"""
        color = color.lstrip('#')
        rgb = tuple(int(color[i:i+2], 16) for i in (0, 2, 4))
        darkened = tuple(max(0, int(c * (1 - factor))) for c in rgb)
        return f"#{darkened[0]:02x}{darkened[1]:02x}{darkened[2]:02x}"


class VMManager(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(f"QML - QEMU Manager for LoongArch ({VERSION_STR})")
        self.setMinimumSize(600, 400)
        self.resize(900, 800)
        self.vm_runner = None
        self.config_file = Path("vm_config.json")

        # 默认配置
        self.default_config = {
            "qemu_dir": ".\\qemu",
            "iso_path": ".\\iso\\deepin-desktop-community-25.1.0-loong64.iso",
            "hdd_path": ".\\disk\\deepin_loong64.qcow2",
            "snapshot_dir": ".\\disk\\snapshot",
            "memory": 12288,
            "cpu_cores": 8,
            "spice_port": 5900,
            "rdp_port": 13389,
            "disk_size": 80
        }

        self.config = self.load_config()
        self.init_ui()
        self.apply_styles()

    def load_config(self):
        """加载配置文件"""
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    loaded = json.load(f)
                    # 合并默认配置
                    return {**self.default_config, **loaded}
            except:
                pass
        return self.default_config.copy()

    def save_config(self):
        """保存配置文件"""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=2, ensure_ascii=False)
        except Exception as e:
            QMessageBox.warning(self, "警告", f"保存配置失败: {e}")

    def apply_styles(self):
        """应用现代样式"""
        # 设置窗口图标
        icon_path = get_resource_path("icon.ico")
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))

        self.setStyleSheet("""
            QMainWindow {
                background-color: #f5f5f5;
            }
            QWidget {
                font-family: "Microsoft YaHei", "Segoe UI", sans-serif;
            }
            QGroupBox {
                font-weight: bold;
                font-size: 13px;
                border: 2px solid #e0e0e0;
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 10px;
                background-color: white;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
                color: #1976D2;
            }
            QLabel {
                font-size: 12px;
                color: #333333;
            }
            QLineEdit {
                padding: 8px;
                border: 2px solid #e0e0e0;
                border-radius: 4px;
                font-size: 12px;
                background-color: white;
            }
            QLineEdit:focus {
                border-color: #2196F3;
            }
            QSpinBox {
                padding: 8px;
                border: 2px solid #e0e0e0;
                border-radius: 4px;
                font-size: 12px;
                background-color: white;
            }
            QTextEdit {
                border: 2px solid #e0e0e0;
                border-radius: 4px;
                font-family: "Consolas", "Courier New", monospace;
                font-size: 11px;
                background-color: #1e1e1e;
                color: #d4d4d4;
            }
            QTabWidget::pane {
                border: 2px solid #e0e0e0;
                border-radius: 8px;
                background-color: white;
            }
            QTabBar::tab {
                padding: 10px 20px;
                margin-right: 2px;
                background-color: #e0e0e0;
                border-top-left-radius: 4px;
                border-top-right-radius: 4px;
            }
            QTabBar::tab:selected {
                background-color: #2196F3;
                color: white;
            }
            QStatusBar {
                background-color: #333333;
                color: white;
            }
        """)

    def init_ui(self):
        """初始化界面"""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        main_layout = QVBoxLayout(central_widget)
        main_layout.setSpacing(10)
        main_layout.setContentsMargins(10, 10, 10, 10)

        # 创建标签页
        tabs = QTabWidget()
        main_layout.addWidget(tabs)

        # 控制面板标签页
        control_tab = QWidget()
        tabs.addTab(control_tab, "⚙️ 控制面板")
        self.setup_control_tab(control_tab)

        # 配置标签页
        config_tab = QWidget()
        tabs.addTab(config_tab, "🔧 配置")
        self.setup_config_tab(config_tab)

        # 磁盘管理标签页
        disk_tab = QWidget()
        tabs.addTab(disk_tab, "💾 磁盘管理")
        self.setup_disk_tab(disk_tab)

        # 快照标签页
        snapshot_tab = QWidget()
        tabs.addTab(snapshot_tab, "📸 快照")
        self.setup_snapshot_tab(snapshot_tab)

        # 日志标签页
        log_tab = QWidget()
        tabs.addTab(log_tab, "📋 日志")
        self.setup_log_tab(log_tab)

        # 状态栏
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("就绪")

        # 状态指示器
        self.status_indicator = QLabel("● 停止")
        self.status_indicator.setStyleSheet("color: #f44336; font-weight: bold;")
        self.status_bar.addPermanentWidget(self.status_indicator)

    def setup_control_tab(self, parent):
        """设置控制面板标签页"""
        layout = QVBoxLayout(parent)
        layout.setSpacing(15)

        # 状态卡片
        status_group = QGroupBox("虚拟机状态")
        status_layout = QGridLayout(status_group)

        self.status_text = QLabel("状态: 停止")
        self.status_text.setStyleSheet("font-size: 16px; color: #f44336;")
        status_layout.addWidget(self.status_text, 0, 0)

        self.config_summary = QLabel(self.get_config_summary())
        self.config_summary.setStyleSheet("color: #666;")
        status_layout.addWidget(self.config_summary, 1, 0)

        layout.addWidget(status_group)

        # 快速操作按钮
        buttons_group = QGroupBox("快速操作")
        buttons_layout = QHBoxLayout(buttons_group)

        self.start_btn = ModernButton("▶ 启动虚拟机", "#4CAF50")
        self.start_btn.clicked.connect(self.start_vm)
        buttons_layout.addWidget(self.start_btn)

        self.stop_btn = ModernButton("⏹ 停止虚拟机", "#f44336")
        self.stop_btn.clicked.connect(self.stop_vm)
        self.stop_btn.setEnabled(False)
        buttons_layout.addWidget(self.stop_btn)

        self.create_disk_btn = ModernButton("💾 创建磁盘", "#FF9800")
        self.create_disk_btn.clicked.connect(self.create_disk)
        buttons_layout.addWidget(self.create_disk_btn)

        layout.addWidget(buttons_group)

        # 测试启动区域
        test_group = QGroupBox("🧪 测试启动（临时运行）")
        test_layout = QVBoxLayout(test_group)

        test_desc = QLabel("启动临时虚拟机，关闭时提示是否保存为快照。适合测试软件或临时使用。")
        test_desc.setWordWrap(True)
        test_desc.setStyleSheet("color: #666; font-size: 11px;")
        test_layout.addWidget(test_desc)

        self.test_start_btn = ModernButton("🧪 测试启动", "#607D8B")
        self.test_start_btn.clicked.connect(self.start_test_vm)
        test_layout.addWidget(self.test_start_btn)

        layout.addWidget(test_group)

        # 从快照启动区域
        snapshot_start_group = QGroupBox("📸 从快照启动")
        snapshot_start_layout = QVBoxLayout(snapshot_start_group)

        snapshot_start_desc = QLabel("选择一个快照启动虚拟机，启动后可在快照标签页管理。")
        snapshot_start_desc.setWordWrap(True)
        snapshot_start_desc.setStyleSheet("color: #666; font-size: 11px;")
        snapshot_start_layout.addWidget(snapshot_start_desc)

        # 快照选择下拉框
        select_layout = QHBoxLayout()
        select_layout.addWidget(QLabel("选择快照:"))
        self.snapshot_combo = QComboBox()
        self.snapshot_combo.setPlaceholderText("点击刷新加载快照列表...")
        select_layout.addWidget(self.snapshot_combo)

        refresh_btn = QPushButton("🔄 刷新")
        refresh_btn.clicked.connect(self.refresh_snapshot_list)
        select_layout.addWidget(refresh_btn)
        snapshot_start_layout.addLayout(select_layout)

        # 启动按钮
        self.snapshot_start_btn = ModernButton("📸 从选定快照启动", "#E91E63")
        self.snapshot_start_btn.clicked.connect(self.start_from_snapshot)
        snapshot_start_layout.addWidget(self.snapshot_start_btn)

        layout.addWidget(snapshot_start_group)

        # 连接信息
        info_group = QGroupBox("连接信息")
        info_layout = QGridLayout(info_group)

        info_layout.addWidget(QLabel("SPICE 显示:"), 0, 0)
        self.spice_info = QLabel(f"127.0.0.1:{self.config['spice_port']}")
        self.spice_info.setStyleSheet("color: #2196F3; font-weight: bold;")
        info_layout.addWidget(self.spice_info, 0, 1)

        info_layout.addWidget(QLabel("RDP 远程桌面:"), 1, 0)
        self.rdp_info = QLabel(f"127.0.0.1:{self.config['rdp_port']}")
        self.rdp_info.setStyleSheet("color: #2196F3; font-weight: bold;")
        info_layout.addWidget(self.rdp_info, 1, 1)

        # Remote Viewer 按钮
        self.remote_viewer_btn = ModernButton("🖥️ 打开 Remote Viewer", "#9C27B0")
        self.remote_viewer_btn.clicked.connect(self.open_remote_viewer)
        info_layout.addWidget(self.remote_viewer_btn, 2, 0, 1, 2)

        # RDP 连接按钮
        self.rdp_btn = ModernButton("🖥️ 连接 RDP 远程桌面", "#00BCD4")
        self.rdp_btn.clicked.connect(self.connect_rdp)
        info_layout.addWidget(self.rdp_btn, 3, 0, 1, 2)

        # RDP 使用说明
        help_btn = QPushButton("📖 查看 RDP 使用说明")
        help_btn.clicked.connect(self.show_rdp_help)
        info_layout.addWidget(help_btn, 4, 0, 1, 2)

        layout.addWidget(info_group)

        layout.addStretch()

    def setup_config_tab(self, parent):
        """设置配置标签页"""
        layout = QVBoxLayout(parent)
        layout.setSpacing(15)

        # 路径配置
        paths_group = QGroupBox("路径配置")
        paths_layout = QGridLayout(paths_group)

        # QEMU 目录
        paths_layout.addWidget(QLabel("QEMU 目录:"), 0, 0)
        self.qemu_dir_input = QLineEdit(self.config['qemu_dir'])
        paths_layout.addWidget(self.qemu_dir_input, 0, 1)
        qemu_browse = QPushButton("浏览...")
        qemu_browse.clicked.connect(lambda: self.browse_dir(self.qemu_dir_input))
        paths_layout.addWidget(qemu_browse, 0, 2)

        # ISO 路径
        paths_layout.addWidget(QLabel("ISO 镜像:"), 1, 0)
        self.iso_input = QLineEdit(self.config['iso_path'])
        paths_layout.addWidget(self.iso_input, 1, 1)
        iso_browse = QPushButton("浏览...")
        iso_browse.clicked.connect(lambda: self.browse_file(self.iso_input, "ISO 文件 (*.iso)"))
        paths_layout.addWidget(iso_browse, 1, 2)

        # 磁盘路径
        paths_layout.addWidget(QLabel("虚拟磁盘:"), 2, 0)
        self.hdd_input = QLineEdit(self.config['hdd_path'])
        paths_layout.addWidget(self.hdd_input, 2, 1)
        hdd_browse = QPushButton("浏览...")
        hdd_browse.clicked.connect(lambda: self.browse_file(self.hdd_input, "QCOW2 文件 (*.qcow2)"))
        paths_layout.addWidget(hdd_browse, 2, 2)

        layout.addWidget(paths_group)

        # 硬件配置
        hardware_group = QGroupBox("硬件配置")
        hardware_layout = QGridLayout(hardware_group)

        # 内存
        hardware_layout.addWidget(QLabel("内存 (MB):"), 0, 0)
        self.memory_spin = QSpinBox()
        self.memory_spin.setRange(1024, 65536)
        self.memory_spin.setValue(self.config['memory'])
        self.memory_spin.setSingleStep(1024)
        hardware_layout.addWidget(self.memory_spin, 0, 1)

        # CPU 核心
        hardware_layout.addWidget(QLabel("CPU 核心数:"), 1, 0)
        self.cpu_spin = QSpinBox()
        self.cpu_spin.setRange(1, 32)
        self.cpu_spin.setValue(self.config['cpu_cores'])
        hardware_layout.addWidget(self.cpu_spin, 1, 1)

        # 磁盘大小
        hardware_layout.addWidget(QLabel("磁盘大小 (GB):"), 2, 0)
        self.disk_size_spin = QSpinBox()
        self.disk_size_spin.setRange(10, 500)
        self.disk_size_spin.setValue(self.config['disk_size'])
        hardware_layout.addWidget(self.disk_size_spin, 2, 1)

        layout.addWidget(hardware_group)

        # 网络配置
        network_group = QGroupBox("网络配置")
        network_layout = QGridLayout(network_group)

        network_layout.addWidget(QLabel("SPICE 端口:"), 0, 0)
        self.spice_spin = QSpinBox()
        self.spice_spin.setRange(5900, 5999)
        self.spice_spin.setValue(self.config['spice_port'])
        network_layout.addWidget(self.spice_spin, 0, 1)

        network_layout.addWidget(QLabel("RDP 转发端口:"), 1, 0)
        self.rdp_spin = QSpinBox()
        self.rdp_spin.setRange(10000, 65535)
        self.rdp_spin.setValue(self.config['rdp_port'])
        network_layout.addWidget(self.rdp_spin, 1, 1)

        layout.addWidget(network_group)

        # 保存按钮
        save_btn = ModernButton("💾 保存配置", "#2196F3")
        save_btn.clicked.connect(self.save_settings)
        layout.addWidget(save_btn)

        layout.addStretch()

    def setup_disk_tab(self, parent):
        """设置磁盘管理标签页"""
        layout = QVBoxLayout(parent)
        layout.setSpacing(15)

        # 磁盘信息
        info_group = QGroupBox("磁盘信息")
        info_layout = QGridLayout(info_group)

        info_layout.addWidget(QLabel("磁盘路径:"), 0, 0)
        self.disk_path_label = QLabel(self.config['hdd_path'])
        self.disk_path_label.setStyleSheet("color: #666;")
        info_layout.addWidget(self.disk_path_label, 0, 1)

        info_layout.addWidget(QLabel("磁盘状态:"), 1, 0)
        self.disk_status_label = QLabel("未知")
        self.disk_status_label.setStyleSheet("color: #666;")
        info_layout.addWidget(self.disk_status_label, 1, 1)

        info_layout.addWidget(QLabel("虚拟大小:"), 2, 0)
        self.disk_virtual_size = QLabel("未知")
        self.disk_virtual_size.setStyleSheet("color: #666;")
        info_layout.addWidget(self.disk_virtual_size, 2, 1)

        info_layout.addWidget(QLabel("实际大小:"), 3, 0)
        self.disk_actual_size = QLabel("未知")
        self.disk_actual_size.setStyleSheet("color: #666;")
        info_layout.addWidget(self.disk_actual_size, 3, 1)

        # 刷新信息按钮
        refresh_btn = QPushButton("🔄 刷新信息")
        refresh_btn.clicked.connect(self.refresh_disk_info)
        info_layout.addWidget(refresh_btn, 4, 0, 1, 2)

        layout.addWidget(info_group)

        # 磁盘操作
        ops_group = QGroupBox("磁盘操作")
        ops_layout = QVBoxLayout(ops_group)

        # 扩容
        resize_layout = QHBoxLayout()
        resize_layout.addWidget(QLabel("扩容到 (GB):"))
        self.resize_spin = QSpinBox()
        self.resize_spin.setRange(1, 500)
        self.resize_spin.setValue(self.config['disk_size'])
        resize_layout.addWidget(self.resize_spin)
        resize_btn = ModernButton("💿 扩容磁盘", "#FF9800")
        resize_btn.clicked.connect(self.resize_disk)
        resize_layout.addWidget(resize_btn)
        ops_layout.addLayout(resize_layout)

        # 压缩
        compact_btn = ModernButton("🗜️ 压缩磁盘", "#4CAF50")
        compact_btn.clicked.connect(self.compact_disk)
        ops_layout.addWidget(compact_btn)

        # 转换格式
        convert_layout = QHBoxLayout()
        convert_layout.addWidget(QLabel("转换为:"))
        self.convert_format = QComboBox()
        self.convert_format.addItems(["qcow2", "raw", "vmdk", "vdi"])
        convert_layout.addWidget(self.convert_format)
        convert_btn = ModernButton("🔄 转换格式", "#2196F3")
        convert_btn.clicked.connect(self.convert_disk)
        convert_layout.addWidget(convert_btn)
        ops_layout.addLayout(convert_layout)

        layout.addWidget(ops_group)

        # 备份操作
        backup_group = QGroupBox("💾 备份操作")
        backup_layout = QVBoxLayout(backup_group)

        # 备份路径选择
        backup_path_layout = QHBoxLayout()
        backup_path_layout.addWidget(QLabel("备份路径:"))
        self.backup_path_input = QLineEdit()
        self.backup_path_input.setPlaceholderText("选择备份保存位置...")
        backup_path_layout.addWidget(self.backup_path_input)
        backup_browse_btn = QPushButton("浏览...")
        backup_browse_btn.clicked.connect(self.browse_backup_path)
        backup_path_layout.addWidget(backup_browse_btn)
        backup_layout.addLayout(backup_path_layout)

        # 备份按钮
        backup_btn_layout = QHBoxLayout()
        full_backup_btn = ModernButton("💾 完整备份", "#9C27B0")
        full_backup_btn.clicked.connect(self.full_backup_disk)
        backup_btn_layout.addWidget(full_backup_btn)

        incremental_backup_btn = ModernButton("📦 增量备份", "#673AB7")
        incremental_backup_btn.clicked.connect(self.incremental_backup_disk)
        backup_btn_layout.addWidget(incremental_backup_btn)
        backup_layout.addLayout(backup_btn_layout)

        layout.addWidget(backup_group)

        # 其他操作
        other_group = QGroupBox("其他操作")
        other_layout = QHBoxLayout(other_group)

        check_btn = QPushButton("🔍 检查磁盘")
        check_btn.clicked.connect(self.check_disk)
        other_layout.addWidget(check_btn)

        repair_btn = QPushButton("🔧 修复磁盘")
        repair_btn.clicked.connect(self.repair_disk)
        other_layout.addWidget(repair_btn)

        delete_btn = QPushButton("🗑️ 删除磁盘")
        delete_btn.setStyleSheet("background-color: #f44336; color: white;")
        delete_btn.clicked.connect(self.delete_disk)
        other_layout.addWidget(delete_btn)

        layout.addWidget(other_group)

        layout.addStretch()

    def setup_snapshot_tab(self, parent):
        """设置快照标签页"""
        layout = QVBoxLayout(parent)
        layout.setSpacing(15)

        # 创建快照
        create_group = QGroupBox("创建快照")
        create_layout = QGridLayout(create_group)

        create_layout.addWidget(QLabel("快照名称:"), 0, 0)
        self.snapshot_name = QLineEdit()
        self.snapshot_name.setPlaceholderText("输入快照名称...")
        create_layout.addWidget(self.snapshot_name, 0, 1)

        create_layout.addWidget(QLabel("描述:"), 1, 0)
        self.snapshot_desc = QLineEdit()
        self.snapshot_desc.setPlaceholderText("可选描述...")
        create_layout.addWidget(self.snapshot_desc, 1, 1)

        create_btn = ModernButton("📸 创建快照", "#4CAF50")
        create_btn.clicked.connect(self.create_snapshot)
        create_layout.addWidget(create_btn, 2, 0, 1, 2)

        layout.addWidget(create_group)

        # 快照路径设置
        path_group = QGroupBox("快照保存路径")
        path_layout = QGridLayout(path_group)

        path_layout.addWidget(QLabel("快照目录:"), 0, 0)
        self.snapshot_dir_input = QLineEdit(self.config.get('snapshot_dir', '.\\disk\\snapshot'))
        self.snapshot_dir_input.setPlaceholderText("选择快照保存目录...")
        path_layout.addWidget(self.snapshot_dir_input, 0, 1)

        snapshot_browse_btn = QPushButton("浏览...")
        snapshot_browse_btn.clicked.connect(self.browse_snapshot_dir)
        path_layout.addWidget(snapshot_browse_btn, 0, 2)

        save_path_btn = QPushButton("💾 保存路径设置")
        save_path_btn.clicked.connect(self.save_snapshot_dir)
        path_layout.addWidget(save_path_btn, 1, 0, 1, 3)

        layout.addWidget(path_group)

        # 快照列表
        list_group = QGroupBox("快照列表")
        list_layout = QVBoxLayout(list_group)

        self.snapshot_list = QTextEdit()
        self.snapshot_list.setReadOnly(True)
        self.snapshot_list.setPlaceholderText("点击刷新查看快照列表...")
        list_layout.addWidget(self.snapshot_list)

        # 快照操作按钮
        btn_layout = QHBoxLayout()

        refresh_snap_btn = QPushButton("🔄 刷新列表")
        refresh_snap_btn.clicked.connect(self.list_snapshots)
        btn_layout.addWidget(refresh_snap_btn)

        restore_btn = ModernButton("⏪ 恢复快照", "#FF9800")
        restore_btn.clicked.connect(self.restore_snapshot)
        btn_layout.addWidget(restore_btn)

        delete_snap_btn = QPushButton("🗑️ 删除快照")
        delete_snap_btn.setStyleSheet("background-color: #f44336; color: white;")
        delete_snap_btn.clicked.connect(self.delete_snapshot)
        btn_layout.addWidget(delete_snap_btn)

        list_layout.addLayout(btn_layout)
        layout.addWidget(list_group)

        layout.addStretch()

    def setup_log_tab(self, parent):
        """设置日志标签页"""
        layout = QVBoxLayout(parent)

        # 日志显示区域
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setPlaceholderText("虚拟机日志将显示在这里...")
        layout.addWidget(self.log_text)

        # 日志操作按钮
        buttons_layout = QHBoxLayout()

        clear_btn = QPushButton("🗑️ 清空日志")
        clear_btn.clicked.connect(self.log_text.clear)
        buttons_layout.addWidget(clear_btn)

        save_log_btn = QPushButton("💾 保存日志")
        save_log_btn.clicked.connect(self.save_log)
        buttons_layout.addWidget(save_log_btn)

        buttons_layout.addStretch()
        layout.addLayout(buttons_layout)

    def get_config_summary(self):
        """获取配置摘要"""
        return (f"内存: {self.config['memory']} MB | "
                f"CPU: {self.config['cpu_cores']} 核 | "
                f"磁盘: {self.config['disk_size']} GB")

    def browse_dir(self, line_edit):
        """浏览目录"""
        dir_path = QFileDialog.getExistingDirectory(self, "选择目录", line_edit.text())
        if dir_path:
            line_edit.setText(dir_path)

    def browse_file(self, line_edit, filter_str):
        """浏览文件"""
        file_path, _ = QFileDialog.getOpenFileName(self, "选择文件", line_edit.text(), filter_str)
        if file_path:
            line_edit.setText(file_path)

    def save_settings(self):
        """保存设置"""
        self.config['qemu_dir'] = self.qemu_dir_input.text()
        self.config['iso_path'] = self.iso_input.text()
        self.config['hdd_path'] = self.hdd_input.text()
        self.config['memory'] = self.memory_spin.value()
        self.config['cpu_cores'] = self.cpu_spin.value()
        self.config['disk_size'] = self.disk_size_spin.value()
        self.config['spice_port'] = self.spice_spin.value()
        self.config['rdp_port'] = self.rdp_spin.value()

        self.save_config()

        # 更新界面显示
        self.config_summary.setText(self.get_config_summary())
        self.spice_info.setText(f"127.0.0.1:{self.config['spice_port']}")
        self.rdp_info.setText(f"127.0.0.1:{self.config['rdp_port']}")

        QMessageBox.information(self, "成功", "配置已保存！")

    def create_disk(self):
        """创建虚拟磁盘"""
        hdd_path = self.config['hdd_path']
        disk_size = self.config['disk_size']

        if os.path.exists(hdd_path):
            reply = QMessageBox.question(
                self, "确认",
                f"磁盘文件已存在:\n{hdd_path}\n\n是否重新创建?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            if reply != QMessageBox.StandardButton.Yes:
                return

        qemu_img = os.path.join(self.config['qemu_dir'], "qemu-img.exe")
        if not os.path.exists(qemu_img):
            QMessageBox.critical(self, "错误", f"找不到 qemu-img.exe:\n{qemu_img}")
            return

        self.log_text.append(f"正在创建 {disk_size}GB 虚拟磁盘...")
        self.status_bar.showMessage("正在创建虚拟磁盘...")

        try:
            cmd = [
                qemu_img,
                "create", "-f", "qcow2",
                "-o", "cluster_size=2M,lazy_refcounts=on",
                hdd_path,
                f"{disk_size}G"
            ]

            result = subprocess.run(cmd, capture_output=True, text=True, creationflags=subprocess.CREATE_NO_WINDOW)

            if result.returncode == 0:
                self.log_text.append(f"✅ 虚拟磁盘创建成功: {hdd_path}")
                QMessageBox.information(self, "成功", "虚拟磁盘创建成功！")
            else:
                self.log_text.append(f"❌ 创建失败: {result.stderr}")
                QMessageBox.critical(self, "错误", f"创建失败:\n{result.stderr}")
        except Exception as e:
            self.log_text.append(f"❌ 错误: {str(e)}")
            QMessageBox.critical(self, "错误", str(e))

        self.status_bar.showMessage("就绪")

    def get_qemu_img(self):
        """获取 qemu-img 路径"""
        qemu_img = os.path.join(self.config['qemu_dir'], "qemu-img.exe")
        if not os.path.exists(qemu_img):
            QMessageBox.critical(self, "错误", f"找不到 qemu-img.exe:\n{qemu_img}")
            return None
        return qemu_img

    def run_qemu_img(self, args):
        """运行 qemu-img 命令"""
        qemu_img = self.get_qemu_img()
        if not qemu_img:
            return None

        cmd = [qemu_img] + args
        try:
            result = subprocess.run(
                cmd, capture_output=True, text=True,
                creationflags=subprocess.CREATE_NO_WINDOW
            )
            return result
        except Exception as e:
            QMessageBox.critical(self, "错误", f"执行命令失败:\n{str(e)}")
            return None

    def browse_backup_path(self):
        """浏览备份保存路径"""
        # 确保默认备份目录存在
        default_backup_dir = ".\\disk\\backup"
        os.makedirs(default_backup_dir, exist_ok=True)

        # 生成默认备份文件名
        hdd_name = os.path.basename(self.config['hdd_path'])
        base_name, _ = os.path.splitext(hdd_name)
        default_name = f"{base_name}_backup_{self.get_timestamp()}.qcow2"
        default_path = os.path.join(default_backup_dir, default_name)

        file_path, _ = QFileDialog.getSaveFileName(
            self, "选择备份保存位置",
            self.backup_path_input.text() or default_path,
            "QCOW2 备份 (*.qcow2);;所有文件 (*.*)"
        )
        if file_path:
            self.backup_path_input.setText(file_path)

    def full_backup_disk(self):
        """完整备份磁盘"""
        hdd_path = self.config['hdd_path']
        backup_path = self.backup_path_input.text().strip()

        if not os.path.exists(hdd_path):
            QMessageBox.critical(self, "错误", "源磁盘文件不存在！")
            return

        if not backup_path:
            # 自动生成备份路径到默认备份目录
            backup_dir = ".\\disk\\backup"
            os.makedirs(backup_dir, exist_ok=True)
            hdd_name = os.path.basename(hdd_path)
            base, ext = os.path.splitext(hdd_name)
            backup_path = os.path.join(backup_dir, f"{base}_backup_{self.get_timestamp()}{ext}")
            self.backup_path_input.setText(backup_path)

        # 检查备份路径是否已存在
        if os.path.exists(backup_path):
            reply = QMessageBox.question(
                self, "确认覆盖",
                f"备份文件已存在:\n{backup_path}\n\n是否覆盖?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            if reply != QMessageBox.StandardButton.Yes:
                return

        # 获取 qemu-img 路径
        qemu_img = self.get_qemu_img()
        if not qemu_img:
            return

        self.log_text.append(f"开始完整备份...")
        self.log_text.append(f"源: {hdd_path}")
        self.log_text.append(f"目标: {backup_path}")

        # 显示文件大小信息
        source_size = os.path.getsize(hdd_path) / (1024 * 1024)

        # 创建进度对话框（使用 QProgressDialog）
        progress_dialog = QProgressDialog(
            f"正在备份磁盘...\n\n源文件大小: {source_size:.2f} MB\n目标: {os.path.basename(backup_path)}",
            "取消备份",
            0, 100, self
        )
        progress_dialog.setWindowTitle("备份进行中")
        progress_dialog.setWindowModality(Qt.WindowModality.WindowModal)
        progress_dialog.setMinimumDuration(0)  # 立即显示
        progress_dialog.setValue(0)
        progress_dialog.setAutoClose(False)
        progress_dialog.setAutoReset(False)

        # 创建备份线程
        self.backup_thread = BackupThread(qemu_img, hdd_path, backup_path, "full")

        # 连接信号
        def on_progress(msg):
            # 解析进度信息（qemu-img 会输出百分比）
            if "%" in msg:
                try:
                    # 提取百分比数字
                    percent_str = msg.split("%")[0].strip()
                    percent = int(float(percent_str))
                    progress_dialog.setValue(percent)
                    progress_dialog.setLabelText(
                        f"正在备份磁盘... {percent}%\n\n"
                        f"源文件大小: {source_size:.2f} MB\n"
                        f"目标: {os.path.basename(backup_path)}"
                    )
                except:
                    progress_dialog.setLabelText(f"正在备份磁盘...\n\n{msg}")
            else:
                progress_dialog.setLabelText(f"正在备份磁盘...\n\n{msg}")

        def on_finished(success, msg):
            progress_dialog.close()
            if success:
                self.log_text.append(f"✅ 完整备份成功: {backup_path}")
                # 显示备份文件大小
                if os.path.exists(backup_path):
                    size = os.path.getsize(backup_path)
                    size_mb = size / (1024 * 1024)
                    self.log_text.append(f"备份文件大小: {size_mb:.2f} MB")
                    # 计算压缩率
                    ratio = (1 - size_mb / source_size) * 100 if source_size > 0 else 0
                    QMessageBox.information(
                        self, "成功",
                        f"备份完成！\n\n保存位置:\n{backup_path}\n\n"
                        f"原文件: {source_size:.2f} MB\n"
                        f"备份后: {size_mb:.2f} MB\n"
                        f"压缩率: {ratio:.1f}%"
                    )
            else:
                self.log_text.append(f"❌ 备份失败: {msg}")
                QMessageBox.critical(self, "错误", f"备份失败:\n{msg}")
                # 清理失败的备份文件
                if os.path.exists(backup_path):
                    os.remove(backup_path)
            self.status_bar.showMessage("就绪")

        self.backup_thread.progress_signal.connect(on_progress)
        self.backup_thread.finished_signal.connect(on_finished)

        # 连接取消按钮
        progress_dialog.canceled.connect(self.backup_thread.stop)

        # 启动备份线程
        self.backup_thread.start()

        # 显示进度对话框
        progress_dialog.exec()

    def incremental_backup_disk(self):
        """增量备份磁盘（使用 backing_file）"""
        hdd_path = self.config['hdd_path']
        backup_path = self.backup_path_input.text().strip()

        if not os.path.exists(hdd_path):
            QMessageBox.critical(self, "错误", "源磁盘文件不存在！")
            return

        if not backup_path:
            # 自动生成备份路径到默认备份目录
            backup_dir = ".\\disk\\backup"
            os.makedirs(backup_dir, exist_ok=True)
            hdd_name = os.path.basename(hdd_path)
            base, ext = os.path.splitext(hdd_name)
            backup_path = os.path.join(backup_dir, f"{base}_incremental_{self.get_timestamp()}{ext}")
            self.backup_path_input.setText(backup_path)

        reply = QMessageBox.question(
            self, "增量备份",
            f"将创建增量备份:\n{backup_path}\n\n"
            "增量备份依赖于原磁盘文件，请确保原文件不会被移动或删除。\n"
            "是否继续?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply != QMessageBox.StandardButton.Yes:
            return

        # 获取 qemu-img 路径
        qemu_img = self.get_qemu_img()
        if not qemu_img:
            return

        self.log_text.append(f"开始增量备份...")
        self.log_text.append(f"源: {hdd_path}")
        self.log_text.append(f"目标: {backup_path}")

        # 显示文件大小信息
        source_size = os.path.getsize(hdd_path) / (1024 * 1024)

        # 创建进度对话框（使用 QProgressDialog）
        progress_dialog = QProgressDialog(
            f"正在创建增量备份...\n\n源文件大小: {source_size:.2f} MB\n目标: {os.path.basename(backup_path)}",
            "取消备份",
            0, 0, self  # 0-0 表示进度未知（忙碌状态）
        )
        progress_dialog.setWindowTitle("增量备份进行中")
        progress_dialog.setWindowModality(Qt.WindowModality.WindowModal)
        progress_dialog.setMinimumDuration(0)  # 立即显示
        progress_dialog.setValue(0)
        progress_dialog.setAutoClose(False)
        progress_dialog.setAutoReset(False)

        # 创建备份线程
        self.backup_thread = BackupThread(qemu_img, hdd_path, backup_path, "incremental")

        # 连接信号
        def on_progress(msg):
            progress_dialog.setLabelText(f"正在创建增量备份...\n\n{msg}")

        def on_finished(success, msg):
            progress_dialog.close()
            if success:
                self.log_text.append(f"✅ 增量备份成功: {backup_path}")
                # 显示备份文件大小
                if os.path.exists(backup_path):
                    size = os.path.getsize(backup_path)
                    size_kb = size / 1024
                    self.log_text.append(f"备份文件大小: {size_kb:.2f} KB (增量)")
                    QMessageBox.information(
                        self, "成功",
                        f"增量备份完成！\n\n保存位置:\n{backup_path}\n\n"
                        f"备份文件大小: {size_kb:.2f} KB\n\n"
                        "注意：此备份依赖于原磁盘文件，请勿删除原文件。"
                    )
            else:
                self.log_text.append(f"❌ 增量备份失败: {msg}")
                QMessageBox.critical(self, "错误", f"增量备份失败:\n{msg}")
                # 清理失败的备份文件
                if os.path.exists(backup_path):
                    os.remove(backup_path)
            self.status_bar.showMessage("就绪")

        self.backup_thread.progress_signal.connect(on_progress)
        self.backup_thread.finished_signal.connect(on_finished)

        # 连接取消按钮
        progress_dialog.canceled.connect(self.backup_thread.stop)

        # 启动备份线程
        self.backup_thread.start()

        # 显示进度对话框
        progress_dialog.exec()

    def refresh_disk_info(self):
        """刷新磁盘信息"""
        hdd_path = self.config['hdd_path']

        if not os.path.exists(hdd_path):
            self.disk_status_label.setText("不存在")
            self.disk_status_label.setStyleSheet("color: #f44336;")
            self.disk_virtual_size.setText("N/A")
            self.disk_actual_size.setText("N/A")
            return

        self.disk_status_label.setText("存在")
        self.disk_status_label.setStyleSheet("color: #4CAF50;")

        # 获取磁盘信息
        result = self.run_qemu_img(["info", hdd_path])
        if result and result.returncode == 0:
            output = result.stdout
            # 解析输出
            for line in output.split('\n'):
                if 'virtual size:' in line:
                    size = line.split('virtual size:')[1].strip()
                    self.disk_virtual_size.setText(size)
                elif 'disk size:' in line:
                    size = line.split('disk size:')[1].strip()
                    self.disk_actual_size.setText(size)

            self.log_text.append(f"磁盘信息:\n{output}")
        else:
            self.disk_virtual_size.setText("获取失败")
            self.disk_actual_size.setText("获取失败")

    def resize_disk(self):
        """扩容磁盘"""
        hdd_path = self.config['hdd_path']
        new_size = self.resize_spin.value()

        if not os.path.exists(hdd_path):
            QMessageBox.critical(self, "错误", "磁盘文件不存在！")
            return

        reply = QMessageBox.question(
            self, "确认扩容",
            f"将磁盘扩容到 {new_size}GB?\n\n注意：扩容后需要在虚拟机内扩展分区！",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply != QMessageBox.StandardButton.Yes:
            return

        self.log_text.append(f"正在扩容磁盘到 {new_size}GB...")
        result = self.run_qemu_img(["resize", hdd_path, f"{new_size}G"])

        if result and result.returncode == 0:
            self.log_text.append("✅ 磁盘扩容成功！")
            QMessageBox.information(self, "成功", "磁盘扩容成功！\n请在虚拟机内使用分区工具扩展分区。")
            self.refresh_disk_info()
        else:
            error = result.stderr if result else "未知错误"
            self.log_text.append(f"❌ 扩容失败: {error}")
            QMessageBox.critical(self, "错误", f"扩容失败:\n{error}")

    def compact_disk(self):
        """压缩磁盘（保存到新文件，文件名加入时间戳）"""
        hdd_path = self.config['hdd_path']

        if not os.path.exists(hdd_path):
            QMessageBox.critical(self, "错误", "磁盘文件不存在！")
            return

        # 构建输出路径：原目录 + 原文件名 + _compressed_时间戳.qcow2
        hdd_dir = os.path.dirname(hdd_path)
        hdd_name = os.path.basename(hdd_path)
        base_name, ext = os.path.splitext(hdd_name)
        timestamp = self.get_timestamp()
        output_path = os.path.join(hdd_dir, f"{base_name}_compressed_{timestamp}{ext}")

        reply = QMessageBox.question(
            self, "确认压缩",
            f"压缩磁盘可以减小实际占用空间，但可能需要较长时间。\n\n"
            f"输出文件:\n{output_path}\n\n"
            f"是否继续?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply != QMessageBox.StandardButton.Yes:
            return

        self.log_text.append("正在压缩磁盘...")
        self.log_text.append(f"源文件: {hdd_path}")
        self.log_text.append(f"输出文件: {output_path}")
        self.status_bar.showMessage("正在压缩磁盘...")

        result = self.run_qemu_img(["convert", "-O", "qcow2", "-c", hdd_path, output_path])

        if result and result.returncode == 0:
            self.log_text.append(f"✅ 磁盘压缩成功: {output_path}")

            # 显示压缩前后大小
            if os.path.exists(hdd_path) and os.path.exists(output_path):
                original_size = os.path.getsize(hdd_path) / (1024 * 1024)
                compressed_size = os.path.getsize(output_path) / (1024 * 1024)
                ratio = (1 - compressed_size / original_size) * 100 if original_size > 0 else 0
                self.log_text.append(f"原文件大小: {original_size:.2f} MB")
                self.log_text.append(f"压缩后大小: {compressed_size:.2f} MB")
                self.log_text.append(f"压缩率: {ratio:.1f}%")

            QMessageBox.information(
                self, "成功",
                f"磁盘压缩成功！\n\n"
                f"保存位置:\n{output_path}\n\n"
                f"压缩率: {ratio:.1f}%"
            )
            self.refresh_disk_info()
        else:
            error = result.stderr if result else "未知错误"
            self.log_text.append(f"❌ 压缩失败: {error}")
            QMessageBox.critical(self, "错误", f"压缩失败:\n{error}")
            # 清理临时文件
            if os.path.exists(output_path):
                os.remove(output_path)

        self.status_bar.showMessage("就绪")

    def convert_disk(self):
        """转换磁盘格式"""
        hdd_path = self.config['hdd_path']
        target_format = self.convert_format.currentText()

        if not os.path.exists(hdd_path):
            QMessageBox.critical(self, "错误", "磁盘文件不存在！")
            return

        # 构建输出路径
        base, _ = os.path.splitext(hdd_path)
        output_path = f"{base}.{target_format}"

        reply = QMessageBox.question(
            self, "确认转换",
            f"将磁盘转换为 {target_format} 格式?\n\n输出文件:\n{output_path}",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply != QMessageBox.StandardButton.Yes:
            return

        self.log_text.append(f"正在转换为 {target_format}...")
        result = self.run_qemu_img(["convert", "-O", target_format, hdd_path, output_path])

        if result and result.returncode == 0:
            self.log_text.append(f"✅ 转换成功: {output_path}")
            QMessageBox.information(self, "成功", f"转换成功！\n输出文件:\n{output_path}")
        else:
            error = result.stderr if result else "未知错误"
            self.log_text.append(f"❌ 转换失败: {error}")
            QMessageBox.critical(self, "错误", f"转换失败:\n{error}")

    def build_command_for_test(self, temp_disk_path):
        """构建测试启动的 QEMU 命令（使用临时磁盘）"""
        qemu_exe = os.path.join(self.config['qemu_dir'], "qemu-system-loongarch64.exe")
        bios_path = os.path.join(self.config['qemu_dir'], "share", "edk2-loongarch64-code.fd")

        cmd = [
            qemu_exe,
            "-machine", "virt",
            "-accel", "tcg,thread=multi",
            "-cpu", "max",
            "-smp", str(self.config['cpu_cores']),
            "-m", str(self.config['memory']),
            "-rtc", "base=localtime",
            "-bios", bios_path,
            "-vga", "none",
            "-device", "virtio-gpu-pci",
            "-spice", f"port={self.config['spice_port']},addr=127.0.0.1,disable-ticketing=on",
            "-device", "qemu-xhci",
            "-device", "usb-kbd",
            "-device", "usb-tablet",
            "-hda", temp_disk_path,  # 使用临时磁盘
            "-boot", "c",
            "-netdev", f"user,id=net0,hostfwd=tcp::{self.config['rdp_port']}-:3389",
            "-device", "e1000,netdev=net0",
            "-device", "intel-hda",
            "-device", "hda-output",
            "-device", "virtio-serial-pci",
            "-device", "virtserialport,chardev=spicechannel0,name=com.redhat.spice.0",
            "-chardev", "spicevmc,id=spicechannel0,name=vdagent"
        ]

        return cmd

    def build_command_for_snapshot(self, snapshot_path):
        """构建从快照启动的 QEMU 命令（使用外部快照文件）"""
        qemu_exe = os.path.join(self.config['qemu_dir'], "qemu-system-loongarch64.exe")
        bios_path = os.path.join(self.config['qemu_dir'], "share", "edk2-loongarch64-code.fd")

        cmd = [
            qemu_exe,
            "-machine", "virt",
            "-accel", "tcg,thread=multi",
            "-cpu", "max",
            "-smp", str(self.config['cpu_cores']),
            "-m", str(self.config['memory']),
            "-rtc", "base=localtime",
            "-bios", bios_path,
            "-vga", "none",
            "-device", "virtio-gpu-pci",
            "-spice", f"port={self.config['spice_port']},addr=127.0.0.1,disable-ticketing=on",
            "-device", "qemu-xhci",
            "-device", "usb-kbd",
            "-device", "usb-tablet",
            "-hda", snapshot_path,  # 使用快照文件作为磁盘
            "-boot", "c",
            "-netdev", f"user,id=net0,hostfwd=tcp::{self.config['rdp_port']}-:3389",
            "-device", "e1000,netdev=net0",
            "-device", "intel-hda",
            "-device", "hda-output",
            "-device", "virtio-serial-pci",
            "-device", "virtserialport,chardev=spicechannel0,name=com.redhat.spice.0",
            "-chardev", "spicevmc,id=spicechannel0,name=vdagent"
        ]

        return cmd

    def browse_snapshot_dir(self):
        """浏览快照保存目录"""
        dir_path = QFileDialog.getExistingDirectory(
            self, "选择快照保存目录",
            self.snapshot_dir_input.text() or ".\\disk\\snapshot"
        )
        if dir_path:
            self.snapshot_dir_input.setText(dir_path)

    def save_snapshot_dir(self):
        """保存快照目录设置"""
        snapshot_dir = self.snapshot_dir_input.text().strip()
        if not snapshot_dir:
            snapshot_dir = ".\\disk\\snapshot"

        # 确保目录存在
        try:
            os.makedirs(snapshot_dir, exist_ok=True)
        except Exception as e:
            QMessageBox.warning(self, "警告", f"创建目录失败: {e}")
            return

        self.config['snapshot_dir'] = snapshot_dir
        self.save_config()
        QMessageBox.information(self, "成功", f"快照保存路径已设置:\n{snapshot_dir}")

    def check_disk(self):
        """检查磁盘"""
        hdd_path = self.config['hdd_path']

        if not os.path.exists(hdd_path):
            QMessageBox.critical(self, "错误", "磁盘文件不存在！")
            return

        self.log_text.append("正在检查磁盘...")
        result = self.run_qemu_img(["check", hdd_path])

        if result:
            self.log_text.append(f"检查结果:\n{result.stdout}")
            if result.stderr:
                self.log_text.append(f"错误输出:\n{result.stderr}")
            QMessageBox.information(self, "检查完成", "磁盘检查完成，请查看日志。")

    def repair_disk(self):
        """修复磁盘"""
        hdd_path = self.config['hdd_path']

        if not os.path.exists(hdd_path):
            QMessageBox.critical(self, "错误", "磁盘文件不存在！")
            return

        reply = QMessageBox.warning(
            self, "确认修复",
            "修复磁盘可能会修改磁盘文件，建议先备份！\n\n是否继续?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply != QMessageBox.StandardButton.Yes:
            return

        self.log_text.append("正在修复磁盘...")
        result = self.run_qemu_img(["check", "-r", "all", hdd_path])

        if result:
            self.log_text.append(f"修复结果:\n{result.stdout}")
            if result.stderr:
                self.log_text.append(f"错误输出:\n{result.stderr}")
            QMessageBox.information(self, "修复完成", "磁盘修复完成，请查看日志。")

    def delete_disk(self):
        """删除磁盘"""
        hdd_path = self.config['hdd_path']

        if not os.path.exists(hdd_path):
            QMessageBox.critical(self, "错误", "磁盘文件不存在！")
            return

        reply = QMessageBox.critical(
            self, "⚠️ 确认删除",
            f"确定要删除磁盘文件吗？\n\n{hdd_path}\n\n此操作不可恢复！",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply != QMessageBox.StandardButton.Yes:
            return

        try:
            os.remove(hdd_path)
            self.log_text.append(f"✅ 磁盘已删除: {hdd_path}")
            QMessageBox.information(self, "成功", "磁盘已删除！")
            self.refresh_disk_info()
        except Exception as e:
            self.log_text.append(f"❌ 删除失败: {str(e)}")
            QMessageBox.critical(self, "错误", str(e))

    def create_snapshot(self):
        """创建快照（外部快照保存到指定目录）"""
        hdd_path = self.config['hdd_path']
        name = self.snapshot_name.text().strip()
        desc = self.snapshot_desc.text().strip()

        if not name:
            QMessageBox.warning(self, "警告", "请输入快照名称！")
            return

        if not os.path.exists(hdd_path):
            QMessageBox.critical(self, "错误", "磁盘文件不存在！")
            return

        # 获取快照保存目录
        snapshot_dir = self.config.get('snapshot_dir', '.\\disk\\snapshot')

        # 确保目录存在
        try:
            os.makedirs(snapshot_dir, exist_ok=True)
        except Exception as e:
            QMessageBox.critical(self, "错误", f"创建快照目录失败:\n{str(e)}")
            return

        # 构建快照文件路径
        snapshot_filename = f"{name}.qcow2"
        snapshot_path = os.path.join(snapshot_dir, snapshot_filename)

        # 如果文件已存在，添加时间戳
        if os.path.exists(snapshot_path):
            snapshot_filename = f"{name}_{self.get_timestamp()}.qcow2"
            snapshot_path = os.path.join(snapshot_dir, snapshot_filename)

        self.log_text.append(f"正在创建快照: {name}...")
        self.log_text.append(f"保存位置: {snapshot_path}")

        # 创建外部快照（使用 backing_file）
        result = self.run_qemu_img([
            "create", "-f", "qcow2",
            "-b", hdd_path,
            "-F", "qcow2",
            snapshot_path
        ])

        if result and result.returncode == 0:
            # 保存描述信息到同名文件
            if desc:
                try:
                    desc_path = os.path.join(snapshot_dir, f"{name}.txt")
                    with open(desc_path, 'w', encoding='utf-8') as f:
                        f.write(f"快照名称: {name}\n")
                        f.write(f"描述: {desc}\n")
                        f.write(f"创建时间: {self.get_timestamp()}\n")
                        f.write(f"原磁盘: {hdd_path}\n")
                except:
                    pass

            self.log_text.append(f"✅ 快照创建成功: {snapshot_path}")
            QMessageBox.information(
                self, "成功",
                f"快照 '{name}' 创建成功！\n\n保存位置:\n{snapshot_path}\n\n"
                "注意：此快照依赖于原磁盘文件，请勿删除原文件。"
            )
            self.snapshot_name.clear()
            self.snapshot_desc.clear()
            self.list_snapshots()
        else:
            error = result.stderr if result else "未知错误"
            self.log_text.append(f"❌ 创建失败: {error}")
            QMessageBox.critical(self, "错误", f"创建失败:\n{error}")

    def list_snapshots(self):
        """列出快照（外部快照文件）"""
        hdd_path = self.config['hdd_path']
        snapshot_dir = self.config.get('snapshot_dir', '.\\disk\\snapshot')

        if not os.path.exists(hdd_path):
            self.snapshot_list.setText("磁盘文件不存在")
            return

        # 获取外部快照文件列表
        snapshot_files = []
        if os.path.exists(snapshot_dir):
            for file in os.listdir(snapshot_dir):
                if file.endswith('.qcow2'):
                    file_path = os.path.join(snapshot_dir, file)
                    try:
                        stat = os.stat(file_path)
                        size_mb = stat.st_size / (1024 * 1024)
                        mtime = stat.st_mtime
                        from datetime import datetime
                        time_str = datetime.fromtimestamp(mtime).strftime('%Y-%m-%d %H:%M:%S')
                        name = file[:-6]  # 去掉 .qcow2

                        # 检查是否有描述文件
                        desc = ""
                        desc_path = os.path.join(snapshot_dir, f"{name}.txt")
                        if os.path.exists(desc_path):
                            try:
                                with open(desc_path, 'r', encoding='utf-8') as f:
                                    for line in f:
                                        if line.startswith('描述:'):
                                            desc = line[3:].strip()
                                            break
                            except:
                                pass

                        snapshot_files.append({
                            'name': name,
                            'size': size_mb,
                            'time': time_str,
                            'desc': desc
                        })
                    except:
                        pass

        if snapshot_files:
            # 按时间排序
            snapshot_files.sort(key=lambda x: x['time'], reverse=True)

            output = f"快照保存目录: {snapshot_dir}\n"
            output += "=" * 60 + "\n"
            output += f"{'名称':<20} {'大小(MB)':<12} {'创建时间':<20} {'描述'}\n"
            output += "-" * 60 + "\n"

            for snap in snapshot_files:
                desc_short = snap['desc'][:15] + '...' if len(snap['desc']) > 15 else snap['desc']
                output += f"{snap['name']:<20} {snap['size']:<12.2f} {snap['time']:<20} {desc_short}\n"

            output += "=" * 60 + "\n"
            output += f"共 {len(snapshot_files)} 个外部快照文件\n"

            self.snapshot_list.setText(output)
            self.log_text.append(f"快照列表:\n{output}")
        else:
            self.snapshot_list.setText(f"暂无外部快照文件\n快照保存目录: {snapshot_dir}")
            self.log_text.append(f"快照目录 {snapshot_dir} 中没有找到快照文件")

    def restore_snapshot(self):
        """恢复快照（从外部快照文件恢复）"""
        hdd_path = self.config['hdd_path']
        name = self.snapshot_name.text().strip()
        snapshot_dir = self.config.get('snapshot_dir', '.\\disk\\snapshot')

        if not name:
            QMessageBox.warning(self, "警告", "请输入要恢复的快照名称！")
            return

        if not os.path.exists(hdd_path):
            QMessageBox.critical(self, "错误", "磁盘文件不存在！")
            return

        # 构建快照文件路径
        snapshot_path = os.path.join(snapshot_dir, f"{name}.qcow2")

        if not os.path.exists(snapshot_path):
            QMessageBox.critical(
                self, "错误",
                f"找不到快照文件:\n{snapshot_path}\n\n"
                "请确保快照名称正确，或点击'刷新列表'查看可用快照。"
            )
            return

        reply = QMessageBox.warning(
            self, "确认恢复",
            f"将从外部快照 '{name}' 恢复?\n\n"
            f"快照文件: {snapshot_path}\n\n"
            "当前磁盘状态将被覆盖！\n\n"
            "建议先备份当前磁盘！",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply != QMessageBox.StandardButton.Yes:
            return

        self.log_text.append(f"正在从外部快照恢复: {name}...")
        self.log_text.append(f"快照文件: {snapshot_path}")
        self.status_bar.showMessage("正在恢复快照...")

        # 将外部快照内容合并回原磁盘
        # 方法：使用 qemu-img convert 将快照转换为原磁盘
        result = self.run_qemu_img([
            "convert", "-O", "qcow2",
            snapshot_path, hdd_path
        ])

        if result and result.returncode == 0:
            self.log_text.append(f"✅ 已从快照恢复: {name}")
            QMessageBox.information(
                self, "成功",
                f"已从快照 '{name}' 恢复！\n\n"
                f"原磁盘已覆盖为快照内容。"
            )
        else:
            error = result.stderr if result else "未知错误"
            self.log_text.append(f"❌ 恢复失败: {error}")
            QMessageBox.critical(self, "错误", f"恢复失败:\n{error}")

        self.status_bar.showMessage("就绪")

    def delete_snapshot(self):
        """删除快照（删除外部快照文件）"""
        name = self.snapshot_name.text().strip()
        snapshot_dir = self.config.get('snapshot_dir', '.\\disk\\snapshot')

        if not name:
            QMessageBox.warning(self, "警告", "请输入要删除的快照名称！")
            return

        # 构建快照文件路径
        snapshot_path = os.path.join(snapshot_dir, f"{name}.qcow2")
        desc_path = os.path.join(snapshot_dir, f"{name}.txt")

        if not os.path.exists(snapshot_path):
            QMessageBox.critical(
                self, "错误",
                f"找不到快照文件:\n{snapshot_path}"
            )
            return

        reply = QMessageBox.question(
            self, "确认删除",
            f"确定要删除快照 '{name}'?\n\n"
            f"文件: {snapshot_path}\n\n"
            "此操作不可恢复！",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply != QMessageBox.StandardButton.Yes:
            return

        self.log_text.append(f"正在删除快照: {name}...")

        try:
            # 删除快照文件
            os.remove(snapshot_path)

            # 删除描述文件（如果存在）
            if os.path.exists(desc_path):
                os.remove(desc_path)

            self.log_text.append(f"✅ 快照已删除: {name}")
            QMessageBox.information(self, "成功", f"快照 '{name}' 已删除！")
            self.list_snapshots()
        except Exception as e:
            self.log_text.append(f"❌ 删除失败: {str(e)}")
            QMessageBox.critical(self, "错误", f"删除失败:\n{str(e)}")

    def build_command(self):
        """构建 QEMU 启动命令"""
        qemu_exe = os.path.join(self.config['qemu_dir'], "qemu-system-loongarch64.exe")
        bios_path = os.path.join(self.config['qemu_dir'], "share", "edk2-loongarch64-code.fd")

        cmd = [
            qemu_exe,
            "-machine", "virt",
            "-accel", "tcg,thread=multi",
            "-cpu", "max",
            "-smp", str(self.config['cpu_cores']),
            "-m", str(self.config['memory']),
            "-rtc", "base=localtime",
            "-bios", bios_path,
            "-vga", "none",
            "-device", "virtio-gpu-pci",
            "-spice", f"port={self.config['spice_port']},addr=127.0.0.1,disable-ticketing=on",
            "-device", "qemu-xhci",
            "-device", "usb-kbd",
            "-device", "usb-tablet",
            "-hda", self.config['hdd_path'],
            "-boot", "c",
            "-netdev", f"user,id=net0,hostfwd=tcp::{self.config['rdp_port']}-:3389",
            "-device", "e1000,netdev=net0",
            "-device", "intel-hda",
            "-device", "hda-output",
            "-device", "virtio-serial-pci",
            "-device", "virtserialport,chardev=spicechannel0,name=com.redhat.spice.0",
            "-chardev", "spicevmc,id=spicechannel0,name=vdagent"
        ]

        return cmd

    def start_vm(self):
        """启动虚拟机"""
        # 检查必要文件
        qemu_exe = os.path.join(self.config['qemu_dir'], "qemu-system-loongarch64.exe")
        if not os.path.exists(qemu_exe):
            QMessageBox.critical(self, "错误", f"找不到 QEMU:\n{qemu_exe}")
            return

        if not os.path.exists(self.config['hdd_path']):
            reply = QMessageBox.question(
                self, "磁盘不存在",
                f"虚拟磁盘不存在:\n{self.config['hdd_path']}\n\n是否先创建磁盘?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No | QMessageBox.StandardButton.Cancel
            )
            if reply == QMessageBox.StandardButton.Yes:
                self.create_disk()
                return
            elif reply == QMessageBox.StandardButton.Cancel:
                return

        cmd = self.build_command()
        self.log_text.append("=" * 50)
        self.log_text.append("🚀 启动虚拟机...")
        self.log_text.append(f"命令: {' '.join(cmd)}")
        self.log_text.append("=" * 50)

        self.vm_runner = VMRunner(cmd)
        self.vm_runner.output_signal.connect(self.on_vm_output)
        self.vm_runner.finished_signal.connect(self.on_vm_finished)
        self.vm_runner.start()

        self.start_btn.setEnabled(False)
        self.stop_btn.setEnabled(True)
        self.status_text.setText("状态: 运行中")
        self.status_text.setStyleSheet("font-size: 16px; color: #4CAF50;")
        self.status_indicator.setText("● 运行中")
        self.status_indicator.setStyleSheet("color: #4CAF50; font-weight: bold;")
        self.status_bar.showMessage("虚拟机运行中...")

    def stop_vm(self):
        """停止虚拟机"""
        if self.vm_runner:
            self.log_text.append("⏹ 正在停止虚拟机...")
            self.vm_runner.stop()
            self.vm_runner = None

        self.start_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)
        self.status_text.setText("状态: 停止")
        self.status_text.setStyleSheet("font-size: 16px; color: #f44336;")
        self.status_indicator.setText("● 停止")
        self.status_indicator.setStyleSheet("color: #f44336; font-weight: bold;")
        self.status_bar.showMessage("虚拟机已停止")

    def on_vm_output(self, text):
        """处理虚拟机输出"""
        self.log_text.append(text)
        # 自动滚动到底部
        scrollbar = self.log_text.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())

    def on_vm_finished(self, return_code):
        """虚拟机结束回调"""
        self.log_text.append(f"虚拟机已退出，返回码: {return_code}")

        # 如果是测试模式，提示是否保存快照
        if getattr(self, 'test_mode', False):
            self.test_mode = False
            self.ask_save_test_snapshot()

        # 如果是从快照启动模式，提示是否保存更改
        if getattr(self, 'snapshot_start_mode', False):
            self.snapshot_start_mode = False
            self.ask_save_snapshot_changes()

        self.stop_vm()

    def start_test_vm(self):
        """测试启动虚拟机（临时运行，使用临时磁盘文件）"""
        # 检查必要文件
        qemu_exe = os.path.join(self.config['qemu_dir'], "qemu-system-loongarch64.exe")
        if not os.path.exists(qemu_exe):
            QMessageBox.critical(self, "错误", f"找不到 QEMU:\n{qemu_exe}")
            return

        hdd_path = self.config['hdd_path']
        if not os.path.exists(hdd_path):
            QMessageBox.critical(self, "错误", "虚拟磁盘不存在！")
            return

        # 创建临时目录
        temp_dir = ".\\disk\\temp"
        try:
            os.makedirs(temp_dir, exist_ok=True)
        except Exception as e:
            QMessageBox.critical(self, "错误", f"创建临时目录失败:\n{str(e)}")
            return

        # 生成临时磁盘文件路径
        timestamp = self.get_timestamp()
        temp_disk_name = f"temp_{timestamp}.qcow2"
        temp_disk_path = os.path.join(temp_dir, temp_disk_name)

        self.log_text.append(f"正在创建临时磁盘文件: {temp_disk_path}...")
        self.status_bar.showMessage("正在创建临时磁盘...")

        # 创建基于原磁盘的外部快照（临时磁盘）
        result = self.run_qemu_img([
            "create", "-f", "qcow2",
            "-b", hdd_path,
            "-F", "qcow2",
            temp_disk_path
        ])

        if not result or result.returncode != 0:
            error = result.stderr if result else "未知错误"
            self.log_text.append(f"❌ 创建临时磁盘失败: {error}")
            QMessageBox.critical(self, "错误", f"创建临时磁盘失败:\n{error}")
            self.status_bar.showMessage("就绪")
            return

        self.log_text.append(f"✅ 临时磁盘创建成功: {temp_disk_path}")

        # 保存临时磁盘路径和原磁盘路径
        self.test_temp_disk = temp_disk_path
        self.test_original_disk = hdd_path

        # 标记为测试模式
        self.test_mode = True

        # 构建命令，使用临时磁盘
        cmd = self.build_command_for_test(temp_disk_path)
        self.log_text.append("=" * 50)
        self.log_text.append("🧪 测试启动虚拟机（临时模式）...")
        self.log_text.append(f"临时磁盘: {temp_disk_path}")
        self.log_text.append(f"命令: {' '.join(cmd)}")
        self.log_text.append("=" * 50)

        self.vm_runner = VMRunner(cmd)
        self.vm_runner.output_signal.connect(self.on_vm_output)
        self.vm_runner.finished_signal.connect(self.on_vm_finished)
        self.vm_runner.start()

        self.start_btn.setEnabled(False)
        self.test_start_btn.setEnabled(False)
        self.stop_btn.setEnabled(True)
        self.status_text.setText("状态: 测试运行中")
        self.status_text.setStyleSheet("font-size: 16px; color: #607D8B;")
        self.status_indicator.setText("● 测试模式")
        self.status_indicator.setStyleSheet("color: #607D8B; font-weight: bold;")
        self.status_bar.showMessage("虚拟机测试运行中...")

    def ask_save_test_snapshot(self):
        """询问是否保存测试快照（处理临时磁盘）"""
        temp_disk = getattr(self, 'test_temp_disk', None)

        if not temp_disk or not os.path.exists(temp_disk):
            self.log_text.append("⚠️ 临时磁盘文件不存在")
            self.cleanup_test_temp()
            return

        msg = QMessageBox(self)
        msg.setWindowTitle("测试完成")
        msg.setText("测试运行已结束，是否保存更改？")
        msg.setInformativeText(
            "• 保存快照 — 将临时磁盘保存为快照\n"
            "• 放弃更改 — 删除临时磁盘\n"
            "• 保留更改 — 将临时磁盘合并回原磁盘"
        )

        save_btn = msg.addButton("💾 保存快照", QMessageBox.ButtonRole.AcceptRole)
        discard_btn = msg.addButton("🗑️ 放弃更改", QMessageBox.ButtonRole.DestructiveRole)
        keep_btn = msg.addButton("✓ 保留更改", QMessageBox.ButtonRole.RejectRole)

        msg.exec()

        if msg.clickedButton() == save_btn:
            self.save_test_snapshot_from_temp(temp_disk)
            # 异步操作，线程完成后会调用 cleanup_test_temp
        elif msg.clickedButton() == discard_btn:
            self.discard_test_temp(temp_disk)
            self.cleanup_test_temp()
        else:
            self.keep_test_changes(temp_disk)
            # 异步操作，线程完成后会调用 cleanup_test_temp

    def save_test_snapshot_from_temp(self, temp_disk):
        """将临时磁盘保存为快照（带进度条）"""
        snapshot_dir = self.config.get('snapshot_dir', '.\\disk\\snapshot')

        # 确保目录存在
        try:
            os.makedirs(snapshot_dir, exist_ok=True)
        except Exception as e:
            QMessageBox.critical(self, "错误", f"创建快照目录失败: {e}")
            return

        name, ok = QInputDialog.getText(
            self, "保存快照",
            "输入快照名称:",
            QLineEdit.EchoMode.Normal,
            f"test_{self.get_timestamp()}"
        )

        if ok and name:
            snapshot_path = os.path.join(snapshot_dir, f"{name}.qcow2")
            self._save_snapshot_with_progress(temp_disk, snapshot_path, name)

    def _save_snapshot_with_progress(self, temp_disk, snapshot_path, name):
        """带进度条保存快照"""
        qemu_img = os.path.join(self.config['qemu_dir'], "qemu-img.exe")
        if not os.path.exists(qemu_img):
            QMessageBox.critical(self, "错误", f"找不到 qemu-img:\n{qemu_img}")
            return

        # 获取源文件大小
        source_size = os.path.getsize(temp_disk) / (1024 * 1024)

        # 创建进度对话框
        progress_dialog = QProgressDialog(
            f"正在保存快照...\n\n源文件大小: {source_size:.2f} MB\n目标: {os.path.basename(snapshot_path)}",
            "取消",
            0, 100, self
        )
        progress_dialog.setWindowTitle("保存快照中")
        progress_dialog.setWindowModality(Qt.WindowModality.WindowModal)
        progress_dialog.setMinimumDuration(0)
        progress_dialog.setValue(0)
        progress_dialog.setAutoClose(False)
        progress_dialog.setAutoReset(False)

        # 创建备份线程（复用 BackupThread）
        self.backup_thread = BackupThread(qemu_img, temp_disk, snapshot_path, "full")

        # 连接信号
        def on_progress(msg):
            if "%" in msg:
                try:
                    percent_str = msg.split("%")[0].strip()
                    percent = int(float(percent_str))
                    progress_dialog.setValue(percent)
                    progress_dialog.setLabelText(
                        f"正在保存快照... {percent}%\n\n"
                        f"源文件大小: {source_size:.2f} MB\n"
                        f"目标: {os.path.basename(snapshot_path)}"
                    )
                except:
                    progress_dialog.setLabelText(f"正在保存快照...\n\n{msg}")
            else:
                progress_dialog.setLabelText(f"正在保存快照...\n\n{msg}")

        def on_finished(success, msg):
            progress_dialog.close()
            if success:
                self.log_text.append(f"测试快照已保存: {snapshot_path}")
                QMessageBox.information(self, "成功", f"快照 '{name}' 保存成功！")
            else:
                self.log_text.append(f"保存快照失败: {msg}")
                QMessageBox.critical(self, "错误", f"保存失败:\n{msg}")
            # 清理临时变量
            self.cleanup_test_temp()

        self.backup_thread.progress_signal.connect(on_progress)
        self.backup_thread.finished_signal.connect(on_finished)

        # 启动线程
        self.backup_thread.start()

    def discard_test_temp(self, temp_disk):
        """放弃临时磁盘"""
        try:
            os.remove(temp_disk)
            self.log_text.append(f"🗑️ 临时磁盘已删除: {temp_disk}")
        except Exception as e:
            self.log_text.append(f"⚠️ 删除临时磁盘失败: {str(e)}")

    def keep_test_changes(self, temp_disk):
        """将临时磁盘更改合并回原磁盘（带进度条）"""
        original_disk = getattr(self, 'test_original_disk', None)
        if not original_disk:
            QMessageBox.critical(self, "错误", "找不到原磁盘路径！")
            return

        reply = QMessageBox.warning(
            self, "确认合并",
            "将临时磁盘的更改合并回原磁盘?\n\n"
            "原磁盘将被覆盖！",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply != QMessageBox.StandardButton.Yes:
            return

        self._merge_with_progress(temp_disk, original_disk)

    def _merge_with_progress(self, temp_disk, original_disk):
        """带进度条合并磁盘"""
        qemu_img = os.path.join(self.config['qemu_dir'], "qemu-img.exe")
        if not os.path.exists(qemu_img):
            QMessageBox.critical(self, "错误", f"找不到 qemu-img:\n{qemu_img}")
            return

        # 获取源文件大小
        source_size = os.path.getsize(temp_disk) / (1024 * 1024)

        # 创建进度对话框
        progress_dialog = QProgressDialog(
            f"正在合并更改到原磁盘...\n\n源文件大小: {source_size:.2f} MB\n目标: {os.path.basename(original_disk)}",
            "取消",
            0, 100, self
        )
        progress_dialog.setWindowTitle("合并中")
        progress_dialog.setWindowModality(Qt.WindowModality.WindowModal)
        progress_dialog.setMinimumDuration(0)
        progress_dialog.setValue(0)
        progress_dialog.setAutoClose(False)
        progress_dialog.setAutoReset(False)

        # 创建临时目标文件
        temp_target = original_disk + ".merging"

        # 创建备份线程
        self.backup_thread = BackupThread(qemu_img, temp_disk, temp_target, "full")

        # 连接信号
        def on_progress(msg):
            if "%" in msg:
                try:
                    percent_str = msg.split("%")[0].strip()
                    percent = int(float(percent_str))
                    progress_dialog.setValue(percent)
                    progress_dialog.setLabelText(
                        f"正在合并更改... {percent}%\n\n"
                        f"源文件大小: {source_size:.2f} MB\n"
                        f"目标: {os.path.basename(original_disk)}"
                    )
                except:
                    progress_dialog.setLabelText(f"正在合并更改...\n\n{msg}")
            else:
                progress_dialog.setLabelText(f"正在合并更改...\n\n{msg}")

        def on_finished(success, msg):
            progress_dialog.close()
            if success:
                # 替换原磁盘
                try:
                    if os.path.exists(original_disk):
                        os.remove(original_disk)
                    os.rename(temp_target, original_disk)
                    self.log_text.append("更改已合并到原磁盘")
                    QMessageBox.information(self, "成功", "更改已保留到原磁盘！")
                except Exception as e:
                    self.log_text.append(f"替换原磁盘失败: {str(e)}")
                    QMessageBox.critical(self, "错误", f"替换失败:\n{str(e)}")
            else:
                self.log_text.append(f"合并失败: {msg}")
                QMessageBox.critical(self, "错误", f"合并失败:\n{msg}")
                # 清理临时文件
                try:
                    if os.path.exists(temp_target):
                        os.remove(temp_target)
                except:
                    pass
            # 删除临时磁盘
            try:
                os.remove(temp_disk)
            except:
                pass
            # 清理临时变量
            self.cleanup_test_temp()

        self.backup_thread.progress_signal.connect(on_progress)
        self.backup_thread.finished_signal.connect(on_finished)

        # 启动线程
        self.backup_thread.start()

    def cleanup_test_temp(self):
        """清理测试临时变量"""
        self.test_temp_disk = None
        self.test_original_disk = None
        self.test_start_btn.setEnabled(True)

    def refresh_snapshot_list(self):
        """刷新快照列表到下拉框（从外部快照文件目录）"""
        hdd_path = self.config['hdd_path']
        snapshot_dir = self.config.get('snapshot_dir', '.\\disk\\snapshot')

        if not os.path.exists(hdd_path):
            self.snapshot_combo.clear()
            self.snapshot_combo.addItem("磁盘文件不存在")
            return

        self.snapshot_combo.clear()

        # 从外部快照目录获取快照文件列表
        snapshots = []
        if os.path.exists(snapshot_dir):
            for file in sorted(os.listdir(snapshot_dir)):
                if file.endswith('.qcow2'):
                    # 去掉 .qcow2 后缀作为快照名称
                    snapshot_name = file[:-6]
                    snapshots.append(snapshot_name)

        if snapshots:
            self.snapshot_combo.addItems(snapshots)
            self.log_text.append(f"✅ 已加载 {len(snapshots)} 个快照")
        else:
            self.snapshot_combo.addItem("暂无快照")
            self.log_text.append(f"ℹ️ 快照目录 {snapshot_dir} 中没有找到快照文件")

    def start_from_snapshot(self):
        """从选定的快照启动虚拟机（使用外部快照文件）"""
        snapshot_name = self.snapshot_combo.currentText()

        if not snapshot_name or snapshot_name in ["暂无快照", "获取失败", "磁盘文件不存在", "点击刷新加载快照列表..."]:
            QMessageBox.warning(self, "警告", "请先选择一个有效的快照！")
            return

        # 检查必要文件
        qemu_exe = os.path.join(self.config['qemu_dir'], "qemu-system-loongarch64.exe")
        if not os.path.exists(qemu_exe):
            QMessageBox.critical(self, "错误", f"找不到 QEMU:\n{qemu_exe}")
            return

        # 获取快照文件路径
        snapshot_dir = self.config.get('snapshot_dir', '.\\disk\\snapshot')
        snapshot_path = os.path.join(snapshot_dir, f"{snapshot_name}.qcow2")

        if not os.path.exists(snapshot_path):
            QMessageBox.critical(self, "错误", f"找不到快照文件:\n{snapshot_path}")
            return

        # 确认启动
        reply = QMessageBox.question(
            self, "从快照启动",
            f"将从快照 '{snapshot_name}' 启动虚拟机。\n\n"
            f"快照文件: {snapshot_path}\n\n"
            "注意：启动后如果保存更改，会影响当前磁盘状态。",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if reply != QMessageBox.StandardButton.Yes:
            return

        self.log_text.append(f"📸 从快照 '{snapshot_name}' 启动虚拟机...")
        self.log_text.append(f"快照文件: {snapshot_path}")

        # 标记为从快照启动模式
        self.snapshot_start_mode = True
        self.started_from_snapshot = snapshot_name
        self.snapshot_file_path = snapshot_path

        # 启动虚拟机（使用快照文件作为磁盘）
        cmd = self.build_command_for_snapshot(snapshot_path)
        self.log_text.append("=" * 50)
        self.log_text.append(f"命令: {' '.join(cmd)}")
        self.log_text.append("=" * 50)

        self.vm_runner = VMRunner(cmd)
        self.vm_runner.output_signal.connect(self.on_vm_output)
        self.vm_runner.finished_signal.connect(self.on_vm_finished)
        self.vm_runner.start()

        self.start_btn.setEnabled(False)
        self.test_start_btn.setEnabled(False)
        self.snapshot_start_btn.setEnabled(False)
        self.stop_btn.setEnabled(True)
        self.status_text.setText(f"状态: 从快照运行")
        self.status_text.setStyleSheet("font-size: 16px; color: #E91E63;")
        self.status_indicator.setText("● 快照模式")
        self.status_indicator.setStyleSheet("color: #E91E63; font-weight: bold;")
        self.status_bar.showMessage(f"虚拟机从快照 '{snapshot_name}' 运行中...")

    def ask_save_snapshot_changes(self):
        """询问从快照启动后是否保存更改"""
        snapshot_name = getattr(self, 'started_from_snapshot', '未知')

        msg = QMessageBox(self)
        msg.setWindowTitle("快照运行完成")
        msg.setText(f"从快照 '{snapshot_name}' 的运行已结束")
        msg.setInformativeText(
            "您想如何处理这次运行的更改？\n\n"
            "• 保存为新快照 — 保留更改到新的快照\n"
            "• 覆盖原快照 — 用当前状态替换原快照\n"
            "• 放弃更改 — 不保存任何更改"
        )

        save_new_btn = msg.addButton("💾 保存为新快照", QMessageBox.ButtonRole.AcceptRole)
        overwrite_btn = msg.addButton("📝 覆盖原快照", QMessageBox.ButtonRole.ActionRole)
        discard_btn = msg.addButton("🗑️ 放弃更改", QMessageBox.ButtonRole.DestructiveRole)

        msg.exec()

        if msg.clickedButton() == save_new_btn:
            self.save_as_new_snapshot()
        elif msg.clickedButton() == overwrite_btn:
            self.overwrite_snapshot(snapshot_name)
        else:
            self.log_text.append("✓ 已放弃快照运行的更改")

        # 清理
        self.started_from_snapshot = None
        self.snapshot_file_path = None
        self.snapshot_start_mode = False
        self.snapshot_start_btn.setEnabled(True)
        self.test_start_btn.setEnabled(True)

    def save_as_new_snapshot(self):
        """保存为新快照"""
        name, ok = QInputDialog.getText(
            self, "保存为新快照",
            "输入新快照名称:",
            QLineEdit.EchoMode.Normal,
            f"snapshot_{self.get_timestamp()}"
        )

        if ok and name:
            result = self.run_qemu_img(["snapshot", "-c", name, self.config['hdd_path']])
            if result and result.returncode == 0:
                self.log_text.append(f"✅ 新快照已保存: {name}")
                QMessageBox.information(self, "成功", f"快照 '{name}' 保存成功！")
                self.refresh_snapshot_list()  # 刷新下拉框
            else:
                error = result.stderr if result else "未知错误"
                self.log_text.append(f"❌ 保存快照失败: {error}")
                QMessageBox.critical(self, "错误", f"保存失败:\n{error}")

    def overwrite_snapshot(self, snapshot_name):
        """覆盖原快照"""
        reply = QMessageBox.warning(
            self, "确认覆盖",
            f"确定要覆盖快照 '{snapshot_name}' 吗？\n\n"
            "原快照内容将被当前状态替换！",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if reply != QMessageBox.StandardButton.Yes:
            return

        # 删除原快照
        result = self.run_qemu_img(["snapshot", "-d", snapshot_name, self.config['hdd_path']])
        if result and result.returncode == 0:
            # 创建同名新快照
            result = self.run_qemu_img(["snapshot", "-c", snapshot_name, self.config['hdd_path']])
            if result and result.returncode == 0:
                self.log_text.append(f"✅ 快照 '{snapshot_name}' 已更新")
                QMessageBox.information(self, "成功", f"快照 '{snapshot_name}' 已更新！")
            else:
                error = result.stderr if result else "未知错误"
                self.log_text.append(f"❌ 创建新快照失败: {error}")
                QMessageBox.critical(self, "错误", f"覆盖失败:\n{error}")
        else:
            error = result.stderr if result else "未知错误"
            self.log_text.append(f"❌ 删除原快照失败: {error}")
            QMessageBox.critical(self, "错误", f"覆盖失败:\n{error}")

    def get_timestamp(self):
        """获取时间戳字符串"""
        from datetime import datetime
        return datetime.now().strftime("%Y%m%d_%H%M%S")

    def open_remote_viewer(self):
        """打开 Remote Viewer 连接 SPICE"""
        remote_viewer_path = r"display\VirtViewer v11.0-256\bin\remote-viewer.exe"

        # 检查文件是否存在
        if not os.path.exists(remote_viewer_path):
            QMessageBox.critical(
                self, "错误",
                f"找不到 Remote Viewer:\n{remote_viewer_path}\n\n"
                "请确保路径正确，或在配置中修改路径。"
            )
            return

        # 构建 SPICE 连接地址
        spice_url = f"spice://127.0.0.1:{self.config['spice_port']}"

        try:
            self.log_text.append(f"正在启动 Remote Viewer: {spice_url}")
            subprocess.Popen(
                [remote_viewer_path, spice_url],
                creationflags=subprocess.CREATE_NO_WINDOW
            )
            self.status_bar.showMessage("Remote Viewer 已启动")
        except Exception as e:
            QMessageBox.critical(self, "错误", f"启动 Remote Viewer 失败:\n{str(e)}")

    def connect_rdp(self):
        """启动 RDP 连接"""
        # 使用 mstsc 命令启动远程桌面连接
        rdp_address = f"127.0.0.1:{self.config['rdp_port']}"

        try:
            self.log_text.append(f"正在启动 RDP 连接: {rdp_address}")
            # 使用系统默认的远程桌面客户端
            subprocess.Popen(
                ["mstsc", f"/v:{rdp_address}"],
                creationflags=subprocess.CREATE_NO_WINDOW
            )
            self.status_bar.showMessage(f"RDP 客户端已启动，连接 {rdp_address}")
        except Exception as e:
            QMessageBox.critical(self, "错误", f"启动 RDP 失败:\n{str(e)}")

    def show_rdp_help(self):
        """显示 RDP 使用说明"""
        help_text = """
<h2>🖥️ RDP 远程桌面使用说明</h2>

<h3>📌 什么是 RDP 转发端口？</h3>
<p>QEMU 将虚拟机内部的 RDP 服务（端口 3389）转发到主机的指定端口（默认 13389），
这样你就可以通过 Windows 远程桌面客户端连接到虚拟机。</p>

<h3>🚀 快速开始</h3>
<ol>
<li><b>启动虚拟机</b> — 点击"▶ 启动虚拟机"按钮</li>
<li><b>等待系统启动</b> — 在日志中看到系统启动完成</li>
<li><b>点击"连接 RDP 远程桌面"</b> — 自动打开 Windows 远程桌面客户端</li>
<li><b>输入用户名和密码</b> — 使用 Deepin 系统的账户登录</li>
</ol>

<h3>⚙️ 虚拟机内设置（首次使用需要）</h3>
<p>如果虚拟机内没有启用 RDP，需要先在 Deepin 中安装和启用：</p>
<pre style="background:#f0f0f0;padding:10px;border-radius:5px;">
# 安装 XRDP
sudo apt update
sudo apt install xrdp

# 启动 XRDP 服务
sudo systemctl enable xrdp
sudo systemctl start xrdp

# 查看服务状态
sudo systemctl status xrdp
</pre>

<h3>🔧 手动连接方法</h3>
<p>如果自动连接失败，可以手动打开远程桌面连接：</p>
<ol>
<li>按 <b>Win + R</b>，输入 <b>mstsc</b> 回车</li>
<li>在"计算机"栏输入：<b>127.0.0.1:13389</b></li>
<li>点击"连接"</li>
<li>输入 Deepin 的用户名和密码</li>
</ol>

<h3>❓ 常见问题</h3>
<p><b>Q: 连接失败怎么办？</b><br>
A: 检查以下几点：
<ul>
<li>虚拟机是否已完全启动</li>
<li>Deepin 内是否已安装并启动 xrdp</li>
<li>防火墙是否允许 3389 端口</li>
</ul>
</p>

<p><b>Q: 如何修改端口？</b><br>
A: 在"配置"标签页中修改"RDP 转发端口"，默认是 13389。</p>

<p><b>Q: SPICE 和 RDP 有什么区别？</b><br>
A: 
<ul>
<li><b>SPICE</b> — 图形性能好，适合日常使用，需要安装 VirtViewer</li>
<li><b>RDP</b> — Windows 自带，兼容性好，适合远程管理</li>
</ul>
</p>

<h3>💡 提示</h3>
<ul>
<li>建议先使用 Remote Viewer (SPICE) 安装配置好系统</li>
<li>RDP 更适合在 Windows 环境下远程管理虚拟机</li>
<li>两个可以同时使用，根据场景选择</li>
</ul>
        """

        msg = QMessageBox(self)
        msg.setWindowTitle("RDP 使用说明")
        msg.setTextFormat(Qt.TextFormat.RichText)
        msg.setText(help_text)
        msg.setStandardButtons(QMessageBox.StandardButton.Ok)
        msg.setMinimumWidth(600)
        msg.exec()

    def save_log(self):
        """保存日志到文件"""
        file_path, _ = QFileDialog.getSaveFileName(
            self, "保存日志", "vm_log.txt", "文本文件 (*.txt)"
        )
        if file_path:
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(self.log_text.toPlainText())
                QMessageBox.information(self, "成功", "日志已保存！")
            except Exception as e:
                QMessageBox.critical(self, "错误", str(e))

    def closeEvent(self, event):
        """关闭窗口时停止虚拟机"""
        if self.vm_runner and self.vm_runner.running:
            reply = QMessageBox.question(
                self, "确认退出",
                "虚拟机正在运行，确定要退出吗？",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            if reply == QMessageBox.StandardButton.Yes:
                self.stop_vm()
                event.accept()
            else:
                event.ignore()
        else:
            event.accept()


def main():
    app = QApplication(sys.argv)
    app.setStyle('Fusion')

    # 设置应用程序图标（任务栏和窗口）
    icon_path = get_resource_path("icon.ico")
    if os.path.exists(icon_path):
        app.setWindowIcon(QIcon(icon_path))

    # 设置应用程序字体
    font = QFont("Microsoft YaHei", 10)
    app.setFont(font)

    window = VMManager()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
