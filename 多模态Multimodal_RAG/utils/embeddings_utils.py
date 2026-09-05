import os
import time
from http import HTTPStatus
from typing import Tuple, List, Dict, Optional

import dashscope

from utils.env_utils import ALIBABA_API_KEY
from utils.log_utils import log

# ========= 配置区 =========
DASHSCOPE_MODEL = "multimodal-embedding-v1"  # 指定使用的达摩院多模态嵌入模型名称

RPM_LIMIT = 120  # 每分钟最多调用次数（Requests Per Minute）
WINDOW_SECONDS = 60  # 限流时间窗口（秒），与RPM_LIMIT配合实现每分钟限流

RETRY_ON_429 = True  # 是否在遇到429（请求过多）状态码时进行重试
MAX_429_RETRIES = 5  # 429状态码的最大重试次数
BASE_BACKOFF = 2.0  # 指数退避算法的基础等待时间（秒）

# 图片最大体积（URL HEAD 检查），若超过则跳过图片项
MAX_IMAGE_BYTES = 3 * 1024 * 1024  # 3MB
# ======== 配置区结束 =========


# 全局数据容器，用于存储所有处理后的数据
all_data: List[Dict] = []


class FixedWindowRateLimiter:
    """固定窗口速率限制器类，用于控制API调用频率"""

    def __init__(self, limit: int, window_seconds: int):
        """初始化速率限制器

        Args:
            limit: 时间窗口内允许的最大请求数
            window_seconds: 时间窗口长度（秒）
        """
        self.limit = limit
        self.window_seconds = window_seconds
        self.window_start = time.monotonic()  # 当前时间窗口的开始时间
        self.count = 0  # 当前时间窗口内的请求计数

    def acquire(self):
        """获取请求许可，如果需要会阻塞直到可以继续请求"""
        now = time.monotonic()
        elapsed = now - self.window_start  # 计算当前时间窗口已过去的时间

        # 如果已超过时间窗口，重置计数器和窗口开始时间
        if elapsed >= self.window_seconds:
            self.window_start = now
            self.count = 0

        # 如果当前窗口内请求数已达到限制，需要等待
        if self.count >= self.limit:
            sleep_sec = self.window_seconds - elapsed  # 计算需要等待的时间
            if sleep_sec > 0:
                print(f"[限速] 达到 {self.limit} 次请求，等待 {sleep_sec:.2f}s...")
                time.sleep(sleep_sec)  # 阻塞等待
            # 等待后重置计数器和窗口开始时间
            self.window_start = time.monotonic()
            self.count = 0

        self.count += 1  # 增加请求计数


# 创建全局速率限制器实例
limiter = FixedWindowRateLimiter(RPM_LIMIT, WINDOW_SECONDS)


def image_to_base64(img: str) -> Tuple[str, str]:
    """将图片转换为base64编码"""

    try:
        import base64, mimetypes
        # 猜测文件MIME类型
        mime = mimetypes.guess_type(img)[0] or "image/png"
        # 读取文件并编码为base64
        with open(img, "rb") as f:
            b64 = base64.b64encode(f.read()).decode("utf-8")
        # 构建data URI格式
        api_img = f"data:{mime};base64,{b64}"
        # store 用原路径或 basename 或 URL 原值，这里存原字符串
        return api_img, img
    except Exception as e:
        print(f"[图片] 本地文件转 base64 失败：{e}")
        log.exception(e)
        return "", ""


