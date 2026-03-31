from typing import Dict
from langchain_core.messages import SystemMessage

def generate_response_node(llm):
    """Factory pour créer le nœud de génération"""

    def generate(state: Dict) -> Dict:
        """Générer la réponse avec Gemini dans la même langue que la question"""
        print("🤖 [NŒUD GENERATION] Génération de la réponse...")

        # Détecter la langue depuis le state (injecté par le router)
        detected_language = state.get("detected_language", "fr")

        if detected_language == "ar":
            lang_instruction = """أنت مساعد ذكي لمنصة iDaraty، متخصص في الإدارة الإلكترونية التونسية.

السياق:
{context}

التعليمات:
1. اشرح جميع الخطوات بوضوح ورتّبها
2. رقّم الخطوات
3. كن دقيقاً وشاملاً
4. إذا لم تكن المعلومات في السياق، قل ذلك بوضوح
5. أجب باللغة العربية دائماً
6. استخدم أسلوباً مهنياً ولطيفاً""".format(context=state.get("context", ""))
        else:
            lang_instruction = """Tu es un assistant intelligent pour iDaraty, spécialisé dans l'e-administration tunisienne.

Contexte:
{context}

INSTRUCTIONS:
1. Explique TOUTES les étapes clairement
2. Numérote les étapes
3. Sois précis et complet
4. Si l'info n'est pas dans le contexte, dis-le
5. Réponds en français
6. Ton professionnel et amical""".format(context=state.get("context", ""))

        system_message = SystemMessage(content=lang_instruction)
        messages = [system_message] + state["messages"]
        response = llm.invoke(messages)

        print(f"✅ Réponse générée ({len(response.content)} caractères) en '{detected_language}'")

        return {
            **state,
            "final_response": response.content
        }

    return generate