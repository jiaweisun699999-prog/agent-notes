from typing import List, Dict

from ragas import SingleTurnSample
from ragas.embeddings import LangchainEmbeddingsWrapper
from ragas.llms import LangchainLLMWrapper
from ragas.metrics import LLMContextPrecisionWithReference, LLMContextPrecisionWithoutReference, ResponseRelevancy, \
    ContextRelevance

from milvus_db.collections_operator import COLLECTION_NAME, client
from milvus_db.db_retriever import MilvusRetriever
from my_llm import llm, embedding
from utils.log_utils import log


def generate_answer(question: str, contexts: List[Dict]) -> str:
    """
    使用LLM基于检索到的上下文生成文本答案

    Args:
        question: 用户问题 (中文)
        contexts: 检索到的上下文列表 (包含text、category等字段)

    Returns:
        生成的中文答案
    """
    # 将检索到的上下文格式化为字符串，便于LLM理解
    # 每个上下文前加上"上下文X"标识，方便LLM区分
    context_str = "\n\n".join([f"上下文 {i + 1}: {context['text']}" for i, context in enumerate(contexts)])

    # 提示词模板 (已翻译成中文)
    prompt = f"""
你是一个AI助手，需要根据提供的上下文回答用户的问题。请确保你的回答基于提供的上下文，不要添加额外信息。

用户问题: {question}

检索到的上下文:
{context_str}

请基于以上上下文回答用户问题。
"""

    # 调用LLM生成答案
    response = llm.invoke(prompt)
    return response.content


class RAGEvaluator:
    """
    RAG的评估类
    """

    def __init__(self, evaluator_llm, evaluator_embeddings):
        self.evaluator_llm = evaluator_llm  # 推理模型
        self.evaluator_embeddings = evaluator_embeddings  # 嵌入模型

    ''' 修改的代码'''
    # 10月18日的代码基础上，修改了一下。
    async def evaluate_context(self, question: str, contexts: List[str]) -> float:
        """上下文相关性评估: 检索到的上下文（块或段落）是否与用户输入相关。"""
        # 0 → 检索到的上下文与用户查询完全不相关。
        # 1 → 上下文部分相关。
        # 2 → 上下文完全相关。
        # SingleTurnSample用于表示单轮对话的评估样本
        sample = SingleTurnSample(
            user_input=question,  # 用户输入的问题
            retrieved_contexts=contexts,  # 检索到的上下文
        )
        scorer = ContextRelevance(llm=self.evaluator_llm)
        return await scorer.single_turn_ascore(sample)


    async def evaluate_answer(self, question: str, contexts: List[Dict], response: str) -> float:
        """评估生成的答案质量"""
        # SingleTurnSample用于表示单轮对话的评估样本
        sample = SingleTurnSample(
            user_input=question,  # 用户输入的问题
            retrieved_contexts=[context['text'] for context in contexts],  # 检索到的上下文
            response=response,  # 生成的答案
        )
        log.info(f"开始评估答案质量, 评估样本为：{sample}")
        scorer = ResponseRelevancy(llm=self.evaluator_llm, embeddings=self.evaluator_embeddings)
        return await scorer.single_turn_ascore(sample)

    async def evaluate_metrics(self, question: str, contexts: List[Dict], response: str, reference: str=None):
        """
        评估RAG模型

        Args:
            question: 用户问题
            contexts: 检索到的上下文列表
            response: LLM生成的答案
            reference: 可选，参考答案 (用于评估的基准答案，通常为已知的正确答案)
        """
        # 1. 创建评估样本 (SingleTurnSample)
        sample = SingleTurnSample(
            user_input=question,  # 用户输入的问题
            retrieved_contexts=[context['text'] for context in contexts],  # 检索到的上下文
            response=response,  # 生成的答案
            reference=reference  # 参考答案 (用于需要参考答案的指标)
        )

        # 2. 初始化评估指标
        if reference:
            # 如果有参考答案，则初始化指标为LLMContextPrecisionWithReference
            context_precision = LLMContextPrecisionWithReference(llm=self.evaluator_llm)
        else:
            # 如果没有参考答案，则初始化指标为LLMContextPrecisionWithoutReference
            context_precision = LLMContextPrecisionWithoutReference(llm=self.evaluator_llm)

        # 3、执行评估指标得到结果
        context_precision_score = await context_precision.single_turn_ascore(sample)
        print(f"上下文精确度指标的 Score: {context_precision_score}")


async def main():
    evaluator_llm = LangchainLLMWrapper(llm)
    evaluator_embeddings = LangchainEmbeddingsWrapper(embedding)

    # 创建RAG评估器
    rag_evaluator = RAGEvaluator(evaluator_llm, evaluator_embeddings)

    question = "有界流和无界流有什么区别？"
    # 检索上下文 (从您的Milvus知识库获取)
    m_re = MilvusRetriever(COLLECTION_NAME, client)
    contexts = m_re.retrieve(question)

    generated_answer = generate_answer(question, contexts)
    print(f"生成的答案: {generated_answer}")

    await rag_evaluator.evaluate_metrics(question, contexts, generated_answer)


if __name__ == '__main__':
    import asyncio
    asyncio.run(main())