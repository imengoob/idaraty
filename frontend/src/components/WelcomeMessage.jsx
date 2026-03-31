import React from "react";
import "./WelcomeMessage.css";

export default function WelcomeMessage({ title, subtitle }) {
  return (
    <div className="text-center">
      <div className="welcome-message">{title} 🤗</div>
      <div className="welcome-sub">{subtitle}</div>
    </div>
  );
}
