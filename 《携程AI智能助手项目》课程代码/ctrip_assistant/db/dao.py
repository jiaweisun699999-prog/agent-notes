from typing import Generic, List

from fastapi.encoders import jsonable_encoder
from sqlalchemy import select, delete
from sqlalchemy.orm import Session

from api.schemas import ModelType, CreateSchema, UpdateSchema


class BaseDAO(Generic[ModelType, CreateSchema, UpdateSchema]):
    """通过实例化 Generic 数组并传入类型参数来定义具体的泛型类。"""

    model: ModelType  # 具体的数据库模型类

    '''以下开始对数据库进行增，删，改，查等操作'''

    def get(self, session: Session) -> List[ModelType]:
        """
        查询所有的模型对象
        :param session:
        :return:
        """
        return session.scalars(select(self.model)).all()

    def get_by_id(self, session: Session, pk: int) -> ModelType:
        """
        根据主键的值返回模型对象的实例
        :param session:
        :param pk:
        :return:
        """
        return session.get(self.model, pk)

    def create(self, session: Session, obj_in: CreateSchema) -> ModelType:
        """
        插入一条数据
        :param session:
        :param obj_in:
        :return:
        """
        obj = self.model(**jsonable_encoder(obj_in))  # 把Pydantic的模型类转化为字典
        session.add(obj)
        session.commit()
        return obj

    def update(self, session: Session, pk: int, obj_in: UpdateSchema) -> ModelType:
        """
        修改一条数据
        :param session:
        :param pk: 主键ID
        :param obj_in: 修改的BaseModel类
        :return:
        """
        obj = self.get_by_id(session, pk)
        update_data = obj_in.dict(exclude_unset=True)  # 排除模型中的默认值
        for key, val in update_data.items():
            setattr(obj, key, val)
        session.add(obj)
        session.commit()
        session.refresh(obj)
        return obj

    def delete(self, session: Session, pk: int) -> None:
        """
        删除一条记录
        :param session:
        :param pk:
        :return:
        """
        obj = self.get_by_id(session, pk)
        session.delete(obj)
        session.commit()

    def count(self, session: Session):
        """
        返回数据总条数
        :param session:
        :return:
        """
        return session.query(self.model).count()

    def deletes(self, session: Session, ids: List[int]):
        """
        根据多个主键，批量删除
        :param session:
        :param ids:
        :return:
        """
        stmt = delete(self.model).where(self.model.id.in_(ids))
        session.execute(stmt)
        session.commit()
