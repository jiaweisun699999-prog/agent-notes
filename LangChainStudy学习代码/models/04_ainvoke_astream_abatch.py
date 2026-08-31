"""
异步调用大模型
ainvoke, astream, abatch
"""

import asyncio
import time
from langchain.chat_models import init_chat_model

from env_utils import DEEPSEEK_API_KEY, DEEPSEEK_BASE_URL

# 初始化模型
llm = init_chat_model(
    model="deepseek-chat",
    model_provider="deepseek",
    api_key=DEEPSEEK_API_KEY,
    base_url=DEEPSEEK_BASE_URL,
)


async def demo_async_invoke():
    """演示单个异步调用的非阻塞特性"""
    print("=== 演示：ainvoke 的异步（非阻塞）效果 ===")

    print("程序开始...")

    # 1. 发起一个异步请求，但不等待它完成
    print(">>> 发起异步模型调用 (ainvoke)...")
    async_task = llm.ainvoke("用一句话解释人工智能。")

    # 2. 在等待模型响应的同时，主程序可以继续执行其他任务
    print(">>> 模型请求已发送，程序无需等待，继续执行...")
    for i in range(3):
        # 等待1s
        time.sleep(1)
        print(f">>> 正在执行第{i + 1}个任务... ")

    # 3. 现在，我们需要模型的结果了，所以用 await 等待它完成
    print(">>> 其他任务已完成，现在等待模型返回结果...")
    response = await async_task  # 此时才开始等待

    print(f">>> 模型返回: {response.content}")


async def demo_async_stream():
    """演示异步调用的非阻塞特性"""
    print("=== 演示：astream 的异步（非阻塞）效果 ===")

    print("程序开始...")

    # 1. 发起异步流式请求，但不立即处理结果
    print(">>> 发起异步流式调用 (astream)...")
    stream_resp = llm.astream("请一句话解释机器学习的基本概念。")

    # 2. 在等待流式响应的同时，执行其他任务
    print(">>> 流式请求已发送，程序无需等待，继续执行...")
    for i in range(3):
        # 等待1s
        time.sleep(1)
        print(f">>> 正在执行第{i + 1}个任务... ")

    # 3. 现在开始处理流式结果
    print(">>> 其他任务已完成，开始处理流式结果...")

    print(">>> 流式输出: ", end="", flush=True)
    async for chunk in stream_resp:
        if hasattr(chunk, 'content'):
            print(chunk.content, end="", flush=True)
    print(">>> 流式输出结束\n")

async def demo_async_batch():
    """演示单个异步调用的非阻塞特性"""
    print("=== 演示：abatch 的异步（非阻塞）效果 ===")

    print("程序开始...")

    # 准备批量输入（即使是单个输入，也用列表形式）
    questions = ["用一句话说明深度学习与传统机器学习的区别"]

    # 1. 发起异步批量请求
    print(">>> 发起异步批量调用 (abatch)...")
    batch_resp = llm.abatch(questions)

    # 2. 在等待批量处理的同时，执行其他任务
    print(">>> 批量请求已发送，程序无需等待，继续执行...")
    for i in range(3):
        # 等待1s
        time.sleep(1)
        print(f">>> 正在执行第{i + 1}个任务... ")

    # 3. 等待批量处理结果
    print(">>> 其他任务已完成，现在等待批量处理结果...")
    responses = await batch_resp

    for response in responses:
        print(f">>> 批量响应: {response.content}")

async def main():
    """主函数"""
    await demo_async_invoke()
    await demo_async_stream()
    await demo_async_batch()


if __name__ == "__main__":
    asyncio.run(main())
