#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
安装脚本
"""

from setuptools import setup, find_packages

setup(
    name="deepin-vm-manager",
    version="1.0.0",
    description="Deepin LoongArch VM 管理器",
    author="VM Manager",
    python_requires=">=3.8",
    install_requires=[
        "PyQt6>=6.4.0",
    ],
    entry_points={
        "console_scripts": [
            "vm-manager=vm_manager:main",
        ],
    },
)
