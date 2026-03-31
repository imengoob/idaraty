import React, { useState } from "react";
const BASE_URL = import.meta.env.VITE_BACKEND_URL || "http://localhost:8000";

export default function NotificationBar({ conversationId, token, lang = "fr" }) {
  const [sent,    setSent]    = useState(null);
  const [loading, setLoading] = useState(null);
  const [showRem, setShowRem] = useState(false);
  const [days,    setDays]    = useState(90);

  const isAr = lang === "ar";
  const headers = {
    "Content-Type": "application/json",
    Authorization: `Bearer ${token}`,
  };

  const sendEmail = async () => {
    setLoading("email");
    try {
      await fetch(`${BASE_URL}/notifications/send-email`, {
        method: "POST",
        headers,
        body: JSON.stringify({ conversation_id: conversationId }),
      });
      setSent("email");
    } catch {}
    setLoading(null);
  };

  const downloadPDF = async () => {
    setLoading("pdf");
    try {
      const res  = await fetch(`${BASE_URL}/notifications/export-pdf/${conversationId}`, { headers });
      const blob = await res.blob();
      const url  = URL.createObjectURL(blob);
      const a    = document.createElement("a");
      a.href     = url;
      a.download = `idaraty-${conversationId}.pdf`;
      a.click();
      URL.revokeObjectURL(url);
      setSent("pdf");
    } catch {}
    setLoading(null);
  };

  const createReminder = async () => {
    setLoading("rem");
    try {
      await fetch(`${BASE_URL}/notifications/reminders`, {
        method: "POST",
        headers,
        body: JSON.stringify({
          conversation_id: conversationId,
          procedure_name: isAr ? "إجراء إداري" : "Procédure administrative",
          remind_in_days: days,
          type: "email",
        }),
      });
      setSent("rem");
      setShowRem(false);
    } catch {}
    setLoading(null);
  };

  if (!conversationId) return null;

  return (
    <div className={`mt-2 flex flex-wrap gap-2 ${isAr ? "flex-row-reverse" : ""}`}>

      {/* ── Email ── */}
      {sent === "email" ? (
        <span className="px-3 py-1.5 rounded-lg bg-green-100 text-green-700 text-xs font-medium">
          {isAr ? "✅ البريد أُرسل" : "✅ Email envoyé"}
        </span>
      ) : (
        <button onClick={sendEmail} disabled={loading === "email"}
          className="px-3 py-1.5 rounded-lg border border-blue-200 bg-blue-50 text-blue-700 text-xs font-medium hover:bg-blue-100 transition disabled:opacity-50">
          {loading === "email" ? "..." : isAr ? "📧 إرسال بالبريد" : "📧 Envoyer par email"}
        </button>
      )}

      {/* ── PDF ── */}
      {sent === "pdf" ? (
        <span className="px-3 py-1.5 rounded-lg bg-green-100 text-green-700 text-xs font-medium">
          {isAr ? "✅ PDF محمّل" : "✅ PDF téléchargé"}
        </span>
      ) : (
        <button onClick={downloadPDF} disabled={loading === "pdf"}
          className="px-3 py-1.5 rounded-lg border border-orange-200 bg-orange-50 text-orange-700 text-xs font-medium hover:bg-orange-100 transition disabled:opacity-50">
          {loading === "pdf" ? "..." : isAr ? "📄 تحميل PDF" : "📄 Télécharger PDF"}
        </button>
      )}

      {/* ── Rappel ── */}
      {sent === "rem" ? (
        <span className="px-3 py-1.5 rounded-lg bg-green-100 text-green-700 text-xs font-medium">
          {isAr ? "✅ تذكير مضبوط" : "✅ Rappel créé"}
        </span>
      ) : showRem ? (
        <div className="flex gap-1 items-center">
          <input type="number" min={1} max={365} value={days}
            onChange={(e) => setDays(Number(e.target.value))}
            className="text-xs border border-gray-300 rounded-lg px-2 py-1.5 w-14 focus:outline-none focus:ring-1 focus:ring-yellow-400"
          />
          <span className="text-xs text-gray-500">{isAr ? "يوم" : "jours"}</span>
          <button onClick={createReminder} disabled={loading === "rem"}
            className="px-2 py-1.5 rounded-lg bg-yellow-500 text-white text-xs font-medium hover:bg-yellow-600 disabled:opacity-50">
            {loading === "rem" ? "..." : isAr ? "تأكيد" : "OK"}
          </button>
          <button onClick={() => setShowRem(false)}
            className="px-2 py-1.5 rounded-lg bg-gray-200 text-gray-600 text-xs hover:bg-gray-300">
            {isAr ? "إلغاء" : "✕"}
          </button>
        </div>
      ) : (
        <button onClick={() => setShowRem(true)}
          className="px-3 py-1.5 rounded-lg border border-yellow-200 bg-yellow-50 text-yellow-700 text-xs font-medium hover:bg-yellow-100 transition">
          {isAr ? "⏰ تذكير" : "⏰ Rappel"}
        </button>
      )}

    </div>
  );
}