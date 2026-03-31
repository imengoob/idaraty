import React, { useState, useRef, useEffect } from "react";

/**
 * VoiceButton — reconnaissance vocale basée sur la langue de l'interface
 *
 * Logique simple et fiable :
 *   - Interface FR  → reconnaissance fr-FR uniquement
 *   - Interface AR/TN → reconnaissance ar-TN uniquement
 *
 * Plus de double reconnaissance — le navigateur sait exactement
 * quelle langue écouter selon le bouton de langue choisi par l'utilisateur.
 *
 * Props :
 *   onResult(text)   — appelé avec le texte transcrit
 *   lang             — "fr" | "ar" | "tn" — langue active de l'interface
 *   disabled         — désactiver pendant le chargement
 */
export default function VoiceButton({ onResult, lang = "fr", disabled = false }) {
  const [listening, setListening] = useState(false);
  const [error,     setError]     = useState(null);
  const [supported, setSupported] = useState(true);
  const recogRef = useRef(null);

  // ── Vérifier support navigateur ──────────────────────────────────────────
  useEffect(() => {
    const SR = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (!SR) setSupported(false);
  }, []);

  // ── Langue de reconnaissance selon la langue de l'interface ──────────────
  // fr → fr-FR | ar ou tn → ar-TN
  const getLangCode = () => (lang === "fr" ? "fr-FR" : "ar-TN");

  // ── Démarrer / Arrêter ────────────────────────────────────────────────────
  const toggleListening = () => {
    if (listening) stopListening();
    else           startListening();
  };

  const startListening = () => {
    const SR = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (!SR) { setSupported(false); return; }

    setError(null);

    const recognition = new SR();
    recogRef.current  = recognition;

    recognition.lang            = getLangCode();
    recognition.continuous      = false;
    recognition.interimResults  = false;
    recognition.maxAlternatives = 1;

    recognition.onstart  = () => setListening(true);

    recognition.onresult = (event) => {
      const transcript = event.results[0][0].transcript.trim();
      if (transcript) onResult(transcript);
      setListening(false);
    };

    recognition.onerror = (event) => {
      if (event.error === "no-speech") {
        setError(lang === "fr" ? "Aucune voix détectée" : "لم يتم اكتشاف صوت");
      } else if (event.error === "not-allowed") {
        setError(lang === "fr"
          ? "Microphone bloqué — autoriser dans le navigateur"
          : "الميكروفون محظور — يُرجى السماح به");
      } else {
        setError(`Erreur : ${event.error}`);
      }
      setListening(false);
    };

    recognition.onend = () => setListening(false);

    try { recognition.start(); }
    catch (e) {
      setError(lang === "fr" ? "Impossible de démarrer" : "تعذّر بدء التسجيل");
      setListening(false);
    }
  };

  const stopListening = () => {
    if (recogRef.current) {
      recogRef.current.stop();
      recogRef.current = null;
    }
    setListening(false);
  };

  // ── Nettoyer au démontage ─────────────────────────────────────────────────
  useEffect(() => () => stopListening(), []);

  if (!supported) return null;

  const isAr = lang !== "fr";
  const langLabel = lang === "fr" ? "FR" : "AR";

  const tooltip = listening
    ? (isAr ? "انقر للإيقاف"        : "Cliquer pour arrêter")
    : (isAr ? "انقر للتحدث بالعربية" : "Parler en français");

  return (
    <div className="relative flex items-center">

      {/* ── Bouton microphone ── */}
      <button
        type="button"
        onClick={toggleListening}
        disabled={disabled}
        title={tooltip}
        className={`
          relative flex items-center justify-center
          w-10 h-10 rounded-full transition-all duration-200
          focus:outline-none focus:ring-2 focus:ring-offset-1
          disabled:opacity-40 disabled:cursor-not-allowed
          ${listening
            ? "bg-red-500 hover:bg-red-600 text-white shadow-lg focus:ring-red-400"
            : "bg-gray-100 hover:bg-blue-50 text-gray-500 hover:text-blue-600 border border-gray-200 hover:border-blue-300 focus:ring-blue-400"
          }
        `}
      >
        {listening ? (
          <svg className="w-5 h-5" viewBox="0 0 24 24" fill="currentColor">
            <rect x="6" y="6" width="12" height="12" rx="2"/>
          </svg>
        ) : (
          <svg className="w-5 h-5" viewBox="0 0 24 24" fill="none"
            stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
            <path d="M12 1a3 3 0 0 0-3 3v8a3 3 0 0 0 6 0V4a3 3 0 0 0-3-3z"/>
            <path d="M19 10v2a7 7 0 0 1-14 0v-2"/>
            <line x1="12" y1="19" x2="12" y2="23"/>
            <line x1="8"  y1="23" x2="16" y2="23"/>
          </svg>
        )}

        {listening && (
          <span className="absolute inset-0 rounded-full bg-red-400 opacity-40 animate-ping"/>
        )}
      </button>

      {/* ── Badge langue (FR ou AR) ── */}
      {!listening && !error && (
        <span className="
          absolute -top-2 -right-1
          text-[9px] font-bold px-1 rounded
          bg-blue-100 text-blue-600
          pointer-events-none select-none
        ">
          {langLabel}
        </span>
      )}

      {/* ── Tooltip écoute en cours ── */}
      {listening && (
        <div className="
          absolute bottom-12 left-1/2 -translate-x-1/2
          bg-red-600 text-white text-xs px-3 py-1.5
          rounded-lg whitespace-nowrap shadow-lg pointer-events-none z-10
        ">
          {isAr ? "🎙️ جارٍ الاستماع بالعربية…" : "🎙️ Écoute en français…"}
          <div className="absolute top-full left-1/2 -translate-x-1/2 border-4 border-transparent border-t-red-600"/>
        </div>
      )}

      {/* ── Message d'erreur ── */}
      {error && (
        <div
          onClick={() => setError(null)}
          className="
            absolute bottom-12 left-1/2 -translate-x-1/2
            bg-orange-500 text-white text-xs px-3 py-1.5
            rounded-lg whitespace-nowrap shadow-lg z-10 cursor-pointer
          "
        >
          ⚠️ {error}
          <div className="absolute top-full left-1/2 -translate-x-1/2 border-4 border-transparent border-t-orange-500"/>
        </div>
      )}

    </div>
  );
}