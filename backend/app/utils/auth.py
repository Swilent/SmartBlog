from flask import current_app
from typing import List


def verify_ip(client_ip: str, whitelist: list) -> bool:
    """
    验证客户端 IP 是否在白名单中

    Args:
        client_ip: 客户端 IP 地址
        whitelist: IP 白名单列表

    Returns:
        bool: 是否在白名单中
    """
    if not whitelist:
        return True

    # 移除 IP 地址可能的端口号
    if ':' in client_ip and client_ip.count(':') > 1:
        # IPv6 地址
        pass
    elif ':' in client_ip:
        client_ip = client_ip.split(':')[0]

    # 检查 IP 是否在白名单中
    for allowed_ip in whitelist:
        allowed_ip = allowed_ip.strip()
        if not allowed_ip:
            continue

        # 支持通配符匹配（简单版本）
        if allowed_ip == '*':
            return True

        if client_ip == allowed_ip:
            return True

    return False


def verify_credentials(username: str, password: str, app) -> bool:
    """
    验证管理员用户名和密码

    Args:
        username: 用户名
        password: 密码
        app: Flask 应用实例

    Returns:
        bool: 是否验证通过
    """
    correct_username = app.config['ADMIN_USERNAME']
    correct_password = app.config['ADMIN_PASSWORD']

    return username == correct_username and password == correct_password
