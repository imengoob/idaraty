import { useState } from "react";

export default function AuthModal({ open, onClose, mode = "login", onSubmit, dict }) {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [name, setName] = useState("");

  if (!open) return null;

  const submit = () => onSubmit({ email, password, name });

  return (
    <div className="fixed inset-0 z-50 grid place-items-center bg-black/50">
      <div className="w-full max-w-md bg-white rounded-2xl p-6 shadow-xl">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-lg font-semibold">{mode === "login" ? dict.login : dict.signup}</h3>
          <button onClick={onClose} className="px-3 py-1 rounded-md bg-gray-100">✕</button>
        </div>
        {mode === "signup" && (
          <input className="w-full mb-3 border rounded-md px-3 py-2" placeholder={dict.placeholders.name} value={name} onChange={e=>setName(e.target.value)} />
        )}
        <input className="w-full mb-3 border rounded-md px-3 py-2" placeholder={dict.placeholders.email}  type="email" value={email} onChange={e=>setEmail(e.target.value)} />
        <input className="w-full mb-4 border rounded-md px-3 py-2" placeholder={dict.placeholders.password}  type="password" value={password} onChange={e=>setPassword(e.target.value)} />
        <button onClick={submit} className="w-full py-2 rounded-xl bg-accent text-[#04202a] font-semibold">
          {mode === "login" ? dict.login : dict.signup}
        </button>
      </div>
    </div>
  );
}