import React, { useState } from "react";

export default function Sidebar({
  dict,
  newChat,
  conversations = [],
  onSelectConversation,
  currentConversationId,
  user,
  onOpenLogin,
  onOpenSignup,
  onLogout,
  onDeleteConversation,
  lng
}) {
  const rtl = lng !== "fr";
  const [confirmDelete, setConfirmDelete] = useState(null); // id de la conv à confirmer

  const handleDelete = (e, convId) => {
    e.stopPropagation(); // ne pas ouvrir la conversation
    setConfirmDelete(convId);
  };

  const confirmDeleteConv = (e, convId) => {
    e.stopPropagation();
    onDeleteConversation && onDeleteConversation(convId);
    setConfirmDelete(null);
  };

  const cancelDelete = (e) => {
    e.stopPropagation();
    setConfirmDelete(null);
  };

  return (
    <aside
      dir={rtl ? "rtl" : "ltr"}
      className={`w-80 bg-white flex flex-col h-full ${
        rtl ? "border-l border-gray-200 order-last" : "border-r border-gray-200"
      }`}
    >
      {/* Header */}
      <div className="p-4 border-b border-gray-200">
        <div className={`flex items-center gap-3 mb-4 ${rtl ? "flex-row-reverse" : ""}`}>
          <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-blue-500 to-cyan-500 flex items-center justify-center text-white font-bold text-xl">
            i
          </div>
          <h1 className="text-xl font-bold text-gray-900">{dict.brand}</h1>
        </div>
        <button
          onClick={newChat}
          className={`w-full flex items-center justify-center gap-2 px-4 py-3 rounded-xl bg-gradient-to-r from-blue-600 to-cyan-600 text-white font-semibold hover:from-blue-700 hover:to-cyan-700 transition-all shadow-lg hover:shadow-xl transform hover:scale-105 ${rtl ? "flex-row-reverse" : ""}`}
        >
          <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
          </svg>
          <span>{dict.newChat}</span>
        </button>
      </div>

      {/* Conversations */}
      <div className="flex-1 overflow-y-auto p-4">
        <div className="mb-3">
          <h2 className={`text-xs font-semibold text-gray-500 uppercase tracking-wider mb-2 ${rtl ? "text-right" : ""}`}>
            {dict.conversations}
          </h2>
        </div>
        <div className="space-y-2">
          {conversations.length > 0 ? (
            conversations.map((conv) => (
              <div key={conv.id} className="relative group">
                {/* Confirmation suppression */}
                {confirmDelete === conv.id ? (
                  <div className={`flex items-center gap-2 px-3 py-3 rounded-lg bg-red-50 border-2 border-red-300 ${rtl ? "flex-row-reverse" : ""}`}>
                    <span className="text-xs text-red-600 font-medium flex-1 truncate">
                      {rtl ? "حذف؟" : "Supprimer ?"}
                    </span>
                    <button
                      onClick={(e) => confirmDeleteConv(e, conv.id)}
                      className="px-2 py-1 rounded bg-red-500 text-white text-xs font-medium hover:bg-red-600"
                    >
                      {rtl ? "نعم" : "Oui"}
                    </button>
                    <button
                      onClick={cancelDelete}
                      className="px-2 py-1 rounded bg-gray-200 text-gray-600 text-xs hover:bg-gray-300"
                    >
                      {rtl ? "لا" : "Non"}
                    </button>
                  </div>
                ) : (
                  <button
                    onClick={() => onSelectConversation(conv)}
                    className={`w-full px-4 py-3 rounded-lg transition-all ${rtl ? "text-right" : "text-left"} ${
                      currentConversationId === conv.id
                        ? "bg-blue-50 border-2 border-blue-500 shadow-sm"
                        : "bg-gray-50 border-2 border-transparent hover:bg-gray-100"
                    }`}
                  >
                    <div className={`flex items-center gap-3 ${rtl ? "flex-row-reverse" : ""}`}>
                      <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-purple-400 to-pink-400 flex items-center justify-center text-white text-sm font-bold flex-shrink-0">
                        {conv.title?.[0]?.toUpperCase() || "?"}
                      </div>
                      <div className="flex-1 min-w-0">
                        <h3 className="font-medium text-gray-900 text-sm truncate">
                          {conv.title || "Sans titre"}
                        </h3>
                        <p className="text-xs text-gray-500 truncate">
                          {conv.last_message || `${conv.message_count} messages`}
                        </p>
                      </div>
                      {/* ✅ Bouton corbeille — visible au hover */}
                      <button
                        onClick={(e) => handleDelete(e, conv.id)}
                        className={`flex-shrink-0 opacity-0 group-hover:opacity-100 transition-opacity p-1 rounded hover:bg-red-100 text-gray-400 hover:text-red-500`}
                        title={rtl ? "حذف" : "Supprimer"}
                      >
                        <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2}
                            d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                        </svg>
                      </button>
                    </div>
                  </button>
                )}
              </div>
            ))
          ) : (
            <div className="text-center py-8 text-gray-400">
              <svg className="w-12 h-12 mx-auto mb-3 opacity-50" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5}
                  d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
              </svg>
              <p className="text-sm">{dict.noMessages}</p>
            </div>
          )}
        </div>
      </div>

      {/* User Section */}
      <div className="p-4 border-t border-gray-200 bg-gray-50">
        {user ? (
          <div className="space-y-3">
            <div className={`flex items-center gap-3 px-3 py-2 ${rtl ? "flex-row-reverse" : ""}`}>
              <div className="w-10 h-10 rounded-full bg-gradient-to-br from-green-400 to-blue-500 flex items-center justify-center text-white font-bold flex-shrink-0">
                {user.name?.[0]?.toUpperCase() || "U"}
              </div>
              <div className="flex-1 min-w-0">
                <div className={`font-medium text-gray-900 text-sm truncate ${rtl ? "text-right" : ""}`}>{user.name}</div>
                <div className={`text-xs text-gray-500 truncate ${rtl ? "text-right" : ""}`}>{user.email}</div>
              </div>
            </div>
            <button onClick={onLogout}
              className="w-full px-4 py-2 rounded-lg bg-red-50 text-red-600 font-medium text-sm hover:bg-red-100 transition-colors">
              {dict.logout}
            </button>
          </div>
        ) : (
          <div className="space-y-2">
            <button onClick={onOpenLogin}
              className="w-full px-4 py-2 rounded-lg border-2 border-gray-300 text-gray-700 font-medium text-sm hover:bg-gray-100 transition-colors">
              {dict.login}
            </button>
            <button onClick={onOpenSignup}
              className="w-full px-4 py-2 rounded-lg bg-blue-600 text-white font-medium text-sm hover:bg-blue-700 transition-colors">
              {dict.signup}
            </button>
          </div>
        )}
      </div>
    </aside>
  );
}