import logging
import re
import traceback
from datetime import datetime
from typing import Callable

from fastapi import FastAPI
from fastapi.requests import Request
from fastapi.responses import Response
from fastapi.responses import JSONResponse
from jose import jwt, ExpiredSignatureError
from starlette import status

from config import settings

log = logging.getLogger('emp')


async def verify_token(request: Request, call_next: Callable) -> Response:
    # OAuth2的规范，如果认证失败，请求头中返回“WWW-Authenticate”
    auth_error = JSONResponse({'detail': '非法的指令牌Token，请重新登录！'}, status_code=status.HTTP_401_UNAUTHORIZED,
                              headers={"WWW-Authenticate": "Bearer"})
    # token校验的中间件

    # 是不是所有api接口都需要token验证？ 有很多是不需要的
    # 不需要的可以把它们保存到一个白名单里面。

    # 得到请求路径
    path: str = request.get('path')
    # 从白名单中匹配请求路径
    for request_path in settings.WHITE_LIST:
        if re.match(request_path, path):
            return await call_next(request)  # 继续往下执行
    else:  # 请求路径不是白名单里面的
        # 从请求的header中读取token
        # curl -X GET "http://localhost:8000/api/test" -H "Authorization: Bearer {token}"
        authorization: str = request.headers.get('Authorization')
        if not authorization:
            return auth_error
        token: str = authorization.split(' ')[1]
        try:
            # 校验token
            res_dict = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.ALGORITHM])
            username = res_dict.get('sub').split(':')[1]

            # 判断是否超时
            if not username:
                return auth_error
            if datetime.fromtimestamp(res_dict.get('exp')) < datetime.now():  # 超时了
                return auth_error

            request.state.username = username  # 把用户名绑定到request对象中
            return await call_next(request)
        except ExpiredSignatureError as e:
            log.error('\n' + traceback.format_exc())
            return auth_error
        except Exception as e:
            log.error(e)
            log.error('\n' + traceback.format_exc())
            return JSONResponse({'detail': '服务器接口异常，请求检查接口'}, status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)


def init_middleware(app: FastAPI) -> None:
    # 在app中注册中间件。 才能生效
    # app.middleware('http')(db_session_middleware)
    app.middleware('http')(verify_token)
