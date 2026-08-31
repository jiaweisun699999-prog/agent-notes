import json

from IPython.core.display import HTML
from IPython.core.display_functions import display
from langchain_unstructured import UnstructuredLoader

pdf_file = r'E:\my_project\RAG_PROJECT\datas\layout-parser-paper.pdf'


def write_json(data, file_name):
    with open('E:\\my_project\\RAG_PROJECT\\datas\\output\\' + file_name, 'w', encoding='utf-8') as file:
        json.dump(data, file, ensure_ascii=False, indent=4)


loader = UnstructuredLoader(
    file_path=pdf_file,
    strategy='hi_res',
    partition_via_api=True,  # 调用API接口的话：True
    coordinates=True,
    api_key='IhWKAZRBmZ14c8tmCsOLabqwIKLJ2e'
)

docs = []
counter = 0
for doc in loader.lazy_load():
    docs.append(doc)
    json_file_name = str(doc.metadata.get('page_number')) + '_' + str(counter) + '.json'
    counter += 1
    write_json(doc.model_dump(), json_file_name)

print(f'doc的数量是: {len(docs)}')
print('第一个doc是：')
print(docs[0].metadata)
print(docs[0].page_content)

print('--' * 50)


segments = [
    doc.metadata
    for doc in docs
    if doc.metadata.get("page_number") == 5 and doc.metadata.get("category") == "Table"
]
print(f'表格数据为:')
print(segments)
display(HTML(segments[0]["text_as_html"]))