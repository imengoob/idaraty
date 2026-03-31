import google.generativeai as genai

# Votre clé API
API_KEY = "AIzaSyArX4vFotm8abEj8j-2r8LtCb3Lv116aJU"
genai.configure(api_key=API_KEY)

print("📋 Modèles Gemini disponibles pour generateContent :\n")

try:
    for model in genai.list_models():
        if 'generateContent' in model.supported_generation_methods:
            print(f"✅ {model.name}")
            print(f"   Support: {', '.join(model.supported_generation_methods)}\n")
except Exception as e:
    print(f"❌ Erreur: {e}")
    print("\n🔑 Vérifiez que votre clé API est valide sur:")
    print("   https://aistudio.google.com/app/apikey")