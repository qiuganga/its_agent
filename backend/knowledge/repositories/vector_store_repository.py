# 1. 优先 import
import logging
from typing import List

# 2. from 三方的
from langchain_chroma import Chroma
from langchain_core.documents import Document
from langchain_openai.embeddings import OpenAIEmbeddings

# 3. from 自己的
from config.settings import settings


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class VectorStoreRepository:
    """
    作用：对向量数据库做场景读写
    """

    def __init__(self):
        """
        创建向量数据库实例
        创建嵌入模型的实例

        向量数据库能力:
        1. 存储向量数据
        2. 搜索能力，也就是向量数据库检索器
        """
        self.embedding = OpenAIEmbeddings(
            model=settings.EMBEDDING_MODEL,
            openai_api_key=settings.API_KEY,
            openai_api_base=settings.BASE_URL
        )

        self.vector_database = Chroma(
            persist_directory=settings.VECTOR_STORE_PATH,
            collection_name="its-knowledge",
            embedding_function=self.embedding
        )

    def add_documents(self, documents: list, batch_size: int = 16) -> int:
        """
        将切分之后的文档块保存到向量数据库中

        Args:
            documents: 切分之后的文档块
            batch_size: 分批保存文档块的批次大小

        Returns:
            int: 成功添加到向量数据库中文档块的数量
        """

        total_documents_chunks = len(documents)
        documents_chunks_added = 0

        try:
            for i in range(0, total_documents_chunks, batch_size):
                batch = documents[i:i + batch_size]

                self.vector_database.add_documents(batch)

                documents_chunks_added += len(batch)

                logger.info(
                    f"成功将文档块:{documents_chunks_added}/{total_documents_chunks}保存到向量数据库..."
                )

            return documents_chunks_added

        except Exception as e:
            logger.error(f"文档块列表:{documents}保存到向量数据库失败: {str(e)}")
            raise e

    def embedd_document(self, text: str) -> List[float]:
        """
        对 query 进行向量化

        Args:
            text: 输入文本

        Returns:
            List[float]: 嵌入后的浮点数列表
        """
        return self.embedding.embed_query(text)

    def embedd_documents(self, texts: List[str]) -> List[List[float]]:
        """
        对字符串列表进行向量化

        Args:
            texts: 输入文本字符串列表

        Returns:
            List[List[float]]: 嵌入后的多个文本的浮点数列表
        """
        return self.embedding.embed_documents(texts)

    def search_similarity_with_score(
        self,
        user_question: str,
        top_k: int = 5
    ) -> List[tuple[Document, float]]:
        """
        相似性检索，返回文档和分数。

        注意：
        Chroma 返回的是距离分数，通常值越小越相似。

        Args:
            user_question: 用户问题
            top_k: 返回最相似的文档数量

        Returns:
            List[tuple[Document, float]]: 文档和相似度/距离分数
        """
        return self.vector_database.similarity_search_with_score(user_question, top_k)