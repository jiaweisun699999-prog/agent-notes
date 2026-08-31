import uuid
from datetime import datetime
from typing import Union, List

from pydantic import BaseModel, Field

from api.schemas import InDBMixin


class GrapConfigurableSchema(BaseModel):
    """普通的Schema"""
    passenger_id: str = Field(description='旅客的ID号', default="3442 587242")
    thread_id: Union[str, None] = Field(description='会话ID', default=str(uuid.uuid4()))


class GraphConfigSchema(BaseModel):
    """配置的Schema"""
    configurable: Union[GrapConfigurableSchema, None] = Field(description='封装配置', default=None)


class BaseGraphSchema(BaseModel):
    """调用工作流的请求参数：的Schema"""
    user_input: str = Field(description='消费者用户输入的内容', default=None)
    config: Union[GraphConfigSchema, None] = Field(description='封装的配置信息', default=None)


class GraphRspSchema(BaseModel):
    """工作流执行完成之后的输出 类型"""
    assistant: str = Field(description='工作流执行后，AI助手响应内容', default=None)