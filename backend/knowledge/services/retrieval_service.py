import logging
import jieba
import re

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

from typing import List, Dict, Any
from langchain_core.documents import Document
from repositories.vector_store_repository import VectorStoreRepository
from services.ingestion.ingestion_processor import IngestionProcessor
from utils.markdown_utils import MarkDownUtils
from config.settings import settings
from sklearn.metrics.pairwise import cosine_similarity


class RetrievalService:
    """
    负责检索的类（检索器）

    当前检索逻辑：
    1. 第一路：基于 Chroma 向量数据库的语义检索
    2. 第二路：基于 Markdown 标题的关键词 + 向量精排检索
    3. 合并两路候选
    4. 去重
    5. 重新打分排序
    6. 返回最终 Top-N 文档
    """

    def __init__(self):
        self.chroma_vector = VectorStoreRepository()
        self.spliter = IngestionProcessor()

    def rough_ranking(self, user_query, mds_metadata: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        对标题进行粗排。
        基于字符重合度 + jieba 分词重合度计算标题粗排分数。

        Args:
            user_query: 用户的问题
            mds_metadata: 所有 md 的元数据，包含 title 和 path

        Returns:
            List[Dict[str, Any]]: 带 roughing_score 的 md 元数据列表
        """

        if not user_query:
            return []

        ROUGHIN_WORD_WEIGHT = 0.7

        valid_mds_metadata = []

        for md_metadata in mds_metadata:
            md_metadata_title = md_metadata.get("title", "")

            if not md_metadata_title or not md_metadata_title.strip():
                continue

            # 字符级 Jaccard 相似度
            user_query_char = set(user_query)
            md_metadata_title_char = set(md_metadata_title)

            unique_char = user_query_char | md_metadata_title_char
            char_score = (
                len(user_query_char & md_metadata_title_char) / len(unique_char)
                if len(unique_char) > 0
                else 0
            )

            # 词级 Jaccard 相似度
            user_query_word = set(jieba.lcut(user_query))
            md_metadata_title_word = set(jieba.lcut(md_metadata_title))

            unique_word = user_query_word | md_metadata_title_word
            word_score = (
                len(user_query_word & md_metadata_title_word) / len(unique_word)
                if len(unique_word) > 0
                else 0
            )

            # 粗排分数：词级 70%，字符级 30%
            roughing_score = (
                word_score * ROUGHIN_WORD_WEIGHT
                + char_score * (1 - ROUGHIN_WORD_WEIGHT)
            )

            md_metadata["roughing_score"] = float(roughing_score)
            valid_mds_metadata.append(md_metadata)

        return sorted(
            valid_mds_metadata,
            key=lambda x: x.get("roughing_score", 0),
            reverse=True
        )[:50]

    def fine_ranking(self, user_query: str, rough_mds_metadata: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        对标题进行精排。
        使用 embedding 模型把用户问题和标题都转成向量，再通过 cosine_similarity 计算语义相似度。

        Args:
            user_query: 用户当前问题
            rough_mds_metadata: 粗排后的 md 元数据

        Returns:
            List[Dict[str, Any]]: 带 sim_score 和 final_score 的元数据
        """

        if not rough_mds_metadata:
            return []

        # 1. 用户问题向量化
        query_embedding = self.chroma_vector.embedd_document(user_query)

        # 2. 取出粗排后的标题
        roughing_title = [
            md_metadata.get("title", "")
            for md_metadata in rough_mds_metadata
            if md_metadata.get("title", "").strip()
        ]

        if not roughing_title:
            return []

        # 3. 标题批量向量化
        roughing_title_embeddings = self.chroma_vector.embedd_documents(roughing_title)

        # 4. 计算用户问题和标题的余弦相似度
        similarity = cosine_similarity(
            [query_embedding],
            roughing_title_embeddings
        ).flatten()

        ROUGH_WEIGHT = 0.3
        SIM_WEIGHT = 0.7

        valid_results = []

        for index, md_metadata in enumerate(rough_mds_metadata):
            if index >= len(similarity):
                break

            sim = similarity[index]

            if sim < 0:
                sim = 0

            roughing_score = md_metadata.get("roughing_score", 0)

            final_score = roughing_score * ROUGH_WEIGHT + sim * SIM_WEIGHT

            md_metadata["sim_score"] = float(sim)
            md_metadata["final_score"] = float(final_score)

            valid_results.append(md_metadata)

        return sorted(
            valid_results,
            key=lambda x: x.get("final_score", 0),
            reverse=True
        )[:5]

    def retrieval(self, user_question: str) -> List[Document]:
        """
        核心检索方法。

        Args:
            user_question: 用户输入的问题

        Returns:
            List[Document]: 返回最终 Top-N 个相似文档
        """

        # 1. 第一路：向量检索
        based_vector_candidates = self._search_based_vector(user_question)

        # 2. 第二路：标题关键词检索 + 标题语义精排
        based_title_candidates = self._search_based_title(user_question)

        # 3. 合并两路候选
        total_candidates = based_vector_candidates + based_title_candidates

        # 4. 去重
        unique_candidates = self._deduplicate(total_candidates)

        # 5. 重新打分排序
        top_documents = self._reranking(unique_candidates, user_question)

        return top_documents

    def _search_based_vector(self, user_question: str) -> List[Document]:
        """
        第一路检索：基于 Chroma 向量数据库的语义相似度检索。

        Args:
            user_question: 用户输入的问题

        Returns:
            List[Document]: 候选文档列表
        """

        documents_with_score = self.chroma_vector.search_similarity_with_score(user_question)

        based_vector_candidates = []

        for document, _ in documents_with_score:
            if self._is_valid_document(document):
                based_vector_candidates.append(document)

        return based_vector_candidates

    def _search_based_title(self, user_query: str) -> List[Document]:
        """
        第二路检索：基于 Markdown 标题的关键词匹配和语义精排。

        Args:
            user_query: 用户输入的问题

        Returns:
            List[Document]: 候选文档列表
        """

        # 1. 获取 crawl 目录下所有 md 文件的标题和路径
        mds_metadata = MarkDownUtils.collect_md_metadata(settings.CRAWL_OUTPUT_DIR)

        # 2. 标题粗排
        rough_mds_metadata = self.rough_ranking(user_query, mds_metadata)

        # 3. 标题精排
        fine_mds_metadata = self.fine_ranking(user_query, rough_mds_metadata)

        based_title_candidates = []

        for fine_md_metadata in fine_mds_metadata:
            try:
                file_path = fine_md_metadata.get("path", "")

                if not file_path:
                    continue

                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read().strip()

                if not content:
                    continue

                # 短文档：不切分，直接封装成 Document
                if len(content) < 3000:
                    doc = Document(
                        page_content=content,
                        metadata={
                            "path": fine_md_metadata.get("path", ""),
                            "title": fine_md_metadata.get("title", ""),
                        }
                    )

                    if self._is_valid_document(doc):
                        based_title_candidates.append(doc)

                # 长文档：切分后选出最相关 chunk
                else:
                    doc_chunks = self._deal_long_title_content(
                        content,
                        fine_md_metadata,
                        user_query
                    )

                    for doc in doc_chunks:
                        if self._is_valid_document(doc):
                            based_title_candidates.append(doc)

            except Exception as e:
                logger.error(f"打开文件失败: {e}")
                continue

        return based_title_candidates

    def _deduplicate(self, total_candidates: List[Document]) -> List[Document]:
        """
        对合并后的文档列表去重。
        去重依据：标题 + 清理后正文前 100 个字符。

        Args:
            total_candidates: 合并后的候选文档列表

        Returns:
            List[Document]: 去重后的文档列表
        """

        if not total_candidates:
            return []

        seen = set()
        unique_candidates = []

        for document in total_candidates:
            if not self._is_valid_document(document):
                continue

            clean_content = self._clean_content_for_compare(document.page_content)
            title = document.metadata.get("title", "")

            key = (title, clean_content[:100])

            if key not in seen:
                seen.add(key)
                unique_candidates.append(document)

        return unique_candidates

    def _reranking(self, unique_candidates: List[Document], user_question: str) -> List[Document]:
        """
        对去重后的候选文档重新计算分数并排序。

        说明：
        1. 长文档 chunk 如果已经在 _deal_long_title_content 中算过 similarity，就直接使用原分数。
        2. 其他文档重新计算 embedding 相似度。
        3. 最后统一按分数排序，返回 Top-N。

        Args:
            unique_candidates: 唯一候选文档列表
            user_question: 用户问题

        Returns:
            List[Document]: 最终 Top-N 文档
        """

        if not unique_candidates:
            return []

        # 兜底过滤无效候选
        unique_candidates = [
            doc for doc in unique_candidates
            if self._is_valid_document(doc)
        ]

        if not unique_candidates:
            return []

        need_embedding_docs = []
        need_embedding_candidates_indices = []
        score_doc = []

        for candidate_index, unique_candidate in enumerate(unique_candidates):
            # 长文档 chunk 已经有 similarity，直接使用
            if (
                "chunk_index" in unique_candidate.metadata
                and "similarity" in unique_candidate.metadata
            ):
                score_doc.append(
                    (
                        unique_candidate,
                        float(unique_candidate.metadata.get("similarity", 0))
                    )
                )
            else:
                need_embedding_docs.append(unique_candidate)
                need_embedding_candidates_indices.append(candidate_index)

        # 对没有分数的文档重新计算分数
        if need_embedding_docs:
            query_embedding = self.chroma_vector.embedd_document(user_question)

            embedding_docs_content = [
                f"文档来源:{doc.metadata.get('title', '')}\n{doc.page_content}"
                for doc in need_embedding_docs
            ]

            doc_embeddings = self.chroma_vector.embedd_documents(embedding_docs_content)

            similarity = cosine_similarity(
                [query_embedding],
                doc_embeddings
            ).flatten()

            for idx, candidate_index in enumerate(need_embedding_candidates_indices):
                score = float(similarity[idx])

                if score < 0:
                    score = 0

                score_doc.append(
                    (
                        unique_candidates[candidate_index],
                        score
                    )
                )

        sorted_docs = sorted(
            score_doc,
            key=lambda x: x[1],
            reverse=True
        )

        # 返回 Top 2
        return [doc for doc, _ in sorted_docs[:2]]

    def _deal_long_title_content(
        self,
        content: str,
        fine_md_metadata: Dict[str, Any],
        user_query: str
    ) -> List[Document]:
        """
        处理标题对应的长文本。
        对长文本切分后，计算每个 chunk 和用户问题的相似度，返回最相关的 3 个 chunk。

        Args:
            content: 长文本内容
            fine_md_metadata: 长文本对应的元数据
            user_query: 用户问题

        Returns:
            List[Document]: 和问题最相似的文档块列表
        """

        # 1. 长文本切分
        chunks = self.spliter.document_spliter.split_text(content)

        # 2. 过滤无效 chunk
        valid_chunks = []

        for chunk in chunks:
            clean_chunk = chunk.strip()

            if not clean_chunk:
                continue

            # 去掉 HTML 注释后再判断内容有效性
            clean_without_comment = re.sub(
                r"<!--.*?-->",
                "",
                clean_chunk,
                flags=re.DOTALL
            ).strip()

            lines = [
                line.strip()
                for line in clean_without_comment.splitlines()
                if line.strip()
            ]

            if not lines:
                continue

            # 过滤只有一个 Markdown 标题的 chunk，比如：## 解决方案
            if len(lines) == 1 and lines[0].startswith("#"):
                continue

            # 过滤太短的 chunk
            if len(clean_without_comment) < 50:
                continue

            valid_chunks.append(clean_chunk)

        chunks = valid_chunks

        if not chunks:
            return []

        # 3. 获取标题
        doc_chunks_title = fine_md_metadata.get("title", "")

        # 4. 标题注入
        doc_chunks_inject_title = [
            f"文档来源:{doc_chunks_title}\n{doc_chunk}"
            for doc_chunk in chunks
        ]

        # 5. 用户问题向量化
        query_embedding = self.chroma_vector.embedd_document(user_query)

        # 6. 文档 chunk 向量化
        doc_chunk_embeddings = self.chroma_vector.embedd_documents(doc_chunks_inject_title)

        # 7. 计算每个 chunk 和用户问题的相似度
        doc_chunks_similarity = cosine_similarity(
            [query_embedding],
            doc_chunk_embeddings
        ).flatten()

        # 8. 取相似度最高的 3 个 chunk 下标
        top_doc_chunks_indices = doc_chunks_similarity.argsort()[-3:][::-1]

        docs = []

        for rank, chunk_idx in enumerate(top_doc_chunks_indices):
            doc = Document(
                page_content=doc_chunks_inject_title[chunk_idx],
                metadata={
                    "path": fine_md_metadata.get("path", ""),
                    "title": fine_md_metadata.get("title", ""),
                    "chunk_index": int(chunk_idx),
                    "rank": int(rank + 1),
                    "similarity": float(doc_chunks_similarity[chunk_idx])
                }
            )

            if self._is_valid_document(doc):
                docs.append(doc)

        return docs

    def _clean_content_for_compare(self, content: str) -> str:
        if not content:
            return ""

        clean_content = content.strip()

        # 去掉开头的文档来源
        clean_content = re.sub(
            r"^文档来源:.*?(\n|$)",
            "",
            clean_content,
            flags=re.DOTALL
        ).strip()

        # 去掉 HTML 注释
        clean_content = re.sub(
            r"<!--.*?-->",
            "",
            clean_content,
            flags=re.DOTALL
        ).strip()

        # 去掉相关阅读这一类单行链接
        clean_content = re.sub(
            r"^\*\*相关阅读.*?$",
            "",
            clean_content,
            flags=re.MULTILINE
        ).strip()

        return clean_content
    def _is_valid_document(self, document: Document) -> bool:
        """
        判断候选文档是否有有效正文内容。

        过滤以下情况：
        1. 空文档
        2. 只有文档来源
        3. 只有 Markdown 标题，比如 ## 解决方案
        4. 只有 HTML 注释
        5. 内容太短，没有实际参考价值

        Args:
            document: LangChain Document 对象

        Returns:
            bool: 是否为有效文档
        """

        if not document or not document.page_content:
            return False

        clean_content = self._clean_content_for_compare(document.page_content)

        if not clean_content:
            return False

        lines = [
            line.strip()
            for line in clean_content.splitlines()
            if line.strip()
        ]

        if not lines:
            return False

        # 如果只剩一行，而且是 Markdown 标题，比如 ## 解决方案
        if len(lines) == 1 and lines[0].startswith("#"):
            return False

        plain_text = "\n".join(lines)

        # 去掉 Markdown 链接，只保留链接文字
        plain_text_no_link = re.sub(r'\[([^\]]+)\]\([^)]+\)', r'\1', plain_text)

        # 去掉常见无效提示词
        invalid_markers = [
            "相关阅读",
            "文档主题",
        ]

        # 如果内容主要是相关阅读/注释类内容，过滤
        if any(marker in plain_text_no_link for marker in invalid_markers) and len(plain_text_no_link) < 120:
            return False

        # 必须有一定长度的有效正文
        if len(plain_text_no_link) < 80:
            return False

        return True

if __name__ == "__main__":
    retrival_service = RetrievalService()
    # result = retrival_service.retrieval("我的电脑开机之后没有任何的反应")
    # result = retrival_service.retrieval("如何安装联想的一件影音")
    # result = retrival_service.retrieval("联想手机K900常见问题汇总有哪些")
    # result = retrival_service.retrieval("如何使用U盘安装Windows7操作系统.")
    result = retrival_service.retrieval("开机屏幕黑屏或蓝屏报错,无法正常进入系统怎么办")
    # result = retrival_service.retrieval("我的电脑经常死机该如何解决")
    # result = retrival_service.retrieval("手机、平板上的画面能无线传输到电视上播放吗") # 80-90%
    #
    for doc in result:
        print("标题:", doc.metadata.get("title"))
        print("来源:", doc.metadata.get("source") or doc.metadata.get("path"))
        print("内容长度:", len(doc.page_content))
        print("内容预览:")
        print(doc.page_content[:1000])
        print("=" * 80)

