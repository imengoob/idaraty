from typing import Dict, List
from services.openstreetmap import openstreetmap_service
from database import SessionLocal
from sqlalchemy import text

def maps_search_node(state: Dict) -> Dict:
    """
    Nœud de recherche Maps - Stratégie :
    1. BD locale (priorité absolue - rapide et fiable)
    2. OpenStreetMap (fallback si BD vide)
    """
    print(f"🗺️ [NŒUD MAPS] Recherche {state['place_type']} à {state['city']}")
    
    place_type = state.get("place_type")
    city = state.get("city", "Sfax")
    
    # 🔹 1. TOUJOURS chercher dans BD locale d'abord
    local_results = _search_local_db(place_type, city)
    
    if local_results:
        print(f"✅ {len(local_results)} lieu(x) trouvé(s) dans la BD locale")
        all_results = local_results
    else:
        # 🔹 2. Fallback OSM seulement si BD vide
        print("⚠️ BD locale vide, recherche OpenStreetMap...")
        osm_results = openstreetmap_service.search_nearby_places(place_type, city)
        
        if osm_results:
            print(f"✅ {len(osm_results)} lieu(x) trouvé(s) via OSM")
            all_results = osm_results
        else:
            print("❌ Aucun résultat OSM")
            all_results = []
    
    # 🔹 3. Formater la réponse
    if not all_results:
        return {
            **state,
            "maps_results": [],
            "maps_response": f"Désolé, je n'ai trouvé aucun **{place_type}** à **{city}**.\n\n💡 Essayez une autre ville (Tunis, Sfax, Sousse) ou un autre type de lieu."
        }
    
    response = _format_maps_response(all_results, place_type, city)
    
    return {
        **state,
        "maps_results": all_results,
        "maps_response": response
    }


def _search_local_db(place_type: str, city: str) -> List[Dict]:
    """Rechercher dans la base de données locale"""
    db = SessionLocal()
    try:
        query = text("""
            SELECT name, address, latitude, longitude, phone, opening_hours
            FROM administrative_places
            WHERE LOWER(type) = LOWER(:place_type) 
            AND LOWER(city) = LOWER(:city)
            ORDER BY id
            LIMIT 5
        """)
        
        result = db.execute(query, {"place_type": place_type, "city": city})
        rows = result.fetchall()
        
        if not rows:
            return []
        
        return [
            {
                "name": row[0],
                "address": row[1],
                "latitude": float(row[2]) if row[2] else None,
                "longitude": float(row[3]) if row[3] else None,
                "phone": row[4],
                "opening_hours": row[5],
                "source": "local"
            }
            for row in rows
        ]
        
    except Exception as e:
        print(f"❌ Erreur recherche BD locale: {e}")
        return []
    finally:
        db.close()


def _format_maps_response(results: List[Dict], place_type: str, city: str) -> str:
    """Formater la réponse avec emoji et style professionnel"""
    
    # Emoji selon le type
    emoji_map = {
        "poste": "📮",
        "banque": "🏦",
        "municipalité": "🏛️",
        "police": "👮",
        "hôpital": "🏥",
        "pharmacie": "💊",
    }
    
    emoji = emoji_map.get(place_type.lower(), "📍")
    
    response = f"{emoji} **{place_type.capitalize()}** à **{city}** :\n\n"
    response += f"J'ai trouvé **{len(results)}** lieu(x) :\n\n"
    
    for i, place in enumerate(results[:5], 1):  # Max 5 résultats
        response += f"**{i}. {place['name']}**\n"
        response += f"   📌 {place['address']}\n"
        
        if place.get('phone'):
            response += f"   ☎️  {place['phone']}\n"
        
        if place.get('opening_hours'):
            response += f"   🕒 {place['opening_hours']}\n"
        
        # Lien carte interactive
        if place.get('latitude') and place.get('longitude'):
            lat, lon = place['latitude'], place['longitude']
            
            # Lien OpenStreetMap
            osm_url = f"https://www.openstreetmap.org/?mlat={lat}&mlon={lon}#map=17/{lat}/{lon}"
            response += f"   🗺️  [Voir sur la carte]({osm_url})\n"
            
            # Lien itinéraire
            directions_url = f"https://www.openstreetmap.org/directions?to={lat},{lon}"
            response += f"   🧭 [Obtenir l'itinéraire]({directions_url})\n"
        
        # Source (utile pour debug)
        source_emoji = "💾" if place.get('source') == 'local' else "🌐"
        response += f"   {source_emoji} Source: {place.get('source', 'inconnu')}\n"
        
        response += "\n"
    
    # Footer avec aide
    response += "---\n"
    response += "💡 **Besoin d'autre chose ?**\n"
    response += "Essayez : *\"Où est l'hôpital le plus proche ?\"* ou *\"Adresse de la municipalité de Tunis\"*"
    
    return response