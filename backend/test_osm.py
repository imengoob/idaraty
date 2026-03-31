import asyncio
from services.openstreetmap import openstreetmap_service

def test_poste_gabes():
    print("\n🧪 TEST 1 : Poste à Gabes")
    results = openstreetmap_service.search_nearby_places("municipalite", "Gabes")
    if results:
        for r in results:
            print(f"✅ {r['name']} - {r['address']}")
    else:
        print("❌ Aucun résultat")

def test_banque_sfax():
    print("\n🧪 TEST 2 : Banque à Sfax")
    results = openstreetmap_service.search_nearby_places("banque", "Sfax")
    if results:
        for r in results:
            print(f"✅ {r['name']} - {r['address']}")
    else:
        print("❌ Aucun résultat")

def test_hopital_tunis():
    print("\n🧪 TEST 3 : Hôpital à Tunis")
    results = openstreetmap_service.search_nearby_places("poste", "Gabes")
    if results:
        for r in results:
            print(f"✅ {r['name']} - {r['address']}")
    else:
        print("❌ Aucun résultat")

if __name__ == "__main__":
    test_poste_gabes()
    test_banque_sfax()
    test_hopital_tunis()
    print("\n✅ Tests terminés !")