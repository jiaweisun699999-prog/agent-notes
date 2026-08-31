import os

from dotenv import load_dotenv

# 从.env文件加载环境变量
load_dotenv(override=True)

# 加载DeepSeek环境变量
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")
DEEPSEEK_BASE_URL = os.getenv("DEEPSEEK_BASE_URL")

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_BASE_URL = os.getenv("OPENAI_BASE_URL")

ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
ANTHROPIC_BASE_URL = os.getenv("ANTHROPIC_BASE_URL")

HUNYUAN_APP_ID = os.getenv("HUNYUAN_APP_ID")
HUNYUAN_SECRET_ID = os.getenv("HUNYUAN_SECRET_ID")
HUNYUAN_SECRET_KEY = os.getenv("HUNYUAN_SECRET_KEY")

DASHSCOPE_API_KEY = os.getenv("DASHSCOPE_API_KEY")
DASHSCOPE_BASE_URL = os.getenv("DASHSCOPE_BASE_URL")

ZHIPUAI_API_KEY = os.getenv("ZHIPUAI_API_KEY")
ZHIPUAI_BASE_URL = os.getenv("ZHIPUAI_BASE_URL")
