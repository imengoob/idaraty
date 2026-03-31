from typing import Dict, List
from database import SessionLocal
from sqlalchemy import text
import re

DOCUMENT_PATTERNS_FR = [
    r"formulaire", r"télécharger", r"telecharger", r"pdf",
    r"document", r"papier", r"imprimé", r"imprime", r"dossier",
    r"pièce(s)? (à|a) fournir", r"fichier",
    r"lien (de |du )?téléchargement",
    r"(obtenir|avoir|donner|envoyer).{0,15}(formulaire|document|pdf|papier)",
    r"je (veux|voudrais|cherche|ai besoin de).{0,20}(formulaire|pdf|document|papier)",
    r"comment (avoir|obtenir|télécharger).{0,20}(formulaire|pdf|document)",
]
DOCUMENT_PATTERNS_AR = [
    r"استمارة", r"نموذج", r"وثيقة", r"ملف", r"تحميل",
    r"تنزيل", r"ورقة", r"مستند", r"رابط",
    r"أريد.{0,15}(ملف|استمارة|نموذج|وثيقة|pdf)",
    r"أبغى.{0,15}(ملف|استمارة|نموذج)",
    r"أحتاج.{0,15}(ملف|استمارة|نموذج|وثيقة)",
    r"(عطيني|ابعثلي|حمّلني|أرسل لي).{0,15}(ملف|استمارة|نموذج|وثيقة)",
]


def documents_search_node(state: Dict) -> Dict:
    question      = state.get("question", "")
    detected_lang = state.get("detected_language", "fr")
    print(f"📄 [NŒUD DOCUMENTS] Recherche PDF: '{question}' (lang={detected_lang})")

    results = _search_documents(question)

    if not results:
        response = (
            "عذراً، لم أجد أي وثيقة متعلقة بطلبك.\n💡 جرّب: «أريد استمارة جواز السفر»"
            if detected_lang == "ar" else
            "Désolé, aucun document trouvé.\n💡 Essayez: «Je veux le formulaire passeport»"
        )
        return {**state, "documents_results": [], "documents_response": response}

    return {
        **state,
        "documents_results":  results,
        "documents_response": _format_documents_response(results, detected_lang),
    }


def _search_documents(question: str) -> List[Dict]:
    db = SessionLocal()
    try:
        lower_q  = question.lower().strip()

        # FULLTEXT
        try:
            rows = db.execute(text("""
                SELECT id, nom_procedure, nom_fichier, chemin_fichier, type,
                       description_fr, description_ar,
                       MATCH(tags_fr) AGAINST (:q IN BOOLEAN MODE) +
                       MATCH(tags_ar) AGAINST (:q IN BOOLEAN MODE) AS score
                FROM documents
                WHERE MATCH(tags_fr) AGAINST (:q IN BOOLEAN MODE)
                   OR MATCH(tags_ar) AGAINST (:q IN BOOLEAN MODE)
                ORDER BY score DESC LIMIT 5
            """), {"q": lower_q}).fetchall()
            if rows:
                return _to_dicts(rows)
        except Exception:
            pass

        # LIKE fallback
        keywords = [w for w in re.findall(r'\w+', lower_q) if len(w) >= 3]
        if not keywords:
            return []

        conds  = " OR ".join([
            f"LOWER(nom_procedure) LIKE :kw{i} OR LOWER(tags_fr) LIKE :kw{i} "
            f"OR LOWER(tags_ar) LIKE :kw{i} OR LOWER(description_fr) LIKE :kw{i} "
            f"OR LOWER(description_ar) LIKE :kw{i}"
            for i, _ in enumerate(keywords)
        ])
        params = {f"kw{i}": f"%{kw}%" for i, kw in enumerate(keywords)}

        rows = db.execute(text(f"""
            SELECT id, nom_procedure, nom_fichier, chemin_fichier, type,
                   description_fr, description_ar, 0, 0
            FROM documents WHERE {conds} ORDER BY id LIMIT 5
        """), params).fetchall()
        return _to_dicts(rows)

    except Exception as e:
        print(f"❌ Erreur recherche documents: {e}")
        return []
    finally:
        db.close()


def _to_dicts(rows) -> List[Dict]:
    return [
        {"id": r[0], "nom_procedure": r[1], "nom_fichier": r[2],
         "chemin_fichier": r[3], "type": r[4],
         "description_fr": r[5], "description_ar": r[6]}
        for r in rows
    ]


def _format_documents_response(results: List[Dict], lang: str) -> str:
    icons = {"formulaire": "📋", "guide": "📖", "attestation": "📜", "autre": "📄"}
    if lang == "ar":
        out = f"📄 وجدت **{len(results)}** وثيقة :\n\n"
        for r in results:
            desc = r["description_ar"] or r["description_fr"] or r["nom_procedure"]
            out += f"**{icons.get(r['type'],'📄')} {desc}**\n"
            out += f"   🔗 [تحميل الملف]({r['chemin_fichier']})\n"
            out += f"   📁 `{r['nom_fichier']}`\n\n"
        out += "---\n💡 انقر على الرابط لتحميل الوثيقة."
    else:
        out = f"📄 J'ai trouvé **{len(results)}** document(s) :\n\n"
        for r in results:
            desc = r["description_fr"] or r["nom_procedure"]
            out += f"**{icons.get(r['type'],'📄')} {desc}**\n"
            out += f"   🔗 [Télécharger]({r['chemin_fichier']})\n"
            out += f"   📁 `{r['nom_fichier']}`\n\n"
        out += "---\n💡 Cliquez sur le lien pour télécharger le PDF."
    return out