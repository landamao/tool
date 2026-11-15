#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import secrets
import string

def secure_shuffle(lst):
    """
    使用密码学安全的随机数生成器打乱列表（Fisher-Yates 洗牌算法）
    """
    for i in range(len(lst) - 1, 0, -1):
        j = secrets.randbelow(i + 1)
        lst[i], lst[j] = lst[j], lst[i]

def generate_password(length=30):
    """
    生成一个符合要求的高强度密码

    参数:
        length: 密码长度，必须在 8 到 30 之间（默认为 30）

    返回:
        符合规则的密码字符串

    规则:
        - 长度 8~30
        - 不含空格
        - 首字符不能为 '/'
        - 至少包含小写字母、大写字母、数字、特殊符号中的三类
        （实际实现包含全部四类，强度更高）
    """
    if not (8 <= length <= 30):
        raise ValueError("密码长度必须在 8 到 30 之间")

    # 定义字符集
    lower = string.ascii_lowercase          # a-z
    upper = string.ascii_uppercase          # A-Z
    digits = string.digits                  # 0-9
    special = "()`~!@#$%^&*-+=_|{}[]:;'<>,.?/"  # 允许的特殊符号（不含空格）

    all_chars = lower + upper + digits + special

    while True:
        # 确保每种字符集至少出现一次（满足“至少包含三类”且强度更高）
        password_chars = [
            secrets.choice(lower),
            secrets.choice(upper),
            secrets.choice(digits),
            secrets.choice(special)
        ]

        # 填充剩余字符（随机从所有字符中选取）
        remaining = length - 4
        for _ in range(remaining):
            password_chars.append(secrets.choice(all_chars))

        # 安全打乱顺序
        secure_shuffle(password_chars)

        password = ''.join(password_chars)

        # 检查首字符是否为 '/'
        if password[0] != '/':
            return password

if __name__ == "__main__":
    # 生成一个 30 位的密码
    pwd = generate_password(30)
    print("生成的密码:", pwd)

    # 验证规则（仅供测试）
    print("\n验证结果:")
    print(f"长度: {len(pwd)} (应为30)")
    print(f"首字符是否为 '/': {pwd[0] == '/'}")
    has_lower = any(c in string.ascii_lowercase for c in pwd)
    has_upper = any(c in string.ascii_uppercase for c in pwd)
    has_digit = any(c in string.digits for c in pwd)
    special_set = "()`~!@#$%^&*-+=_|{}[]:;'<>,.?/"
    has_special = any(c in special_set for c in pwd)
    print(f"包含小写字母: {has_lower}")
    print(f"包含大写字母: {has_upper}")
    print(f"包含数字: {has_digit}")
    print(f"包含特殊符号: {has_special}")
    categories = sum([has_lower, has_upper, has_digit, has_special])
    print(f"包含的字符类别数: {categories} (至少需要3)")
    print("是否包含空格:", ' ' in pwd)
