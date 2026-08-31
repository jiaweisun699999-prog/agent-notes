"""
客服路由系统 —— 交互式命令行客户端
"""
import asyncio
import uuid

from langgraph_sdk import get_client

client = get_client(url="http://127.0.0.1:2024")


async def main():
    # 首次启动如果用户输入thread_id 就用用户的thread_id 否则自动创建一个thread_id
    current_thread_id = "b1897645-4b96-46c4-a0ec-c94aba84a641"

    if len(current_thread_id.strip()) != 36:
        # 如果用户没有输入thread_id 则自动创建一个thread_id
        current_thread_id = str(uuid.uuid4())

    # 在服务端注册这个 thread_id
    # if_exists="do_nothing"：已存在则复用（恢复 Checkpointer 保存的上下文），不存在则新建
    await client.threads.create(thread_id=current_thread_id, if_exists="do_nothing")

    print(f"当前thread_id: {current_thread_id}")

    while True:
        try:
            user_input = input("[用户]: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\n 【输出错误，再见！】\n")
            break

        if not user_input:
            continue

        print("处理中...\n\n")

        try:
            result = await client.runs.wait(
                current_thread_id,
                "langgraph_checkpoint",
                input={
                    "messages": [{"role": "user", "content": user_input}],
                    "user_input": user_input,
                    "intent": "",
                    "department": "",
                    "response": "",
                },
            )

            print(f"对话内容：{user_input}; 意图: {result['intent']} ;部门: {result['department']}")
            print(f"回复: {result['response']}")
            print("result:", result)

        except Exception as e:
            print(f"请求失败: {e}")


if __name__ == "__main__":
    asyncio.run(main())

