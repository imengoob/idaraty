import React from "react";

const TYPE_ICONS = {
  formulaire:  "📋",
  guide:       "📖",
  attestation: "📜",
  autre:       "📄",
};

export default function DocumentResult({ documents, lang = "fr" }) {
  if (!documents || documents.length === 0) return null;

  const isAr = lang === "ar";

  return (
    <div className={`mt-3 rounded-2xl overflow-hidden border border-gray-200 shadow-lg bg-white max-w-[80%] ${isAr ? "direction-rtl" : ""}`}>

      {/* Header */}
      <div className="bg-gradient-to-r from-orange-500 to-amber-500 px-4 py-3 text-white">
        <div className="flex items-center gap-2">
          <span style={{fontSize:22}}>📄</span>
          <div>
            <h3 className="font-bold text-sm">
              {isAr ? "الوثائق والاستمارات" : "Documents & Formulaires"}
            </h3>
            <p className="text-xs text-orange-100">
              {isAr
                ? `${documents.length} وثيقة متاحة للتحميل`
                : `${documents.length} document(s) disponible(s)`}
            </p>
          </div>
        </div>
      </div>

      {/* Liste documents */}
      <div className="divide-y divide-gray-100">
        {documents.map((doc, i) => {
          const icon  = TYPE_ICONS[doc.type] || "📄";
          const desc  = isAr
            ? (doc.description_ar || doc.description_fr || doc.procedure)
            : (doc.description_fr || doc.procedure);

          // URL de téléchargement
          const downloadUrl = doc.chemin_fichier.startsWith("/")
            ? `${import.meta.env.VITE_BACKEND_URL || "http://localhost:8000"}${doc.chemin_fichier}`
            : doc.chemin_fichier;

          return (
            <div key={i} className="px-4 py-3 hover:bg-gray-50 transition-colors">
              <div className="flex items-start gap-3">
                <span style={{fontSize:20, marginTop:2}}>{icon}</span>
                <div className="flex-1 min-w-0">
                  <p className="font-semibold text-gray-900 text-sm">{desc}</p>
                  <p className="text-xs text-gray-400 mt-0.5">{doc.nom_fichier}</p>
                </div>
              </div>

              {/* Boutons d'action */}
              <div className="flex gap-2 mt-2 ml-8">
                <a
                  href={downloadUrl}
                  download={doc.nom_fichier}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="flex items-center gap-1 px-3 py-1.5 rounded-lg bg-orange-600 text-white text-xs font-semibold hover:bg-orange-700 transition-colors"
                >
                  ⬇️ {isAr ? "تحميل" : "Télécharger"}
                </a>
                <a
                  href={downloadUrl}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="flex items-center gap-1 px-3 py-1.5 rounded-lg border border-gray-300 text-gray-700 text-xs font-semibold hover:bg-gray-100 transition-colors"
                >
                  👁️ {isAr ? "معاينة" : "Aperçu"}
                </a>
              </div>
            </div>
          );
        })}
      </div>

      {/* Footer */}
      <div className="px-4 py-2 bg-amber-50 border-t border-amber-100">
        <p className="text-xs text-amber-700">
          {isAr
            ? "💡 انقر على «تحميل» للحصول على الملف مباشرةً"
            : "💡 Cliquez sur «Télécharger» pour obtenir le fichier PDF"}
        </p>
      </div>
    </div>
  );
}