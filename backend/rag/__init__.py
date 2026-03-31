# backend/rag/__init__.py

# N'importer QUE les classes, PAS les instances
from .engine_langgraph import LangGraphRAGEngine

# Pour la compatibilité avec l'ancien code
try:
    from .engine import RAGEngine
except ImportError:
    RAGEngine = None

__all__ = ["LangGraphRAGEngine", "RAGEngine"]