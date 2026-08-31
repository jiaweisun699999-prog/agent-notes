# 定义数据库连接的URL
from datetime import datetime

from sqlalchemy import URL, create_engine, DateTime, func
from sqlalchemy.orm import sessionmaker, scoped_session, DeclarativeBase, declared_attr, Mapped, mapped_column

from config import settings

url = URL(
    drivername=settings.DATABASE.DRIVER,
    username=settings.DATABASE.get('USERNAME', None),
    password=settings.DATABASE.get('PASSWORD', None),
    host=settings.DATABASE.get('HOST', None),
    port=settings.DATABASE.get('PORT', None),
    database=settings.DATABASE.get('NAME', None),
    query=settings.DATABASE.get('QUERY', None),
)

engine = create_engine(url, echo=True, future=True, pool_size=10)

sm = sessionmaker(bind=engine, autoflush=True, autocommit=False)


class DBModelBase(DeclarativeBase):
    """ 定义一系列的可以映射的公共属性，此类是所有数据库模型类的父类"""

    @declared_attr.directive
    def __tablename__(cls) -> str:
        return 't_'+cls.__name__.lower()  # 未来所有的模型中：表名就是：t_当前模型类名字

    __table_args__ = {"mysql_engine": "InnoDB"}
    #  如果为true，则ORM将在插入或更新之后立即获取服务器生成的默认值的值
    __mapper_args__ = {"eager_defaults": True}

    # 所有的模型类，都有的属性和字段映射
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    create_time: Mapped[datetime] = mapped_column(DateTime, insert_default=func.now(), comment='记录的创建时间')
    update_time: Mapped[datetime] = mapped_column(DateTime, insert_default=func.now(), onupdate=func.now(),
                                                  comment='记录的最后一次修改时间')