from langgraph_sdk import get_sync_client

from langgraph_sdk import get_client
import asyncio

async def main():
    client = get_client(url="http://127.0.0.1:2024")

    async for chunk in client.runs.stream(
        None, "my_graph",
        input={
            "messages": [{"role": "user", "content": "100除以4再乘以3等于多少?"}]
        },
    ):
        print(f"事件: {chunk.event}")
        print(chunk.data)

asyncio.run(main())



# client = get_sync_client(url="http://127.0.0.1:2024")
#
# for chunk in client.runs.stream(
#     None,       # thread_id=None → 无状态运行，每次调用独立
#     "my_graph",    # 对应 langgraph.json 中的 graph 名称
#     input={
#         "messages": [{"role": "user", "content": "请帮我算一下：(3+5)*2 是多少？"}]
#     },
# ):
#     # chunk 是每个步骤的事件，包含 event 类型和 data 数据
#     print(f"事件: {chunk.event}")
#     print(f"数据: {chunk.data}")