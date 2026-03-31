# Déplacer la fonction retrieve_context de engine_langgraph.py ici
from typing import Dict

def retrieve_context_node(vectorstore):
    """Factory pour créer le nœud de récupération"""
    
    def retrieve(state: Dict) -> Dict:
        """Récupérer le contexte depuis le vector store"""
        print("📚 [NŒUD RETRIEVAL] Récupération du contexte...")
        
        question = state["question"]
        
        retriever = vectorstore.as_retriever(search_kwargs={"k": 5})
        docs = retriever.invoke(question)
        
        context = "\n\n".join([doc.page_content for doc in docs])
        
        matched_question = None
        similarity = 0.0
        if docs:
            matched_question = docs[0].metadata.get("question")
            similarity = 0.85
        
        print(f"✅ {len(docs)} documents récupérés")
        
        return {
            **state,
            "context": context,
            "retrieved_docs": docs,
            "matched_question": matched_question,
            "similarity": similarity
        }
    
    return retrieve