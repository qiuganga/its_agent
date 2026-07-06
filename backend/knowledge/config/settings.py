from pydantic_settings import BaseSettings
import os

class Settings(BaseSettings):
    API_KEY: str = os.environ.get("API_KEY")
    BASE_URL: str = os.environ.get("BASE_URL")
    MODEL: str = os.environ.get("MODEL")
    EMBEDDING_MODEL: str = os.environ.get("EMBEDDING_MODEL")

    
    # knowledge/config
    KNOWLEDGE_BASE_URL:str=os.environ.get("KNOWLEDGE_BASE_URL")
    _current_dir = os.path.dirname(os.path.abspath(__file__))
    # knowledge
    _project_root = os.path.dirname(_current_dir)
    
    VECTOR_STORE_PATH: str = os.path.join(_project_root, "chroma_kb")
    VECTOR_COLLECTION_NAME: str = os.environ.get("VECTOR_COLLECTION_NAME", "its-knowledge")
    VECTOR_DISTANCE_SPACE: str = os.environ.get("VECTOR_DISTANCE_SPACE", "cosine")
    
    # Default directories
    CRAWL_OUTPUT_DIR: str = os.path.join(_project_root, "data", "crawl")
    # Using 'data/crawl' as the default location for markdown files
    MD_FOLDER_PATH: str = CRAWL_OUTPUT_DIR
    
    # Text splitting configuration
    CHUNK_SIZE: int = 3000
    CHUNK_OVERLAP: int = 200

    MAX_WORKERS: int = 10
    
    # Retrieval configuration
    TOP_ROUGH: int = 50
    TOP_FINAL: int = 5
    RAG_VECTOR_CANDIDATE_TOP_K: int = int(os.environ.get("RAG_VECTOR_CANDIDATE_TOP_K", "15"))
    RAG_TITLE_CANDIDATE_TOP_K: int = int(os.environ.get("RAG_TITLE_CANDIDATE_TOP_K", "10"))
    RAG_FINAL_TOP_K: int = int(os.environ.get("RAG_FINAL_TOP_K", "2"))
    RAG_MIN_RERANK_SCORE: float = float(os.environ.get("RAG_MIN_RERANK_SCORE", "0.35"))
    RAG_MMR_LAMBDA: float = float(os.environ.get("RAG_MMR_LAMBDA", "0.75"))
    RAG_MAX_CHUNKS_PER_DOCUMENT: int = int(os.environ.get("RAG_MAX_CHUNKS_PER_DOCUMENT", "1"))
    RAG_BM25_MODE: str = os.environ.get("RAG_BM25_MODE", "off")
    RAG_BM25_CANDIDATE_TOP_K: int = int(os.environ.get("RAG_BM25_CANDIDATE_TOP_K", "10"))
    RAG_RERANKER_MODE: str = os.environ.get("RAG_RERANKER_MODE", "off")
    RAG_RERANKER_PROVIDER: str = os.environ.get("RAG_RERANKER_PROVIDER", "siliconflow")
    RAG_RERANKER_BASE_URL: str = os.environ.get("RAG_RERANKER_BASE_URL", "https://api.siliconflow.cn/v1")
    RAG_RERANKER_MODEL: str = os.environ.get("RAG_RERANKER_MODEL", "Qwen/Qwen3-Reranker-8B")
    RAG_RERANKER_MAX_DOCUMENT_CHARS: int = int(os.environ.get("RAG_RERANKER_MAX_DOCUMENT_CHARS", "4000"))
    RAG_RERANKER_TIMEOUT_SECONDS: int = int(os.environ.get("RAG_RERANKER_TIMEOUT_SECONDS", "30"))
    RAG_RERANKER_BATCH_SIZE: int = int(os.environ.get("RAG_RERANKER_BATCH_SIZE", "20"))
    SILICONFLOW_API_KEY: str = os.environ.get("SILICONFLOW_API_KEY")
    RAG_ANCHOR_EVIDENCE_ENABLED: bool = os.environ.get("RAG_ANCHOR_EVIDENCE_ENABLED", "false").lower() == "true"
    RAG_ANCHOR_EVIDENCE_MODE: str = os.environ.get("RAG_ANCHOR_EVIDENCE_MODE", "off")
    RAG_ANCHOR_EVIDENCE_WINDOW_SIZE: int = int(os.environ.get("RAG_ANCHOR_EVIDENCE_WINDOW_SIZE", "10"))
    RAG_ANCHOR_MATCH_BOOST: float = float(os.environ.get("RAG_ANCHOR_MATCH_BOOST", "0.08"))
    RAG_ANCHOR_MISSING_PENALTY: float = float(os.environ.get("RAG_ANCHOR_MISSING_PENALTY", "0.10"))
    RAG_HARD_ANCHOR_MATCH_BOOST: float = float(os.environ.get("RAG_HARD_ANCHOR_MATCH_BOOST", "0.08"))
    RAG_HARD_ANCHOR_MISSING_PENALTY: float = float(os.environ.get("RAG_HARD_ANCHOR_MISSING_PENALTY", "0.10"))
    RAG_SOFT_ANCHOR_MATCH_BOOST: float = float(os.environ.get("RAG_SOFT_ANCHOR_MATCH_BOOST", "0.03"))
    RAG_SOFT_ANCHOR_MISSING_PENALTY: float = float(os.environ.get("RAG_SOFT_ANCHOR_MISSING_PENALTY", "0.00"))
    RAG_NEGATIVE_ANCHOR_MATCH_PENALTY: float = float(os.environ.get("RAG_NEGATIVE_ANCHOR_MATCH_PENALTY", "0.10"))
    RAG_ANCHOR_REQUIRE_EVIDENCE_FOR_BLOCK: bool = (
        os.environ.get("RAG_ANCHOR_REQUIRE_EVIDENCE_FOR_BLOCK", "true").lower() == "true"
    )

    class Config:
        env_file = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), ".env")
        extra = "ignore"

#实例化
settings = Settings()
