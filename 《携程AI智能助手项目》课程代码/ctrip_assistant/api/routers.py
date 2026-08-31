from fastapi import APIRouter, FastAPI

from api.system_mgt import user_views
from api.graph_api import graph_views


def router_v1():
    # 主路由
    root_router = APIRouter()
    # 加载所有的分路由
    root_router.include_router(user_views.router, tags=['用户管理'])
    root_router.include_router(graph_views.router, tags=['工作流调用'])

    return root_router


def init_routers(app: FastAPI):
    app.include_router(router_v1(), prefix='/api')
