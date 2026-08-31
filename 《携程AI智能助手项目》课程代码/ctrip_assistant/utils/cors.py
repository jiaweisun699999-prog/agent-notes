from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from config import settings


def init_cors(app: FastAPI) -> None:
    """
    在app中注册cors的中间件，cors的中间件名字是：CORSMiddleware
    :param app:
    :return:
    """
    app.add_middleware(CORSMiddleware,
                       allow_origins=settings.ORIGINS,  # 前端服务器的源
                       allow_credentials=True,  # 指示跨域请求支持 cookies
                       allow_methods=["*"],  # 允许所有标准方法
                       allow_headers=["*"],
                       )