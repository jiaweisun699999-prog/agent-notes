from langchain import hub

prompt = hub.pull("rlm/rag-prompt")
print(prompt)