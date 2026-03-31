import requests
from typing import Dict, List
import time
import math

class OpenStreetMapService:
    """
    Service OpenStreetMap - 100% GRATUIT
    Utilise Overpass API pour des résultats complets + Nominatim comme fallback
    """

    def __init__(self):
        self.nominatim_url = "https://nominatim.openstreetmap.org"
        self.overpass_url = "https://overpass-api.de/api/interpreter"
        self.headers = {
            "User-Agent": "iDaraty/1.0 (contact@idaraty.tn)"
        }

        # Mapping type → tags OSM (Overpass)
        # Chaque type a plusieurs tags pour maximiser les résultats
        self.osm_tags = {
            "poste": [
                '["amenity"="post_office"]',
                '["operator"="La Poste Tunisienne"]',
                '["name"~"[Pp]oste|[Bb]ureau de [Pp]oste|[Bb]riid|بريد",i]',
            ],
            "banque": [
                '["amenity"="bank"]',
                '["amenity"="atm"]',
                '["name"~"[Bb]anque|ATB|BIAT|BNA|STB|BH|UIB|Attijari|Zitouna",i]',
            ],
            "municipalité": [
                '["amenity"="townhall"]',
                '["office"="government"]',
                '["name"~"[Mm]unicipal|[Mm]airie|[Bb]aladia|بلدية",i]',
            ],
            "police": [
                '["amenity"="police"]',
                '["name"~"[Pp]olice|[Ss]ûreté|[Cc]ommissariat|شرطة",i]',
            ],
            "hôpital": [
                '["amenity"="hospital"]',
                '["amenity"="clinic"]',
                '["amenity"="health_centre"]',
                '["name"~"[Hh]ôpital|[Cc]linique|[Cc]entre de [Ss]anté|مستشفى",i]',
            ],
            "pharmacie": [
                '["amenity"="pharmacy"]',
                '["name"~"[Pp]harmacie|صيدلية",i]',
            ],
        }

        # Fallback Nominatim (termes de recherche texte)
        self.search_terms = {
            "poste": ["La Poste Tunisienne", "Bureau de poste", "Poste", "بريد"],
            "banque": ["Banque", "ATB", "BIAT", "BNA", "STB", "BH"],
            "municipalité": ["Municipalité", "Mairie", "Commune", "Baladia", "بلدية"],
            "police": ["Police", "Sûreté", "Commissariat", "شرطة"],
            "hôpital": ["Hôpital", "Clinique", "Centre de santé", "مستشفى"],
            "pharmacie": ["Pharmacie", "صيدلية"],
        }

        # Coordonnées approximatives des villes tunisiennes
        self.city_coords = {
            "Tunis":      (36.8190, 10.1658),
            "Sfax":       (34.7399, 10.7600),
            "Sousse":     (35.8245, 10.6346),
            "Gabes":      (33.8814, 10.0982),
            "Bizerte":    (37.2744, 9.8739),
            "Nabeul":     (36.4561, 10.7376),
            "Kairouan":   (35.6781, 10.0963),
            "Gafsa":      (34.4250, 8.7842),
            "Monastir":   (35.7643, 10.8113),
            "Mahdia":     (35.5047, 11.0622),
            "Tozeur":     (33.9197, 8.1335),
            "Tataouine":  (32.9297, 10.4518),
            "Medenine":   (33.3549, 10.5055),
            "Jendouba":   (36.5011, 8.7757),
            "Beja":       (36.7256, 9.1817),
            "Siliana":    (36.0844, 9.3708),
            "Zaghouan":   (36.4029, 10.1430),
            "Ariana":     (36.8625, 10.1956),
            "Ben Arous":  (36.7531, 10.2281),
            "Manouba":    (36.8100, 10.0983),
        }

    # ─────────────────────────────────────────
    # API PRINCIPALE
    # ─────────────────────────────────────────

    def search_nearby_places(self, place_type: str, city: str, limit: int = 5) -> List[Dict]:
        """
        Recherche principale :
        1. Overpass API (résultats OSM complets)
        2. Fallback Nominatim si Overpass échoue
        """
        print(f"📡 Recherche '{place_type}' à {city}...")

        # 1. Essayer Overpass API
        results = self._search_overpass(place_type, city, limit)

        # 2. Fallback Nominatim si pas de résultats
        if not results:
            print(f"⚠️ Overpass vide, fallback Nominatim...")
            results = self._search_nominatim(place_type, city, limit)

        print(f"✅ {len(results)} résultat(s) trouvé(s) pour '{place_type}' à {city}")
        return results

    def search_by_coordinates(
        self, place_type: str, user_lat: float, user_lon: float,
        city: str = "", limit: int = 5
    ) -> List[Dict]:
        """Recherche par GPS, triée par distance"""
        print(f"📍 Recherche '{place_type}' près de ({user_lat:.4f}, {user_lon:.4f})...")

        results = self._search_overpass_coords(place_type, user_lat, user_lon, radius_km=10)

        if not results and city:
            results = self.search_nearby_places(place_type, city, limit * 2)

        # Calculer et trier par distance
        for place in results:
            if place.get("latitude") and place.get("longitude"):
                place["distance_km"] = self._haversine(
                    user_lat, user_lon, place["latitude"], place["longitude"]
                )
            else:
                place["distance_km"] = 9999

        results.sort(key=lambda x: x.get("distance_km", 9999))
        return results[:limit]

    # ─────────────────────────────────────────
    # OVERPASS API
    # ─────────────────────────────────────────

    def _search_overpass(self, place_type: str, city: str, limit: int) -> List[Dict]:
        """
        Recherche via Overpass API dans un rayon autour de la ville.
        Utilise plusieurs tags OSM pour maximiser les résultats.
        """
        coords = self.city_coords.get(city)
        if not coords:
            # Géocoder la ville via Nominatim
            coords = self._geocode_city(city)
        if not coords:
            return []

        lat, lon = coords
        radius = 15000  # 15 km autour du centre-ville

        tags = self.osm_tags.get(place_type.lower(), [f'["name"~"{place_type}",i]'])

        all_results = []
        for tag in tags:
            query = f"""
[out:json][timeout:25];
(
  node{tag}(around:{radius},{lat},{lon});
  way{tag}(around:{radius},{lat},{lon});
  relation{tag}(around:{radius},{lat},{lon});
);
out center {limit * 3};
"""
            try:
                time.sleep(0.5)
                response = requests.post(
                    self.overpass_url,
                    data={"data": query},
                    headers=self.headers,
                    timeout=20
                )
                if response.status_code != 200:
                    continue

                data = response.json()
                for elem in data.get("elements", []):
                    tags_elem = elem.get("tags", {})
                    name = (
                        tags_elem.get("name") or
                        tags_elem.get("name:fr") or
                        tags_elem.get("name:ar") or
                        tags_elem.get("operator") or
                        place_type.capitalize()
                    )
                    # Coordonnées (node direct ou centroïde way/relation)
                    if elem["type"] == "node":
                        e_lat, e_lon = elem.get("lat"), elem.get("lon")
                    else:
                        center = elem.get("center", {})
                        e_lat, e_lon = center.get("lat"), center.get("lon")

                    if not e_lat or not e_lon:
                        continue

                    address = self._build_address(tags_elem, city)

                    all_results.append({
                        "name": name,
                        "address": address,
                        "latitude": float(e_lat),
                        "longitude": float(e_lon),
                        "phone": tags_elem.get("phone") or tags_elem.get("contact:phone", ""),
                        "opening_hours": tags_elem.get("opening_hours", ""),
                        "city": city,
                        "source": "overpass"
                    })

            except Exception as e:
                print(f"⚠️ Overpass erreur ({tag}): {e}")
                continue

        # Dédupliquer par proximité géographique
        return self._deduplicate(all_results)[:limit]

    def _search_overpass_coords(
        self, place_type: str, lat: float, lon: float, radius_km: int = 10
    ) -> List[Dict]:
        """Recherche Overpass par coordonnées GPS"""
        radius = radius_km * 1000
        tags = self.osm_tags.get(place_type.lower(), [f'["name"~"{place_type}",i]'])
        all_results = []

        for tag in tags:
            query = f"""
[out:json][timeout:25];
(
  node{tag}(around:{radius},{lat},{lon});
  way{tag}(around:{radius},{lat},{lon});
);
out center 10;
"""
            try:
                time.sleep(0.5)
                response = requests.post(
                    self.overpass_url,
                    data={"data": query},
                    headers=self.headers,
                    timeout=20
                )
                if response.status_code != 200:
                    continue

                data = response.json()
                for elem in data.get("elements", []):
                    tags_elem = elem.get("tags", {})
                    name = (
                        tags_elem.get("name") or
                        tags_elem.get("name:fr") or
                        tags_elem.get("operator") or
                        place_type.capitalize()
                    )
                    if elem["type"] == "node":
                        e_lat, e_lon = elem.get("lat"), elem.get("lon")
                    else:
                        center = elem.get("center", {})
                        e_lat, e_lon = center.get("lat"), center.get("lon")

                    if not e_lat or not e_lon:
                        continue

                    all_results.append({
                        "name": name,
                        "address": self._build_address(tags_elem, ""),
                        "latitude": float(e_lat),
                        "longitude": float(e_lon),
                        "phone": tags_elem.get("phone", ""),
                        "opening_hours": tags_elem.get("opening_hours", ""),
                        "source": "overpass"
                    })
            except Exception as e:
                print(f"⚠️ Overpass GPS erreur: {e}")
                continue

        return self._deduplicate(all_results)

    # ─────────────────────────────────────────
    # NOMINATIM (fallback)
    # ─────────────────────────────────────────

    def _search_nominatim(self, place_type: str, city: str, limit: int) -> List[Dict]:
        """Recherche Nominatim par texte (fallback)"""
        terms = self.search_terms.get(place_type.lower(), [place_type])
        all_results = []

        for term in terms[:3]:  # Max 3 termes pour éviter le rate limit
            params = {
                "q": f"{term}, {city}, Tunisie",
                "format": "json",
                "limit": 5,
                "addressdetails": 1,
                "countrycodes": "tn"
            }
            try:
                time.sleep(1)
                response = requests.get(
                    f"{self.nominatim_url}/search",
                    params=params,
                    headers=self.headers,
                    timeout=10
                )
                response.raise_for_status()
                data = response.json()

                for place in data:
                    addr = place.get("address", {})
                    all_results.append({
                        "name": place.get("name") or place.get("display_name", "").split(",")[0],
                        "address": place.get("display_name", ""),
                        "latitude": float(place.get("lat", 0)),
                        "longitude": float(place.get("lon", 0)),
                        "phone": "",
                        "opening_hours": "",
                        "city": addr.get("city") or addr.get("town") or city,
                        "source": "nominatim"
                    })

            except Exception as e:
                print(f"⚠️ Nominatim erreur ('{term}'): {e}")
                continue

        return self._deduplicate(all_results)[:limit]

    def _geocode_city(self, city: str):
        """Géocoder une ville via Nominatim"""
        try:
            time.sleep(1)
            response = requests.get(
                f"{self.nominatim_url}/search",
                params={"q": f"{city}, Tunisie", "format": "json", "limit": 1},
                headers=self.headers,
                timeout=10
            )
            data = response.json()
            if data:
                return float(data[0]["lat"]), float(data[0]["lon"])
        except Exception:
            pass
        return None

    # ─────────────────────────────────────────
    # UTILITAIRES
    # ─────────────────────────────────────────

    def _build_address(self, tags: dict, city: str) -> str:
        """Construire une adresse lisible depuis les tags OSM"""
        parts = []
        if tags.get("addr:housenumber"):
            parts.append(tags["addr:housenumber"])
        if tags.get("addr:street"):
            parts.append(tags["addr:street"])
        if tags.get("addr:city") or city:
            parts.append(tags.get("addr:city") or city)
        return ", ".join(parts) if parts else city

    def _deduplicate(self, results: List[Dict]) -> List[Dict]:
        """Supprimer les doublons géographiques (distance < 100m)"""
        unique = []
        for r in results:
            is_dup = any(
                self._haversine(
                    r.get("latitude", 0), r.get("longitude", 0),
                    u.get("latitude", 0), u.get("longitude", 0)
                ) < 0.1
                for u in unique
            )
            if not is_dup:
                unique.append(r)
        return unique

    def _haversine(self, lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """Distance en km entre deux points GPS"""
        R = 6371
        dlat = math.radians(lat2 - lat1)
        dlon = math.radians(lon2 - lon1)
        a = (math.sin(dlat / 2) ** 2 +
             math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) *
             math.sin(dlon / 2) ** 2)
        return R * 2 * math.asin(math.sqrt(a))

    def get_directions_url(self, lat: float, lon: float) -> str:
        return f"https://www.openstreetmap.org/directions?to={lat},{lon}"

    def get_embed_url(self, lat: float, lon: float, zoom: int = 16) -> str:
        return f"https://www.openstreetmap.org/?mlat={lat}&mlon={lon}#map={zoom}/{lat}/{lon}"


# Instance globale
openstreetmap_service = OpenStreetMapService()