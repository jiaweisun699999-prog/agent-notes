from langchain_core.messages import AIMessage, HumanMessage
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.constants import START, END
from langgraph.graph import MessagesState, StateGraph


#定义节点
def my_node(state:MessagesState):
    return {"messages":[AIMessage(content="处理成功")]}

# 构建Graph图
builder = StateGraph(MessagesState)

builder.add_node("my_node",my_node)
builder.add_edge(START,"my_node")
builder.add_edge("my_node",END)

graph = builder.compile(checkpointer=InMemorySaver())


if __name__ == '__main__':

    # ====================exit 模式
    config_exit = {"configurable":{"thread_id":"threadid_exit"}}

    graph.invoke(
        {"messages":[HumanMessage(content="测试")]},
        config=config_exit,
        durability="exit"
    )

    exit_history = graph.get_state_history(config_exit)

    for s in exit_history:
        print(f" step={s.metadata['step']},next={s.next}")


    print("="*100)
    # ==================== async 模式
    config_async = {"configurable": {"thread_id": "threadid_async"}}

    graph.invoke(
        {"messages": [HumanMessage(content="测试")]},
        config=config_async,
        durability="async"
    )

    async_history = graph.get_state_history(config_async)

    for s in async_history:
        print(f" step={s.metadata['step']},next={s.next}")

    print("=" * 100)
    # ==================== sync 模式
    config_sync = {"configurable": {"thread_id": "threadid_sync"}}

    graph.invoke(
        {"messages": [HumanMessage(content="测试")]},
        config=config_sync,
        durability="sync"
    )

    sync_history = graph.get_state_history(config_sync)

    for s in sync_history:
        print(f" step={s.metadata['step']},next={s.next}")

