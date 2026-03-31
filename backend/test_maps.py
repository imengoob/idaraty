import os
from dotenv import load_dotenv

load_dotenv()

# Test 1: Clé existe ?
api_key = os.getenv("GOOGLE_MAPS_API_KEY")
if api_key:
    print(f"✅ Clé Google Maps trouvée: {api_key[:10]}...")
else:
    print("❌ GOOGLE_MAPS_API_KEY non trouvée dans .env")
    exit(1)

# Test 2: Service Google Maps
try:
    from services.google_maps import google_maps_service
    print("✅ Service Google Maps importé")
    
    # Test 3: Recherche de lieux
    print("\n🔍 Test recherche 'poste' à Sfax...")
    results = google_maps_service.search_nearby_places("poste", "Sfax")
    
    if results:
        print(f"✅ {len(results)} lieux trouvés:")
        for place in results:
            print(f"   - {place['name']}")
            print(f"     {place['address']}")
            print(f"     GPS: {place['latitude']}, {place['longitude']}\n")
    else:
        print("⚠️ Aucun lieu trouvé (vérifiez votre quota API)")
        
except Exception as e:
    print(f"❌ Erreur: {e}")
    import traceback
    traceback.print_exc()