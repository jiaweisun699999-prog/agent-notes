"""
智能购物助手:交互式命令行客户端
通过 LangGraph SDK 远程调用 langgraph dev 服务
"""
import asyncio
import uuid

from langchain_core.messages import HumanMessage
from langgraph_sdk import get_client

client = get_client(url="http://127.0.0.1:2024")


async def main():
    # 输入业务 ID
    raw = input("请输入用户ID (如 user_001，回车默认为user_001): ").strip()
    user_id = raw if raw else "user_001"

    # 首次启动如果用户输入thread_id 就用用户的thread_id 否则自动创建一个thread_id
    current_thread_id = "435973d3-40f0-49d1-8bb4-1fb2574d55ca"

    if len(current_thread_id.strip()) != 36:
        # 如果用户没有输入thread_id 则自动创建一个thread_id
        current_thread_id = str(uuid.uuid4())

    # 在服务端注册这个 thread_id
    # if_exists="do_nothing"：已存在则复用（恢复 Checkpointer 保存的上下文），不存在则新建
    await client.threads.create(thread_id=current_thread_id, if_exists="do_nothing")

    print(f"用户: {user_id} | thread: {current_thread_id}...")

    while True:
        try:
            user_input = input("[用户]: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\n再见！")
            break

        if not user_input:
            continue

        print("处理中...\n\n")
        try:
            result = await client.runs.wait(
                current_thread_id,
                "langgraph_store",    # 对应 langgraph.json 中 graphs 的 key
                input={
                    "messages": [HumanMessage(content=user_input)],
                    "user_profile": "",
                },
                context={"user_id": user_id},
            )

            print("result:",result)
            # messages 中的 Message 对象经过 HTTP 传输时被序列化为 dict，取 content 字段需要用 ["content"]
            print(f"回复: {result['messages'][-1]["content"]}")

            print("=" * 100)
            # 读取 Store 中长期记忆
            resp = await client.store.search_items(
                (user_id, "profile"), limit=10
            )
            print("resp:",resp)
            store_items = resp["items"]
            print("Store 中长期记忆:")
            for item in store_items:
                print(f"  [{item['key']}] {item['value']}")
            print("=" * 100)


        except Exception as e:
            print(f"请求失败: {e}\n")


if __name__ == "__main__":
    asyncio.run(main())