def normalize_image(img: str) -> Tuple[str, str]:
    """规范化图像输入，处理URL和本地文件两种类型

    返回元组 (api_image, store_image)
    api_image 用于向量化；store_image 用于入库；
    若图片无效或超过限制，则返回 ("", "")

    Args:
        img: 图像路径或URL字符串

    Returns:
        Tuple[str, str]: (用于API的图像数据, 用于存储的图像标识)
    """
    if not img:
        return "", ""

    raw = img.strip()  # 去除首尾空格
    low = raw.lower()  # 转换为小写便于判断

    # URL处理
    if low.startswith("http://") or low.startswith("https://"):
        try:
            import requests
            # 发送HEAD请求获取图像信息
            head = requests.head(raw, timeout=5, allow_redirects=True)
            if head.status_code == 200:
                # 获取图像大小
                size = int(head.headers.get("Content-Length") or 0)
                if size and size > MAX_IMAGE_BYTES:
                    print(f"[图片] URL 大小 {size} > {MAX_IMAGE_BYTES}，跳过该图：{raw}")
                    return "", ""
            else:
                print(f"[图片] URL 不可达，status {head.status_code}：{raw}")
                return "", ""
        except Exception as e:
            print(f"[图片] HEAD 检查异常：{e}")
        # API 用 URL；store 用 URL 原值
        return raw, raw

    # 文件 scheme file:/// 处理（目前返回空，可能需要进一步实现）
    if low.startswith("file:///"):
        return "", ""

    # 本地文件处理
    if os.path.isfile(raw):
        return image_to_base64(raw)

    # 其他不支持的类型
    return "", ""


def call_dashscope_once(input_data: List[Dict]) -> Tuple[bool, List[float], Optional[int], Optional[float]]:
    """调用达摩院多模态嵌入API一次

    Args:
        input_data: 输入数据列表，包含文本或图像数据

    Returns:
        Tuple: (成功标志, 嵌入向量, HTTP状态码, 重试等待时间)
    """
    # 应用速率限制
    limiter.acquire()

    try:
        # 调用达摩院多模态嵌入API
        response = dashscope.MultiModalEmbedding.call(
            model=DASHSCOPE_MODEL,
            input=input_data,
            api_key=ALIBABA_API_KEY
        )
    except Exception as e:
        print(f"调用 DashScope 异常：{e}")
        log.exception(e)
        return False, [], None, None

    # 获取HTTP状态码
    status = getattr(response, "status_code", None)
    retry_after = None

    # 检查是否需要重试等待
    try:
        headers = getattr(response, "headers", None)
        if headers and isinstance(headers, dict):
            ra = headers.get("Retry-After") or headers.get("retry-after")
            if ra:
                retry_after = float(ra)
    except Exception as e:
        pass
        # log.exception(e)

    # 获取API返回的代码和消息
    resp_code = getattr(response, "code", "")
    resp_msg = getattr(response, "message", "")

    # 处理成功响应
    if status == HTTPStatus.OK:
        try:
            # 提取嵌入向量
            embedding = response.output['embeddings'][0]['embedding']
            return True, embedding, status, retry_after
        except Exception as e:
            print(f"解析嵌入失败：{e}")
            log.exception(e)
            return False, [], status, retry_after
    else:
        # 处理失败响应
        print(f"请求失败，状态码：{status}，code：{resp_code}，message：{resp_msg}")
        return False, [], status, retry_after


def process_item_with_guard(item: Dict) -> Dict:
    """处理单个数据项（文本或图像），生成嵌入向量
    mode = 'text'：文本项：把 content 向量化；
    mode = 'image'：图片项：向量化图片

    Args:
        item: 原始数据项
        mode: 处理模式（'text'或'image'）
        api_image: 当mode为'image'时使用的图像数据

    Returns:
        Dict: 处理后的数据项，包含嵌入向量
    """
    # 创建原始项的副本以避免修改原数据
    new_item = item.copy()
    # raw_content = (new_item.get('text') or '').strip()
    raw_content = (new_item.get('text') or '').strip()  # 获取文本内容
    image_raw = (new_item.get('image_path') or '').strip()  # 获取原始图像路径


    if image_raw:
        img = normalize_image(image_raw)[0]
        input_data = [{"image": img, "text": raw_content}]
        log.info(f'图片：{image_raw}, 所对应的描述为{raw_content}')
    else:
        input_data = [{"text": raw_content}]

    ok, embedding, status, retry_after = call_dashscope_once(input_data)
    if ok:
        new_item['dense'] = embedding
    else:
        new_item['dense'] = []


    return new_item



if __name__ == "__main__":
    pass
