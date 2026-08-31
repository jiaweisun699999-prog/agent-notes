from datetime import datetime
from typing import Union, List

from pydantic import BaseModel, Field

from api.schemas import InDBMixin


class BaseUserSchema(BaseModel):
    """普通用户的Schema"""
    username: str = Field(description='用户名', default=None)
    # 为什么没有密码属性： 查询某一个用户信息---> json里面要不要包含密码？
    phone: Union[str, None] = Field(description='用户手机号', default=None)
    email: Union[str, None] = Field(description='用户游戏', default=None)
    real_name: Union[str, None] = Field(description='用户真实姓名', default=None)
    icon: Union[str, None] = Field(description='用户头像', default=None)
    dept_id: Union[int, None] = Field(description='所属部门ID', default=None)


class GetUserList(BaseModel):
    """获取用户列表的时候的Schema"""
    username: str = Field(description='用户名', default=None)
    id: int = Field(description='用户ID编号', default=None)

class CreateOrUpdateUserSchema(BaseUserSchema):
    """创建或者修改用户的Schema"""
    password: str = Field(description='密码', default=None)
    roles: List[int] = Field(description='用户所选的角色ID列表', default=None)


class UserSchema(BaseUserSchema, InDBMixin):
    """查询用户数据的Schema"""
    create_time: Union[datetime, None] = Field(description='创建时间', default=None)
    id: int = Field(description='用户ID编号', default=None)
    # create_time: Union[datetime, None] = Field(description='创建时间', default=None)


class UserLoginSchema(BaseModel):
    """用户登录接受数据的模型类型"""
    username: str = Field(description='用户名')
    password: str = Field(description='密码')


class UserLoginRspSchema(UserSchema):
    """用户登录之后响应类型"""
    token: str
