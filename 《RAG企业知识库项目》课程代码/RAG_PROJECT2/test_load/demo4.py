from langchain_community.document_loaders import UnstructuredMarkdownLoader

loader = UnstructuredMarkdownLoader(
    file_path=r'E:\my_project\RAG_PROJECT\datas\md\operational_faq.md',
    mode='elements',
    strategy='fast'
)

docs = loader.load()
print(f'doc的数量是: {len(docs)}')

for i in range(10):

    print(docs[i].metadata)
    print(docs[i].page_content)

    print('--' * 50)