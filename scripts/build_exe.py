#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
打包脚本：将 VM Manager 打包成单个 exe 文件
"""

import subprocess
import sys
import os

def build():
    """使用 PyInstaller 打包"""

    # 打包命令
    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--onefile",           # 打包成单个文件
        "--windowed",          # Windows GUI 程序（无控制台窗口）
        "--name", "Deepin_VM_Manager",  # 输出文件名
        "--icon", "icon.ico",  # 图标文件
        "--clean",             # 清理临时文件
        "--noconfirm",         # 不确认覆盖
        # 添加数据文件（图标）
        "--add-data", "icon.ico;.",
        "vm_manager.py"
    ]

    print("开始打包...")
    print(f"命令: {' '.join(cmd)}")
    print("-" * 50)

    result = subprocess.run(cmd, capture_output=False, text=True)

    if result.returncode == 0:
        print("-" * 50)
        print("✅ 打包成功！")
        print("输出文件: dist/Deepin_VM_Manager.exe")
        print("\n提示：")
        print("1. exe 文件可以复制到其他机器运行")
        print("2. 需要确保目标机器有 QEMU 文件在正确路径")
        print("3. 配置文件 vm_config.json 会自动生成")
    else:
        print("-" * 50)
        print("❌ 打包失败！")
        return result.returncode

    return 0

if __name__ == "__main__":
    sys.exit(build())
