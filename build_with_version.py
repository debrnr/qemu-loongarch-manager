#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
打包脚本：生成带版本号的 exe
版本号格式：年月日 + 字母数字组合
例如：Deepin_VM_Manager_20250521_A1.exe
"""

import subprocess
import sys
import os
from datetime import datetime


def get_version():
    """生成版本号：年月日(简写)_字母数字"""
    today = datetime.now()
    # 简写年月日：年份后两位 + 月份 + 日期 = 5位
    date_str = today.strftime("%y%m%d")  # 例如：260521
    # 使用字母和数字组合，基于小时和分钟
    hour = today.hour
    minute = today.minute
    # A-M 对应 0-12 小时，数字对应分钟十位
    hour_letter = chr(ord('A') + hour % 13)  # A-M
    minute_digit = minute // 10  # 0-5
    version = f"{date_str}_{hour_letter}{minute_digit}"
    return version


def build():
    """使用 PyInstaller 打包"""
    version = get_version()
    exe_name = f"QML_{version}"

    print(f"版本号: {version}")
    print(f"输出文件名: {exe_name}.exe")
    print("-" * 50)

    # 打包命令
    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--onefile",           # 打包成单个文件
        "--windowed",          # Windows GUI 程序
        "--name", exe_name,    # 带版本号的文件名
        "--icon", "icon.ico",  # 图标
        "--add-data", "icon.ico;.",  # 包含图标资源
        "--add-data", "version.py;.",  # 包含版本信息
        "--clean",             # 清理临时文件
        "--noconfirm",         # 不确认覆盖
        "vm_manager.py"
    ]

    print("开始打包...")
    print(f"命令: {' '.join(cmd)}")
    print("-" * 50)

    result = subprocess.run(cmd)

    if result.returncode == 0:
        print("-" * 50)
        print("打包成功！")
        print(f"版本号: {version}")
        print(f"输出文件: dist/{exe_name}.exe")
        print("\n提示：")
        print("1. exe 文件可以复制到其他机器运行")
        print("2. 需要确保目标机器有 QEMU 文件在正确路径")
        print("3. 配置文件 vm_config.json 会自动生成")
    else:
        print("-" * 50)
        print("打包失败！")
        return result.returncode

    return 0


if __name__ == "__main__":
    sys.exit(build())
