import os

from dotenv import load_dotenv

load_dotenv(override=True)

OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
DEEPSEEK_API_KEY = os.getenv('DEEPSEEK_API_KEY')

MILVUS_URI = 'http://1.95.116.112:19530'

COLLECTION_NAME = 't_collection01'
