from langchain_community.document_loaders import PyPDFLoader

pdf_file = r'E:\my_project\RAG_PROJECT\datas\layout-parser-paper.pdf'

# 一页一页的解析，每一页对于一个document对象
loader = PyPDFLoader(file_path=pdf_file)

docs = loader.load()

print(f'doc的数量是: {len(docs)}')
print(docs[0].metadata)
print(docs[0].page_content)