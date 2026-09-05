import json
import os
import random
import time
from typing import List, Dict

from langchain_core.documents import Document
from langchain_core.messages import HumanMessage
from pymilvus import MilvusException

from milvus_db.collections_operator import client, COLLECTION_NAME
from my_llm import multiModal_llm
from utils.common_utils import get_surrounding_text_content
from utils.embeddings_utils import  limiter, RETRY_ON_429, process_item_with_guard, MAX_429_RETRIES, \
    BASE_BACKOFF, image_to_base64
from utils.log_utils import log


def doc_to_dict(docs: List[Document]) -> List[Dict]:
    """
        将 Document 对象列表转换为指定格式的字典列表。

        参数:
            doc_list: 包含 Document 对象的列表

        返回:
            list: 包含转换后字典的列表
        """
    result_list = []

    for doc in docs:
        # 初始化一个空字典来存储当前文档的信息
        doc_dict = {}
        metadata = doc.metadata

        # 1. 提取 text (仅当 embedding_type 为 'text' 时)
        if metadata.get('embedding_type') == 'text':
            doc_dict['text'] = doc.page_content
        else:
            doc_dict['text'] = None  # 或者设置为空字符串 ''，根据需要调整

        # 2. 提取 category (embedding_type)
        doc_dict['category'] = metadata.get('embedding_type', '')

        # 3. 提取 filename (source)
        source = metadata.get('source', '')
        doc_dict['filename'] = source

        # 4. 提取 filetype (source 中文件名的后缀)
        _, file_extension = os.path.splitext(source)
        doc_dict['filetype'] = file_extension.lower()  # 转换为小写，如 '.jpg'

        # 5. 提取 image_path (仅当 embedding_type 为 'image' 时)
        if metadata.get('embedding_type') == 'image':
            doc_dict['image_path'] = doc.page_content
        else:
            doc_dict['image_path'] = None  # 或者设置为空字符串 ''，根据需要调整

        # 6. 提取 title (拼接所有 Header 层级)
        headers = []
        # 假设 Header 的键可能为 'Header 1', 'Header 2', 'Header 3' 等，我们按层级顺序拼接
        # 我们需要先收集所有存在的 Header 键，并按层级排序
        header_keys = [key for key in metadata.keys() if key.startswith('Header')]
        # 按 Header 后的数字排序，确保层级顺序
        header_keys_sorted = sorted(header_keys, key=lambda x: int(x.split()[1]) if x.split()[1].isdigit() else x)

        for key in header_keys_sorted:
            value = metadata.get(key, '').strip()
            if value:  # 只添加非空的 Header 值
                headers.append(value)

        # 将所有非空的 Header 值用连字符或空格连接起来
        doc_dict['title'] = ' --> '.join(headers) if headers else ''  # 你也可以用其他连接符，如空格
        if not doc_dict['image_path']:
            doc_dict['text'] = doc_dict['title'] + ' ：' + doc_dict['text']
        # 将当前文档的字典添加到结果列表中
        result_list.append(doc_dict)

    return result_list


def write_to_milvus(processed_data: List[Dict]):
    """
    把数据写入到Milvus中
    :param processed_data:
    :return:
    """
    if not processed_data:
        print("[Milvus] 没有可写入的数据。")
        return
    try:
        insert_result = client.insert(collection_name=COLLECTION_NAME, data=processed_data)
        print(f"[Milvus] 成功插入 {insert_result['insert_count']} 条记录。IDs 示例: {insert_result['ids'][:5]}")
    except MilvusException as e:
        print(f"[Milvus] 插入失败: {e}")
        log.exception(e)


def generate_image_description(data_list):
    """
    处理文档数据，为每个图片字典生成多模态描述

    参数:
        data_list: 包含字典的列表

    返回:
        包含完整结果的新列表
    """
    results = []

    for index, item in enumerate(data_list):
        if item.get('image_path'):  # 检查是否为图片字典
            # 获取前后文本内容
            prev_text, next_text = get_surrounding_text_content(data_list, index)

            # 将图片转换为base64
            image_data = image_to_base64(item['image_path'])[0]

            # 构建提示词模板
            context_prompt = ""
            if prev_text and next_text:
                context_prompt = f"""
                前文内容: {prev_text}
                后文内容: {next_text}

                请根据以上上下文和图片内容，生成对该图片的简洁描述，描述内容长度最好不超过300个汉字。
                注意：图片可能与前文、后文或两者都相关，请综合分析。
                """
            elif prev_text:
                context_prompt = f"""
                前文内容: {prev_text}

                请根据以上上下文和图片内容，生成对该图片的简洁描述，描述内容长度最好不超过300个汉字。
                注意：图片可能与前文内容相关，请结合分析。
                """
            elif next_text:
                context_prompt = f"""
                后文内容: {next_text}

                请根据以上上下文和图片内容，生成对该图片的简洁描述，描述内容长度最好不超过300个汉字。
                注意：图片可能与后文内容相关，请结合分析。
                """
            else:
                context_prompt = "请描述这张图片的内容，生成对该图片的简洁描述，描述内容长度最好不超过300个汉字。"

            # 构建多模态消息
            message = HumanMessage(
                content=[
                    {"type": "text", "text": context_prompt},
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"{image_data}"
                        }
                    }
                ]
            )

            # 调用模型生成描述
            response = multiModal_llm.invoke([message])
            item['text'] = response.content
    return data_list


def do_save_to_milvus(processed_data: List[Document]):
    """
    第一步：
    把Splitter之后的的数据（document对象列表），先转换为字典；
    第二步：
    把字典中的文本 和图片 ，进行向量化，然后再存入字典。
    第三步：
    最后写入向量数据库
    :param processed_data:
    :return:
    """
    # 第一步
    expanded_data = generate_image_description(doc_to_dict(processed_data))
    processed_data: List[Dict] = []
    # 处理每个 item
    for idx, item in enumerate(expanded_data, 1):
        # 限速控制
        limiter.acquire()

        # 处理 + 可选 429 重试
        if RETRY_ON_429:
            attempts = 0
            while True:
                # 包装版处理
                result = process_item_with_guard(item.copy())
                # 检查是否成功
                if result.get("dense"):
                    processed_data.append(result)
                    break
                attempts += 1
                if attempts > MAX_429_RETRIES:
                    print(f"[429重试] 超过最大重试次数，跳过 idx={idx}")
                    processed_data.append(result)
                    break
                backoff = BASE_BACKOFF * (2 ** (attempts - 1)) * (0.8 + random.random() * 0.4)
                print(f"[429重试] 第{attempts}次，sleep {backoff:.2f}s …")
                time.sleep(backoff)
        else:
            # 若关闭 429 重试，这里同样使用包装版
            processed_data.append(process_item_with_guard(item.copy()))

        # 进度打印
        if idx % 20 == 0:
            print(f"[进度] 已处理 {idx}/{len(expanded_data)}")

    # 打印处理后的 item 内容
    for item in processed_data:
        print(json.dumps(item, ensure_ascii=False, indent=4))



    write_to_milvus(processed_data)
    return processed_data