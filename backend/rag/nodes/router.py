from typing import Dict
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

LOCATION_PATTERNS_FR = [
    r"où (est|se trouve|trouver|sont|puis-je trouver)",
    r"adresse (du|de la|des|d'un|d'une)",
    r"(le|la|les) plus proche",
    r"localisa", r"localis",
    r"donner.{0,15}(adresse|localisation|lieu|endroit|position|carte)",
    r"(donne|donnez).{0,10}(moi|nous).{0,10}(adresse|localisation|lieu|position|carte)",
    r"(cherche|je cherche).{0,20}(poste|banque|hôpital|pharmacie|police|municipalité)",
    r"(proche|autour|à proximité)", r"itinéraire",
    r"comment (aller|accéder|rejoindre)", r"se situe|situé", r"emplacement",
]
LOCATION_PATTERNS_AR = [
    r"أين (يوجد|توجد|هو|هي|تقع|يقع|أجد)",
    r"عنوان", r"(موقع|مواقع)", r"مكان", r"أقرب",
    r"كيف (أصل|أذهب|أروح)", r"خريطة",
    r"فين (الـ|هو|هي|البريد|البنك)",
    r"وين (الـ|هو|هي|البريد|البنك)",
    r"عطيني (عنوان|موقع)", r"دلّني", r"(قريب|بالقرب)",
]

PLACE_TYPES = {
    "poste":        ["poste","bureau de poste","la poste","postea","البريد","مكتب البريد","بريد"],
    "banque":       ["banque","distributeur","atm","agence bancaire","بنك","مصرف","البنك"],
    "municipalité": ["municipalité","mairie","commune","baladia","بلدية","البلدية"],
    "police":       ["police","commissariat","شرطة","مركز الشرطة","أمن"],
    "hôpital":      ["hôpital","clinique","centre de santé","hopital","مستشفى","عيادة"],
    "pharmacie":    ["pharmacie","pharmacien","صيدلية","صيدلي"],
}

CITY_MAP = {
    "tunis":"Tunis","تونس":"Tunis","sfax":"Sfax","صفاقس":"Sfax",
    "sousse":"Sousse","سوسة":"Sousse","gabes":"Gabes","gabès":"Gabes","قابس":"Gabes",
    "bizerte":"Bizerte","بنزرت":"Bizerte","nabeul":"Nabeul","نابل":"Nabeul",
    "kairouan":"Kairouan","القيروان":"Kairouan","gafsa":"Gafsa","قفصة":"Gafsa",
    "monastir":"Monastir","المنستير":"Monastir","mahdia":"Mahdia","المهدية":"Mahdia",
    "tozeur":"Tozeur","توزر":"Tozeur","tataouine":"Tataouine","تطاوين":"Tataouine",
    "medenine":"Medenine","مدنين":"Medenine","jendouba":"Jendouba","جندوبة":"Jendouba",
    "beja":"Beja","باجة":"Beja","ariana":"Ariana","أريانة":"Ariana",
    "manouba":"Manouba","منوبة":"Manouba",
}


def route_question_node(state: Dict) -> Dict:
    """
    Routage intelligent — 3 routes, priorité : documents > maps > rag
    Détection FR + AR + dialecte tunisien + fautes de frappe
    """
    question       = state["question"]
    question_lower = question.lower().strip()

    # 1. Langue
    arabic_chars      = len(re.findall(r'[\u0600-\u06FF]', question))
    detected_language = "ar" if arabic_chars > 3 else "fr"

    # 2. Route DOCUMENTS (priorité absolue)
    is_doc = any(re.search(p, question_lower) for p in DOCUMENT_PATTERNS_FR + DOCUMENT_PATTERNS_AR)
    if is_doc:
        print(f"📄 [ROUTER] → documents (lang={detected_language})")
        return {**state, "route": "documents", "detected_language": detected_language}

    # 3. Route MAPS
    is_loc = any(re.search(p, question_lower) for p in LOCATION_PATTERNS_FR + LOCATION_PATTERNS_AR)
    if is_loc:
        detected_type = None
        for ptype, keywords in PLACE_TYPES.items():
            if any(kw in question_lower for kw in keywords):
                detected_type = ptype
                break

        detected_city = None
        for key, canonical in CITY_MAP.items():
            if key in question_lower:
                detected_city = canonical
                break
        if not detected_city:
            m = re.search(r"(?:à|a |de |en |في|بـ|ب)\s*([A-ZÀ-Öa-zà-ö\u0600-\u06FF]{3,})", question)
            if m:
                raw = m.group(1).strip().capitalize()
                detected_city = CITY_MAP.get(raw.lower(), raw)
        if not detected_city:
            detected_city = "Sfax"

        print(f"🗺️ [ROUTER] → maps ({detected_type} à {detected_city}, lang={detected_language})")
        return {
            **state,
            "route": "maps",
            "place_type": detected_type or "lieu",
            "city": detected_city,
            "detected_language": detected_language,
        }

    # 4. Route RAG (défaut)
    print(f"📚 [ROUTER] → rag (lang={detected_language})")
    return {**state, "route": "rag", "detected_language": detected_language}