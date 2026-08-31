from fastapi import Request
from sqlalchemy.orm import Session

from db import sm


def get_db(request: Request) -> Session:
    """
    session的依赖注入函数, 每个视图函数的操作，都会有一个独立新session
    :param request:
    :return:
    """
    try:
        session = sm()
        yield session
    finally:
        session.close()


