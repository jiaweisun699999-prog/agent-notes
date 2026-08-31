
def draw_graph(graph, file_name: str):

    mermaid_code = graph.get_graph().draw_mermaid_png()
    with open(file_name, "wb") as f:
        f.write(mermaid_code)

