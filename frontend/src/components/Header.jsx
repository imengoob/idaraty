import React from "react";
import logo from "../assets/react.svg";

export default function Header({
  lng,
  dict,
  onLangToggle = () => {},
  onOpenLogin = () => {},
  onOpenSignup = () => {},
  user = null,
  onLogout = () => {}
}) {
  const rtl = lng !== "fr";

  return (
    <header
      className={`w-full flex items-center justify-between px-6 py-3 bg-white/0 sticky top-0 z-40`}
    >
      <div className="flex items-center gap-3">
        <img src={logo} alt={dict.brand} className="w-9 h-9 rounded-xl" />
        <h1 className="text-lg font-semibold">{dict.brand}</h1>
      </div>

      <div className="flex items-center gap-3">
        {/* Language toggle */}
        <button
          onClick={onLangToggle}
          className="px-3 py-1 rounded-full bg-gray-400 hover:bg-gray-400 text-white text-sm"
          title="Changer la langue"
        >
          {lng === "fr" ? dict.langSwitchToAR ?? "بالتونسي" : dict.langSwitchToFR ?? "Français"}
        </button>

        {/* If user logged in: show avatar + name + logout, else show login / signup */}
        {user ? (
          <div className="flex items-center gap-2">
            <div className="w-8 h-8 rounded-full bg-blue-600/10 text-blue-700 flex items-center justify-center font-medium">
              {user.name?.[0]?.toUpperCase() || "U"}
            </div>
            <div className="hidden sm:block text-sm">
              <div className="font-medium">{user.name || user.email}</div>
            </div>
            <button
              onClick={onLogout}
              className="ml-2 px-3 py-1 rounded-md bg-red-50 text-red-600 border border-red-100 text-sm hover:bg-red-100"
            >
              {dict.logout ?? "Déconnexion"}
            </button>
          </div>
        ) : (
          <div className="flex items-center gap-2">
            <button
              onClick={onOpenLogin}
              className="px-3 py-1 rounded-full bg-gray-400 hover:bg-gray-400 text-white text-sm"
            >
              {dict.login ?? "Se connecter"}
            </button>
            <button
              onClick={onOpenSignup}
              className="px-3 py-1 rounded-md bg-blue-600 text-white text-sm hover:bg-blue-700"
            >
              {dict.signup ?? "S'inscrire"}
            </button>
          </div>
        )}
      </div>
    </header>
  );
}
