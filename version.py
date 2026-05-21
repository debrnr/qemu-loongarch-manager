# -*- coding: utf-8 -*-
"""
版本信息
"""

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


# 当前版本
VERSION = get_version()
VERSION_STR = f"QML v{VERSION}"
