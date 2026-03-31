import React, { useState } from "react";
import ChatInput from "./ChatInput";

export default function Chat() {
  const [history, setHistory] = useState(["Bonjour", "Comment ça va ?"]);
  const [value, setValue] = useState("");

  // Supprimer un élément de l'historique
  const handleDeleteHistory = (idx) => {
    setHistory(prev => prev.filter((_, i) => i !== idx));
  };

  // Envoyer un message
  const handleSend = () => {
    if (!value.trim()) return;
    if (!history.includes(value)) setHistory(prev => [...prev, value]);
    console.log("Message envoyé:", value);
    setValue("");
  };

  return (
    <div className="w-full max-w-md mx-auto p-4">
      <ChatInput
        value={value}
        onChange={setValue}
        onSend={handleSend}
        disabled={false}
        dict={{ placeholder: "Écrire...", send: "Envoyer" }}
        history={history}
        onDeleteHistory={handleDeleteHistory} // 👈 connecte la suppression
      />
    </div>
  );
}
