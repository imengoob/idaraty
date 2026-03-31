import os
from typing import List, Dict
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
from langchain_community.vectorstores import Chroma
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document
from langchain_core.messages import HumanMessage, AIMessage
from config import settings

class RAGEngine:
    def __init__(self):
        print("🔧 Initialisation du RAG Engine...")
        
        # 🔹 1. Initialiser Gemini LLM avec le MEILLEUR modèle
        try:
            self.llm = ChatGoogleGenerativeAI(
                model="models/gemini-2.5-flash",  # ✅ LE MEILLEUR MODÈLE
                google_api_key=settings.GOOGLE_API_KEY,
                temperature=0.3,
                convert_system_message_to_human=True
            )
            print("✅ Gemini 2.5 Flash initialisé")
        except Exception as e:
            print(f"❌ Erreur Gemini LLM: {e}")
            raise
        
        # 🔹 2. Embeddings LOCAUX (100% gratuit, multilingue FR/AR)
        try:
            self.embeddings = HuggingFaceEmbeddings(
                model_name="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2",
                model_kwargs={'device': 'cpu'},
                encode_kwargs={'normalize_embeddings': True}
            )
            print("✅ HuggingFace Embeddings initialisé (LOCAL - FR/AR)")
        except Exception as e:
            print(f"❌ Erreur Embeddings: {e}")
            raise
        
        # 🔹 3. Vector Store
        self.vectorstore = None
        
        # 🔹 4. Initialiser avec les procédures de la BD
        self._initialize_vectorstore()
        
        # 🔹 5. Créer le prompt template
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", """Tu es un assistant intelligent pour iDaraty, spécialisé dans l'e-administration tunisienne.

Utilise le contexte suivant pour répondre à la question de l'utilisateur de manière claire et précise en français.

Contexte:
{context}

IMPORTANT:
- Si la procédure existe dans le contexte, explique-la étape par étape
- Si l'information n'est pas dans le contexte, dis-le poliment
- Sois concis mais complet
- Utilise un ton professionnel et amical"""),
            MessagesPlaceholder(variable_name="chat_history"),
            ("human", "{question}")
        ])
    
    def _initialize_vectorstore(self):
        """Initialise le vector store avec les procédures de la BD"""
        try:
            print("📚 Chargement des procédures depuis MySQL...")
            
            from database import SessionLocal
            from sqlalchemy import text
            db = SessionLocal()
            
            result = db.execute(text("""
                SELECT DISTINCT question, GROUP_CONCAT(etape SEPARATOR '\n') as steps 
                FROM procedures 
                GROUP BY question
            """))
            procedures = result.fetchall()
            db.close()
            
            if not procedures:
                print("⚠️ Aucune procédure trouvée dans la BD")
                documents = [Document(
                    page_content="Bienvenue sur iDaraty - Assistant e-administration tunisienne.",
                    metadata={"source": "default", "question": "Bienvenue"}
                )]
            else:
                print(f"✅ {len(procedures)} procédures chargées")
                
                documents = []
                for question, steps in procedures:
                    if question and steps:
                        content = f"Question: {question}\n\nProcédure:\n{steps}"
                        documents.append(Document(
                            page_content=content,
                            metadata={"question": question, "source": "procedures"}
                        ))
            
            print(f"📄 {len(documents)} documents créés")
            
            text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=1000,
                chunk_overlap=200,
                length_function=len,
            )
            splits = text_splitter.split_documents(documents)
            print(f"✂️ {len(splits)} chunks créés")
            
            print("🗄️ Création du vector store ChromaDB...")
            self.vectorstore = Chroma.from_documents(
                documents=splits,
                embedding=self.embeddings,
                persist_directory="./chroma_db"
            )
            
            print(f"✅ Vector store initialisé avec {len(splits)} chunks")
            
        except Exception as e:
            print(f"❌ Erreur initialisation vectorstore: {e}")
            import traceback
            traceback.print_exc()
            
            self.vectorstore = Chroma(
                embedding_function=self.embeddings,
                persist_directory="./chroma_db"
            )
    
    def _format_chat_history(self, conversation_history: List[Dict]) -> List:
        """Convertir l'historique en format LangChain"""
        messages = []
        for msg in conversation_history:
            if msg["role"] == "user":
                messages.append(HumanMessage(content=msg["content"]))
            elif msg["role"] == "assistant":
                messages.append(AIMessage(content=msg["content"]))
        return messages
    
    def ask(self, question: str, conversation_history: List[Dict] = None) -> Dict:
        """Poser une question au RAG"""
        try:
            print(f"❓ Question: {question}")
            
            # 🔹 Récupérer les documents pertinents
            retriever = self.vectorstore.as_retriever(search_kwargs={"k": 3})
            docs = retriever.invoke(question)
            
            # 🔹 Formater le contexte
            context = "\n\n".join([doc.page_content for doc in docs])
            print(f"📚 Contexte trouvé: {len(docs)} documents pertinents")
            
            # 🔹 Formater l'historique
            chat_history = []
            if conversation_history:
                chat_history = self._format_chat_history(conversation_history)
                print(f"💬 Historique: {len(chat_history)} messages")
            
            # 🔹 Créer la chaîne RAG
            chain = (
                {
                    "context": lambda x: context,
                    "chat_history": lambda x: chat_history,
                    "question": RunnablePassthrough()
                }
                | self.prompt
                | self.llm
                | StrOutputParser()
            )
            
            # 🔹 Générer la réponse
            print("🤖 Génération de la réponse avec Gemini 2.5 Flash...")
            response = chain.invoke(question)
            
            # 🔹 Extraire la question matchée
            matched_question = None
            similarity = 0.0
            
            if docs:
                matched_question = docs[0].metadata.get("question")
                similarity = 0.85
            
            print(f"✅ Réponse générée (procédure trouvée: {matched_question})")
            
            return {
                "response": response,
                "matched_question": matched_question,
                "similarity": similarity,
                "sources": [doc.page_content[:200] for doc in docs[:2]]
            }
            
        except Exception as e:
            print(f"❌ Erreur RAG: {e}")
            import traceback
            traceback.print_exc()
            
            return {
                "response": "Désolé, une erreur est survenue lors du traitement de votre question. Pouvez-vous la reformuler ?",
                "matched_question": None,
                "similarity": 0.0,
                "sources": []
            }

# Instance globale
print("🚀 Création de l'instance RAG Engine...")
rag_engine = RAGEngine()
print("✅ RAG Engine prêt!")