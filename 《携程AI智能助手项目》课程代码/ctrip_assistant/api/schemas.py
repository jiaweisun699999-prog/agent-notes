from typing import TypeVar

from pydantic import BaseModel

from db import DBModelBase

# 先定义三种泛型, 以便于在数据库操作的时候更加方便。
ModelType = TypeVar('ModelType', bound=DBModelBase)
CreateSchema = TypeVar('CreateSchema', bound=BaseModel)
UpdateSchema = TypeVar('UpdateSchema', bound=BaseModel)


class InDBMixin(BaseModel):
    """
    定义一个基类， 所有响应的模型的父类
    """

    class Config:
        # 有了这个配置，才能把ORM数据库模型类对象转化成Pydantic模型对象
        # orm_mode = True 老版本
        from_attributes = True
