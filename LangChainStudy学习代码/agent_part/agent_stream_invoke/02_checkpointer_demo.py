from langchain.agents import create_agent
from langchain.tools import tool
from langchain_core.stores import InMemoryStore
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph.state import CompiledStateGraph

from init_llm import deepseek_llm

agent = create_agent(
    model=deepseek_llm,
    tools=[],
    checkpointer=InMemorySaver(),
    store=InMemoryStore()
)

config1 = {"configurable": {"thread_id": "session_001"}}
config2 = {"configurable": {"thread_id": "session_002"}}

resp1 = agent.invoke( {"messages": [{"role": "user", "content": "我叫张三，你是谁？"}]}, config=config1)
print(resp1["messages"][-1].content)

print("+++++"*30)
resp2 = agent.invoke( {"messages": [{"role": "user", "content": "我叫什么名字？"}]}, config=config2)
print(resp2["messages"][-1].content)
