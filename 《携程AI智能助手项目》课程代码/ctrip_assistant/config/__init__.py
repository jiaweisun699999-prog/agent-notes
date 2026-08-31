from pathlib import Path
from dynaconf import Dynaconf

_BASE_DIR = Path(__file__).parent.parent  # 得到项目目录

settings_files = [
    Path(__file__).parent / 'development.yml',  # 开发时候的配置文件
    # Path(__file__).parent / 'production.yml'
]  # 指定绝对路径加载默认配置


# settings 就是配置对象
settings = Dynaconf(
    envvar_prefix="EMP_CONF",  # 环境变量前缀。
    settings_files=settings_files,
    env_switcher="EMP_ENV",  # 用于切换模式的环境变量名称 EMP_ENV=production
    lowercase_read=False,  # 禁用小写访问， settings.name 是不允许的
    base_dir=_BASE_DIR,  # 指定项目目录
)