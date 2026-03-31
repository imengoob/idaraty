import React, { useState } from "react";

const PLACE_ICONS = {
  poste: "📮",
  banque: "🏦",
  municipalité: "🏛️",
  police: "👮",
  hôpital: "🏥",
  pharmacie: "💊",
};

export default function MapResult({ results, placeType, city }) {
  const [selected, setSelected] = useState(0);

  if (!results || results.length === 0) return null;

  const place = results[selected];
  const emoji = PLACE_ICONS[placeType?.toLowerCase()] || "📍";

  return (
    <div className="mt-3 rounded-2xl overflow-hidden border border-gray-200 shadow-lg bg-white max-w-[80%]">

      {/* Header */}
      <div className="bg-gradient-to-r from-blue-600 to-cyan-600 px-4 py-3 text-white">
        <div className="flex items-center gap-2">
          <span className="text-2xl">{emoji}</span>
          <div>
            <h3 className="font-bold text-sm">
              {placeType?.charAt(0).toUpperCase() + placeType?.slice(1)} à {city}
            </h3>
            <p className="text-xs text-blue-100">{results.length} lieu(x) trouvé(s)</p>
          </div>
        </div>
      </div>

      {/* Liste des lieux */}
      <div className="divide-y divide-gray-100">
        {results.map((r, i) => (
          <button
            key={i}
            onClick={() => setSelected(i)}
            className={`w-full text-left px-4 py-3 transition-colors ${
              selected === i ? "bg-blue-50 border-l-4 border-blue-500" : "hover:bg-gray-50"
            }`}
          >
            <div className="flex items-start gap-2">
              <span className="text-blue-500 mt-0.5 text-sm">📍</span>
              <div className="flex-1 min-w-0">
                <p className="font-semibold text-gray-900 text-sm truncate">{r.name}</p>
                <p className="text-xs text-gray-500 truncate mt-0.5">
                  {r.address?.split(",").slice(0, 3).join(", ")}
                </p>
                {r.distance_km != null && (
                  <span className="inline-block mt-1 text-xs bg-green-100 text-green-700 px-2 py-0.5 rounded-full">
                    📏 {r.distance_km.toFixed(1)} km
                  </span>
                )}
              </div>
            </div>
          </button>
        ))}
      </div>

      {/* Carte OpenStreetMap embed */}
      {place.latitude && place.longitude && (
        <div className="relative">
          <iframe
            title="map"
            width="100%"
            height="200"
            style={{ border: 0 }}
            src={`https://www.openstreetmap.org/export/embed.html?bbox=${place.longitude - 0.01},${place.latitude - 0.01},${place.longitude + 0.01},${place.latitude + 0.01}&layer=mapnik&marker=${place.latitude},${place.longitude}`}
          />
        </div>
      )}

      {/* Boutons action */}
      {place.latitude && place.longitude && (
        <div className="flex gap-2 p-3 bg-gray-50 border-t border-gray-100">
          <a
            href={`https://www.openstreetmap.org/?mlat=${place.latitude}&mlon=${place.longitude}#map=17/${place.latitude}/${place.longitude}`}
            target="_blank"
            rel="noopener noreferrer"
            className="flex-1 flex items-center justify-center gap-1 px-3 py-2 rounded-lg bg-blue-600 text-white text-xs font-semibold hover:bg-blue-700 transition-colors"
          >
            🗺️ Voir la carte
          </a>
          <a
            href={`https://www.openstreetmap.org/directions?to=${place.latitude},${place.longitude}`}
            target="_blank"
            rel="noopener noreferrer"
            className="flex-1 flex items-center justify-center gap-1 px-3 py-2 rounded-lg bg-green-600 text-white text-xs font-semibold hover:bg-green-700 transition-colors"
          >
            🧭 Itinéraire
          </a>
        </div>
      )}
    </div>
  );
}