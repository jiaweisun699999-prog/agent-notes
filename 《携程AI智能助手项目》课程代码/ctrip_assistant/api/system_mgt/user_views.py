import logging
from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from starlette import status

from api.system_mgt.user_schemas import CreateOrUpdateUserSchema, UserSchema, UserLoginRspSchema, UserLoginSchema, \
    GetUserList
from config import settings
from db.system_mgt.user_dao import UserDao
from utils.dependencies import get_db
from utils.jwt_utils import create_token
from utils.password_hash import get_hashed_password, verify_password

# 创建分路由
router = APIRouter()
# 创建dao类的对象实例
_dao = UserDao()

log = logging.getLogger('emp')


@router.get('/users/getUsers/', description='得到所有的用户信息', response_model=List[GetUserList])
def get_users(session: Session = Depends(get_db)):
    return _dao.get(session)


@router.get('/users/{pk}/', description='根据主键查询用户信息', summary='单个查询', response_model=UserSchema)
def get_by_id(pk: int, session: Session = Depends(get_db)):
    return _dao.get_by_id(session, pk)


@router.post('/register/', description='创建用户', summary='用户注册', response_model=UserSchema)
def create(obj_in: CreateOrUpdateUserSchema, session: Session = Depends(get_db)):
    if not obj_in.password:
        obj_in.password = str(settings.DEFAULT_PASSWORD)  # 添加用户时：给所有用户一个默认的密码

    # 把密码变成hash之后的密文
    obj_in.password = get_hashed_password(obj_in.password)

    return _dao.create(session, obj_in)


@router.post('/login/', description='用户登录', summary='用户登录', response_model=UserLoginRspSchema)
def login(obj_in: UserLoginSchema, session: Session = Depends(get_db)):
    # 实现用户登录，成功之后返回用户信息，包括token
    # 第一步：根据用户名去查询用户
    user = _dao.get_user_by_username(session, obj_in.username)
    log.info(user)
    if not user:  # 用户不存在
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f'用户名{obj_in.username}，在数据库表中不存在!'
        )
    if not verify_password(obj_in.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f'登录密码错误'
        )
    # 代码执行到此，则登录成功
    return {
        'id': user.id,
        'username': user.username,
        'phone': user.phone,
        'real_name': user.real_name,
        'token': create_token(str(user.id) + ':' + user.username)  # 创建token
    }


@router.post('/auth/', description='接口文档中认证表单提交')
def auth(form_data: OAuth2PasswordRequestForm = Depends(), session: Session = Depends(get_db)):
    """
    接口文档中，用于接受认证表单提交的视图函数
    :param form_data: 表单数据
    :param session:
    :return:
    """
    user = _dao.get_user_by_username(session, form_data.username)
    log.info(user)
    if not user:  # 用户不存在
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f'用户名{form_data.username}，在数据库表中不存在!'
        )
    if not verify_password(form_data.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f'登录密码错误'
        )
    # 代码执行到此，则登录成功
    return {
        'access_token': create_token(str(user.id) + ':' + user.username),  # 创建token
        'token_type': 'bearer'
    }


@router.patch('/users/{pk}/', response_model=UserSchema, description='根据主键，修改用户')
def patch(pk: int, obj_in: CreateOrUpdateUserSchema,
          session: Session = Depends(get_db)):
    return _dao.update(session, pk, obj_in)


@router.post('/users/delete/', description='根据主键批量删除多个用户')
def delete(ids: List[int], session: Session = Depends(get_db)):
    return _dao.deletes(session, ids)
