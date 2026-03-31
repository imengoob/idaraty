import os
import requests
from typing import Dict, List, Optional
from config import settings

class GoogleMapsService:
    """Service pour interagir avec Google Maps API"""
    
    def __init__(self):
        self.api_key = os.getenv("GOOGLE_MAPS_API_KEY")
        if not self.api_key:
            raise ValueError("GOOGLE_MAPS_API_KEY non définie dans .env")
        
        self.places_base_url = "https://maps.googleapis.com/maps/api/place"
        self.geocode_base_url = "https://maps.googleapis.com/maps/api/geocode"
    
    def search_nearby_places(
        self, 
        place_type: str, 
        city: str, 
        radius: int = 5000
    ) -> List[Dict]:
        """
        Recherche des lieux à proximité
        
        Args:
            place_type: Type de lieu (poste, banque, municipalité)
            city: Ville de recherche
            radius: Rayon de recherche en mètres
            
        Returns:
            Liste de lieux trouvés
        """
        # D'abord, géocoder la ville pour obtenir lat/lng
        location = self._geocode_city(city)
        if not location:
            return []
        
        # Mapper les types français vers les types Google
        type_mapping = {
            "poste": "post_office",
            "banque": "bank",
            "municipalité": "city_hall",
            "police": "police",
            "hôpital": "hospital",
            "pharmacie": "pharmacy"
        }
        
        google_type = type_mapping.get(place_type.lower(), place_type)
        
        # Recherche sur Google Places
        url = f"{self.places_base_url}/nearbysearch/json"
        params = {
            "location": f"{location['lat']},{location['lng']}",
            "radius": radius,
            "type": google_type,
            "language": "fr",
            "key": self.api_key
        }
        
        try:
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            results = []
            for place in data.get("results", [])[:5]:  # Top 5
                results.append({
                    "name": place.get("name"),
                    "address": place.get("vicinity"),
                    "latitude": place["geometry"]["location"]["lat"],
                    "longitude": place["geometry"]["location"]["lng"],
                    "place_id": place.get("place_id"),
                    "rating": place.get("rating"),
                    "open_now": place.get("opening_hours", {}).get("open_now")
                })
            
            return results
            
        except Exception as e:
            print(f"❌ Erreur Google Places API: {e}")
            return []
    
    def _geocode_city(self, city: str) -> Optional[Dict]:
        """Obtenir lat/lng d'une ville"""
        url = f"{self.geocode_base_url}/json"
        params = {
            "address": f"{city}, Tunisie",
            "key": self.api_key
        }
        
        try:
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            if data.get("results"):
                location = data["results"][0]["geometry"]["location"]
                return {"lat": location["lat"], "lng": location["lng"]}
            
            return None
            
        except Exception as e:
            print(f"❌ Erreur Geocoding: {e}")
            return None
    
    def get_place_details(self, place_id: str) -> Optional[Dict]:
        """Obtenir les détails complets d'un lieu"""
        url = f"{self.places_base_url}/details/json"
        params = {
            "place_id": place_id,
            "fields": "name,formatted_address,formatted_phone_number,opening_hours,rating,website",
            "language": "fr",
            "key": self.api_key
        }
        
        try:
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            if data.get("result"):
                result = data["result"]
                return {
                    "name": result.get("name"),
                    "address": result.get("formatted_address"),
                    "phone": result.get("formatted_phone_number"),
                    "opening_hours": result.get("opening_hours", {}).get("weekday_text", []),
                    "rating": result.get("rating"),
                    "website": result.get("website")
                }
            
            return None
            
        except Exception as e:
            print(f"❌ Erreur Place Details: {e}")
            return None
    
    def get_directions_url(self, destination_lat: float, destination_lng: float) -> str:
        """Générer URL Google Maps pour itinéraire"""
        return f"https://www.google.com/maps/dir/?api=1&destination={destination_lat},{destination_lng}"
    
    def get_embed_url(self, latitude: float, longitude: float) -> str:
        """Générer URL pour carte embed"""
        return f"https://www.google.com/maps/embed/v1/place?key={self.api_key}&q={latitude},{longitude}&zoom=15"


# Instance globale
google_maps_service = GoogleMapsService()