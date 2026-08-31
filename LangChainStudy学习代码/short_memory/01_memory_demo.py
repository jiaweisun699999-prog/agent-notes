from langchain.agents import create_agent
from langchain_core.stores import InMemoryStore
from langgraph.checkpoint.memory import InMemorySaver

from init_llm import deepseek_llm


checkpointer=InMemorySaver()

agent = create_agent(
    model=deepseek_llm,
    tools=[],
    checkpointer=checkpointer
)

config = {"configurable":{"thread_id":"session001"}}

resp1 = agent.invoke({"messages":[{"role":"user","content":"你好,我叫张三"}]},config=config)
print(resp1["messages"][-1].content)

print("-----------------")

resp2 = agent.invoke({"messages":[{"role":"user","content":"我叫什么名字？"}]},config=config)
print(resp2["messages"][-1].content)



