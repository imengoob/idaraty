import React from "react";
import "./TypingIndicator.css"; // assure-toi que le CSS des dots est importé

export default function TypingIndicator({ rtl }) {
  return (
    <div className={`w-full flex justify-start fade-in ${rtl ? "direction-rtl" : ""}`}>
      <div className="max-w-[72%] rounded-2xl px-4 py-2 bg-bot/20 text-text shadow-md italic flex items-center gap-2">
        <span></span> {/* optionnel pour fallback */}
        <div className="typing-dots">
          <span></span>
          <span></span>
          <span></span>
        </div>
      </div>
    </div>
  );
}
