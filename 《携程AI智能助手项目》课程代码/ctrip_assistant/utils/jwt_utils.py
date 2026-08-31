from datetime import datetime, timedelta
from typing import Union, Any

from jose import jwt

from config import settings

# 用于访问的：JWT令牌的有效时间
ACCESS_TOKEN_EXPIRE_MINUTES = settings.ACCESS_TOKEN_EXPIRE_MINUTES  # 30 minutes
#  JWT令牌的有效时间: 较长
# REFRESH_TOKEN_EXPIRE_MINUTES = 60 * 24 * 7  # 7 days
# 加密算法
ALGORITHM = settings.ALGORITHM
# 密钥
JWT_SECRET_KEY = settings.JWT_SECRET_KEY


def create_token(subject: Union[str, Any], expires_delta: int = None) -> str:
    """
    根据用户的信息创建一个token。
    subject ---> token  未来， token ---> subject
    :param subject: 用户信息
    :param expires_delta: 有效时间戳
    :return:
    """
    if expires_delta:
        # 自定义token的过期时间
        expires_delta = datetime.utcnow() + expires_delta
    else:
        # 默认的token过期时间
        expires_delta = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    # 根据subject和过期时间生成一个token
    return jwt.encode({'exp': expires_delta, 'sub': str(subject)}, JWT_SECRET_KEY, ALGORITHM)


if __name__ == '__main__':
    print(create_token('lisi'))
