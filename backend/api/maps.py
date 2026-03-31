from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
from services.openstreetmap import openstreetmap_service

router = APIRouter(prefix="/maps", tags=["Maps"])

class PlaceSearchRequest(BaseModel):
    place_type: str          # "poste", "banque", "hôpital"...
    city: Optional[str] = "" # "Sfax", "Tunis"...
    user_lat: Optional[float] = None  # GPS latitude
    user_lon: Optional[float] = None  # GPS longitude

class PlaceResult(BaseModel):
    name: str
    address: str
    latitude: Optional[float]
    longitude: Optional[float]
    distance_km: Optional[float] = None
    map_url: str
    directions_url: str
    source: str

@router.post("/search")
def search_places(data: PlaceSearchRequest):
    """
    Rechercher des lieux administratifs.
    - Avec city → cherche dans cette ville
    - Avec user_lat/user_lon → cherche le plus proche par GPS
    """
    try:
        # Recherche par GPS (le plus proche)
        if data.user_lat and data.user_lon:
            results = openstreetmap_service.search_by_coordinates(
                place_type=data.place_type,
                user_lat=data.user_lat,
                user_lon=data.user_lon,
                city=data.city or "",
                limit=5
            )
        # Recherche par ville
        elif data.city:
            results = openstreetmap_service.search_nearby_places(
                place_type=data.place_type,
                city=data.city,
                limit=5
            )
        else:
            raise HTTPException(
                status_code=400,
                detail="Fournir soit 'city' soit 'user_lat' et 'user_lon'"
            )
        
        if not results:
            return {
                "success": False,
                "message": f"Aucun(e) {data.place_type} trouvé(e)",
                "results": []
            }
        
        # Enrichir avec les URLs de carte
        enriched = []
        for place in results:
            lat = place.get("latitude")
            lon = place.get("longitude")
            enriched.append({
                **place,
                "map_url": openstreetmap_service.get_embed_url(lat, lon) if lat and lon else "",
                "directions_url": openstreetmap_service.get_directions_url(lat, lon) if lat and lon else "",
            })
        
        return {
            "success": True,
            "count": len(enriched),
            "results": enriched
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/types")
def get_place_types():
    """Retourne les types de lieux supportés"""
    return {
        "types": [
            {"id": "poste", "label": "La Poste", "emoji": "📮"},
            {"id": "banque", "label": "Banque", "emoji": "🏦"},
            {"id": "municipalité", "label": "Municipalité", "emoji": "🏛️"},
            {"id": "police", "label": "Police", "emoji": "👮"},
            {"id": "hôpital", "label": "Hôpital", "emoji": "🏥"},
            {"id": "pharmacie", "label": "Pharmacie", "emoji": "💊"},
        ]
    }