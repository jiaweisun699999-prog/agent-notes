import uvicorn
from fastapi import FastAPI, Depends
from starlette.staticfiles import StaticFiles
from config import settings
from utils import handler_error, cors, middlewares

from config.log_config import init_log
from api import routers
from utils.docs_oauth2 import MyOAuth2PasswordBearer


class Server:

    def __init__(self):
        init_log()  # 加载日志的配置
        # 创建自定义的OAuth2的实例
        my_oauth2 = MyOAuth2PasswordBearer(tokenUrl='/api/auth/', schema='JWT')
        # 添加全局的依赖: 让所有的接口，都拥有接口文档的认证
        self.app = FastAPI(dependencies=[Depends(my_oauth2)])
        # 把项目下的static目录作为静态文件的访问目录
        self.app.mount('/static', StaticFiles(directory='static'), name='my_static')

    def init_app(self):
        # 初始化全局异常处理
        handler_error.init_handler_errors(self.app)
        # 初始化全局中间件
        middlewares.init_middleware(self.app)
        # 初始化全局CORS跨域的处理
        cors.init_cors(self.app)
        # 初始化主路由
        routers.init_routers(self.app)

    def run(self):
        self.init_app()
        uvicorn.run(
            app=self.app,
            host=settings.HOST,
            port=settings.PORT
        )


if __name__ == '__main__':
    Server().run()