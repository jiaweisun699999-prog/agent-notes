from typing import Optional, List

from sqlalchemy import String, Integer, Boolean, ForeignKey, Table, Column
from sqlalchemy.orm import Mapped, mapped_column, relationship
from db import DBModelBase


class UserModel(DBModelBase):
    """用户模型类"""

    username: Mapped[str] = mapped_column(String(20), unique=True, nullable=False)
    password: Mapped[str] = mapped_column(String(200), nullable=False)
    phone: Mapped[str] = mapped_column(String(20), nullable=True, comment='用户的手机号码')
    email: Mapped[str] = mapped_column(String(50), nullable=True, comment='用户的邮箱地址')
    real_name: Mapped[str] = mapped_column(String(50), nullable=True, comment='用户的真实名字')
    icon: Mapped[str] = mapped_column(String(100), default='/static/user_icon/default.jpg', nullable=True,
                                      comment='用户的展示头像')
