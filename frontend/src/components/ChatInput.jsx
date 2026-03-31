import React from "react";
import VoiceButton from "./VoiceButton";

/**
 * ChatInput — barre de saisie avec bouton vocal intégré
 *
 * Props :
 *   value, onChange, onSend, disabled, dict, rtl, lang
 *
 * Changements vs ancienne version :
 *   - Import VoiceButton
 *   - onVoiceResult : injecte le texte transcrit dans l'input
 *   - VoiceButton placé entre l'input et le bouton Envoyer
 *   - Ordre RTL géré (flex-row-reverse en arabe)
 */
export default function ChatInput({
  value,
  onChange,
  onSend,
  disabled,
  dict,
  rtl = false,
  lang = "fr",
}) {
  // Quand la reconnaissance vocale retourne un texte :
  // on l'injecte dans l'input ET on envoie automatiquement
  const handleVoiceResult = (transcript) => {
    onChange(transcript);          // remplir l'input
    // Envoyer après un petit délai (le temps que l'état se mette à jour)
    setTimeout(() => {
      if (transcript.trim()) {
        onSend(transcript);        // envoyer directement
      }
    }, 100);
  };

  const handleKeyDown = (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      onSend();
    }
  };

  return (
    <div
      className={`flex items-center gap-2 ${rtl ? "flex-row-reverse" : ""}`}
      dir={rtl ? "rtl" : "ltr"}
    >
      {/* ── Zone de saisie texte ────────────────────────────────────────── */}
      <input
        type="text"
        value={value}
        onChange={(e) => onChange(e.target.value)}
        onKeyDown={handleKeyDown}
        placeholder={dict?.placeholder || "Posez votre question…"}
        disabled={disabled}
        dir={rtl ? "rtl" : "ltr"}
        className={`
          flex-1 px-4 py-3 rounded-xl
          border border-gray-300 bg-white
          text-gray-800 placeholder-gray-400
          focus:outline-none focus:ring-2 focus:ring-blue-400 focus:border-transparent
          disabled:opacity-50 disabled:cursor-not-allowed
          transition-all text-base
          ${rtl ? "text-right" : "text-left"}
        `}
      />

      {/* ── Bouton microphone (vocal FR/AR) ─────────────────────────────── */}
      <div className="group relative">
        <VoiceButton
          onResult={handleVoiceResult}
          lang={lang}
          disabled={disabled}
        />
      </div>

      {/* ── Bouton Envoyer ──────────────────────────────────────────────── */}
      <button
        onClick={onSend}
        disabled={disabled || !value.trim()}
        className={`
          px-5 py-3 rounded-xl font-semibold text-white
          bg-gradient-to-r from-blue-600 to-cyan-600
          hover:from-blue-700 hover:to-cyan-700
          disabled:opacity-50 disabled:cursor-not-allowed
          transition-all shadow-md hover:shadow-lg
          transform hover:scale-105 active:scale-95
          flex items-center gap-2
        `}
      >
        <span>{dict?.send || (rtl ? "إرسال" : "Envoyer")}</span>
        <svg
          className={`w-4 h-4 ${rtl ? "rotate-180" : ""}`}
          fill="none" stroke="currentColor" strokeWidth="2"
          viewBox="0 0 24 24" strokeLinecap="round" strokeLinejoin="round"
        >
          <line x1="22" y1="2" x2="11" y2="13"/>
          <polygon points="22 2 15 22 11 13 2 9 22 2"/>
        </svg>
      </button>
    </div>
  );
}