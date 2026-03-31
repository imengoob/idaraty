import os
from typing import List, Dict, TypedDict, Annotated, Optional
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from langgraph.graph import StateGraph, END
from langgraph.graph.message import add_messages
from config import settings

# Nœuds externes
from rag.nodes.router import route_question_node
from rag.nodes.retrieval import retrieve_context_node
from rag.nodes.generation import generate_response_node
from rag.nodes.maps import maps_search_node
from rag.nodes.documents import documents_search_node


# ════════════════════════════════════════════════════════
# ÉTAT DU GRAPHE
# ════════════════════════════════════════════════════════

class GraphState(TypedDict):
    messages:           Annotated[list, add_messages]
    question:           str
    detected_language:  str
    route:              str

    # RAG
    context:            str
    retrieved_docs:     List[Document]
    matched_question:   str
    similarity:         float
    final_response:     str

    # Maps
    place_type:         str
    city:               str
    maps_results:       List[Dict]
    maps_response:      str

    # Documents
    documents_results:  List[Dict]
    documents_response: str


# ════════════════════════════════════════════════════════
# MOTEUR
# ════════════════════════════════════════════════════════

class LangGraphRAGEngine:
    """
    Moteur RAG LangGraph — 3 routes :
      router → documents  : PDF / formulaires
      router → maps       : localisation OSM
      router → rag        : procédures administratives
    """

    def __init__(self):
        print("🔧 Initialisation du LangGraph RAG Engine...")

        # LLM Gemini
        self.llm = ChatGoogleGenerativeAI(
            model="models/gemini-2.5-flash",
            google_api_key=settings.GOOGLE_API_KEY,
            temperature=0.3,
            convert_system_message_to_human=True
        )
        print("✅ Gemini 2.5 Flash initialisé")

        # Embeddings multilingues
        self.embeddings = HuggingFaceEmbeddings(
            model_name="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2",
            model_kwargs={'device': 'cpu'},
            encode_kwargs={'normalize_embeddings': True}
        )
        print("✅ HuggingFace Embeddings initialisé (LOCAL - FR/AR)")

        self.vectorstore = None
        self._initialize_vectorstore()

        self.graph = self._build_graph()
        print("✅ LangGraph RAG Engine prêt!")

    # ── Vector Store ───────────────────────────────────

    def _initialize_vectorstore(self):
        try:
            print("📚 Chargement des procédures depuis MySQL...")
            from database import SessionLocal
            from sqlalchemy import text
            db = SessionLocal()

            result = db.execute(text("""
                SELECT question, GROUP_CONCAT(etape ORDER BY id SEPARATOR '\n') as steps
                FROM procedures
                GROUP BY question
                ORDER BY question
            """))
            procedures = result.fetchall()
            db.close()

            if not procedures:
                documents = [Document(
                    page_content="Bienvenue sur iDaraty.",
                    metadata={"source": "default", "question": "Bienvenue"}
                )]
            else:
                print(f"✅ {len(procedures)} procédures chargées")
                documents = []
                for question, steps in procedures:
                    if question and steps:
                        steps_list = steps.split('\n')
                        numbered   = '\n'.join(
                            f"Étape {i+1}: {s.strip()}"
                            for i, s in enumerate(steps_list) if s.strip()
                        )
                        content = (
                            f"PROCÉDURE: {question}\n\n{numbered}\n\n"
                            "Cette procédure fait partie de l'e-administration tunisienne iDaraty."
                        )
                        documents.append(Document(
                            page_content=content,
                            metadata={"question": question, "source": "procedures",
                                      "num_steps": len(steps_list)}
                        ))

            splitter = RecursiveCharacterTextSplitter(
                chunk_size=3000, chunk_overlap=500
            )
            splits = splitter.split_documents(documents)

            self.vectorstore = Chroma.from_documents(
                documents=splits,
                embedding=self.embeddings,
                persist_directory="./chroma_db_langgraph"
            )
            print(f"✅ Vector store initialisé avec {len(splits)} chunks")

        except Exception as e:
            print(f"❌ Erreur vectorstore: {e}")
            import traceback; traceback.print_exc()
            self.vectorstore = Chroma(
                embedding_function=self.embeddings,
                persist_directory="./chroma_db_langgraph"
            )

    # ── Graphe ─────────────────────────────────────────

    def _build_graph(self) -> StateGraph:
        print("🔨 Construction du graphe LangGraph...")

        retrieve = retrieve_context_node(self.vectorstore)
        generate = generate_response_node(self.llm)

        workflow = StateGraph(GraphState)

        # Nœuds
        workflow.add_node("router",    route_question_node)
        workflow.add_node("retrieve",  retrieve)
        workflow.add_node("generate",  generate)
        workflow.add_node("maps",      maps_search_node)
        workflow.add_node("documents", documents_search_node)   # ✅ nouveau

        # Point d'entrée
        workflow.set_entry_point("router")

        # Routage conditionnel
        workflow.add_conditional_edges(
            "router",
            lambda s: s.get("route", "rag"),
            {
                "rag":       "retrieve",
                "maps":      "maps",
                "documents": "documents",   # ✅
            }
        )

        # Flux RAG
        workflow.add_edge("retrieve",  "generate")
        workflow.add_edge("generate",  END)

        # Flux Maps et Documents → fin directe
        workflow.add_edge("maps",      END)
        workflow.add_edge("documents", END)    # ✅

        graph = workflow.compile()

        print("✅ Graphe compilé")
        print("   Flux: router → [rag: retrieve→generate | maps | documents] → END")
        return graph

    # ── API publique ───────────────────────────────────

    def ask(self, question: str, conversation_history: List[Dict] = None) -> Dict:
        try:
            print(f"❓ Question: {question}")

            messages = []
            if conversation_history:
                for msg in conversation_history:
                    if msg["role"] == "user":
                        messages.append(HumanMessage(content=msg["content"]))
                    elif msg["role"] == "assistant":
                        messages.append(AIMessage(content=msg["content"]))
            messages.append(HumanMessage(content=question))

            initial_state = {
                "messages":           messages,
                "question":           question,
                "detected_language":  "fr",
                "route":              "",
                "context":            "",
                "retrieved_docs":     [],
                "matched_question":   None,
                "similarity":         0.0,
                "final_response":     "",
                "place_type":         "",
                "city":               "",
                "maps_results":       [],
                "maps_response":      "",
                "documents_results":  [],
                "documents_response": "",
            }

            print("🚀 Exécution du graphe LangGraph...")
            final_state = self.graph.invoke(initial_state)
            route       = final_state.get("route", "rag")

            print(f"✅ Route utilisée : {route}")

            # ── Réponse selon la route ──
            if route == "documents":
                return {
                    "response":        final_state["documents_response"],
                    "route":           "documents",
                    "matched_question": None,
                    "similarity":       1.0,
                    "sources":          [],
                    "documents":        final_state.get("documents_results", []),
                }

            if route == "maps":
                return {
                    "response":        final_state["maps_response"],
                    "route":           "maps",
                    "matched_question": None,
                    "similarity":       1.0,
                    "sources":          [],
                    "maps_results":     final_state.get("maps_results", []),
                }

            # RAG
            return {
                "response":        final_state["final_response"],
                "route":           "rag",
                "matched_question": final_state.get("matched_question"),
                "similarity":       final_state.get("similarity", 0.0),
                "sources":         [d.page_content[:300] for d in final_state.get("retrieved_docs", [])[:2]],
                "documents":        [],
            }

        except Exception as e:
            print(f"❌ Erreur LangGraph: {e}")
            import traceback; traceback.print_exc()
            return {
                "response":        "Désolé, une erreur est survenue. Pouvez-vous reformuler votre question ?",
                "route":           "error",
                "matched_question": None,
                "similarity":       0.0,
                "sources":          [],
            }


# Instance globale
if __name__ != "__main__":
    print("🚀 Création de l'instance LangGraph RAG Engine...")
    try:
        langgraph_rag_engine = LangGraphRAGEngine()
        print("✅ LangGraph RAG Engine prêt!")
    except Exception as e:
        print(f"❌ Erreur initialisation: {e}")
        langgraph_rag_engine = None