"""速率限制"""
import time

from langchain.chat_models import init_chat_model
from langchain_core.rate_limiters import InMemoryRateLimiter

from env_utils import DEEPSEEK_API_KEY, DEEPSEEK_BASE_URL

rate_limiter = InMemoryRateLimiter(
    requests_per_second = 0.1, # 每10秒最多1个请求
    check_every_n_seconds = 0.1, # 检查间隔0.1秒
    max_bucket_size = 5, #流量高峰最多允许的请求个数
)



deepseek_llm = init_chat_model(
    model="deepseek-chat",
    model_provider="deepseek",
    api_key=DEEPSEEK_API_KEY,
    base_url=DEEPSEEK_BASE_URL,
    rate_limiter=rate_limiter # 模型速度限制
)

for i in range(3):
    response = deepseek_llm.invoke("你好")
    print(response.content)
    print(time.time())




