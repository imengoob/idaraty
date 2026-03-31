import React from "react";
import MapResult from "./MapResult";
import DocumentResult from "./DocumentResult";
import NotificationBar from "./NotificationBar";

export default function MessageBubble({
  role,
  text,
  rtl = false,
  mapData = null,
  docData = null,
  conversationId = null,
  token = null,
  isLastAssistant = false,
  route = "rag",
  lang = "fr",
}) {
  const isUser = role === "user";
  const base   = "rounded-2xl px-5 py-4 text-base leading-relaxed break-words";
  const userCls      = `${base} self-end bg-gray-200 text-gray-800 shadow-sm max-w-[75%]`;
  const assistantCls = `${base} self-start bg-gray-100 text-gray-900 shadow-sm max-w-[80%]`;

  const detectedLang = (text.match(/[\u0600-\u06FF]/g)||[]).length > 3 ? "ar" : "fr";

  // ✅ Condition simplifiée — affiche la barre sur TOUT message assistant
  // qui n'est pas maps/documents, même si route est undefined
  const isRagResponse = !isUser && route !== "maps" && route !== "documents" && role === "assistant";
  const showNotifBar  = isRagResponse && isLastAssistant && !!token;

  return (
    <div className={`w-full flex flex-col ${isUser ? "items-end" : "items-start"} ${rtl ? "direction-rtl" : ""}`}>

      {/* Bulle de message */}
      <div
        className={isUser ? userCls : assistantCls}
        style={{ whiteSpace: "pre-wrap", wordBreak: "break-word", minHeight: 48 }}
      >
        {text}
      </div>

      {/* Carte Maps si disponible */}
      {!isUser && mapData && mapData.results?.length > 0 && (
        <MapResult
          results={mapData.results}
          placeType={mapData.placeType}
          city={mapData.city}
        />
      )}

      {/* Documents/PDF si disponibles */}
      {!isUser && docData && docData.length > 0 && (
        <DocumentResult documents={docData} lang={detectedLang} />
      )}

      {/* Barre de notification — email / SMS / PDF / rappel */}
      {showNotifBar && (
        <div className="mt-2 max-w-[80%]">
          <NotificationBar
            conversationId={conversationId}
            token={token}
            lang={lang}
          />
        </div>
      )}

    </div>
  );
}