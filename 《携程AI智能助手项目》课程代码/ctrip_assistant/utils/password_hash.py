from passlib.context import CryptContext

# 密码哈希的算法：bcrypt
# 当设置为 "auto" 时，它将根据已配置的密码哈希方案自动确定哪些方案被视为过时的，并且在验证密码时会更新为更安全的哈希算法。
password_context = CryptContext(schemes=['bcrypt'], deprecated='auto')


def get_hashed_password(password: str) -> str:
    """
    接受一个真实的密码，返回一个hash之后的密文
    :param password:
    :return:
    """
    return password_context.hash(password)


def verify_password(password: str, hashed_pass: str) -> bool:
    """
    校验密码是否正确
    :param password: 传入的密码
    :param hashed_pass: hash之后密文
    :return:
    """
    return password_context.verify(password, hashed_pass)