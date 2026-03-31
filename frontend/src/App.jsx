import React, { useEffect, useMemo, useState, useRef } from "react";
import Sidebar from "./components/Sidebar.jsx";
import Header from "./components/Header.jsx";
import MessageBubble from "./components/MessageBubble.jsx";
import ChatInput from "./components/ChatInput.jsx";
import TypingIndicator from "./components/TypingIndicator.jsx";
import WelcomeMessage from "./components/WelcomeMessage.jsx";
import AuthModal from "./components/AuthModal.jsx";
import {
  sendMessage, login, signup,
  getConversations, getConversationMessages,
  deleteConversation
} from "./api/api.js";
import { LOCALES, tf } from "./i18n.js";

const detectLanguage = (t) => ((t.match(/[\u0600-\u06FF]/g)||[]).length > 3 ? "ar" : "fr");

export default function App() {
  const [lng, setLng]   = useState(localStorage.getItem("lng") || LOCALES.FR);
  const dict            = useMemo(() => tf(lng), [lng]);
  const [messages, setMessages]           = useState([]);
  const [input, setInput]                 = useState("");
  const [loading, setLoading]             = useState(false);
  const [authOpen, setAuthOpen]           = useState(null);
  const [user,  setUser]  = useState(() => JSON.parse(localStorage.getItem("user") || "null"));
  const [token, setToken] = useState(() => localStorage.getItem("token") || "");
  const [conversations, setConversations] = useState([]);
  const [currentConversationId, setCurrentConversationId] = useState(null);
  const conversationIdRef = useRef(null);
  const messagesEndRef    = useRef(null);
  const rtl = lng !== LOCALES.FR;

  useEffect(() => { conversationIdRef.current = currentConversationId; }, [currentConversationId]);
  useEffect(() => { localStorage.setItem("lng", lng); }, [lng]);
  useEffect(() => {
    if (token && user) loadConversations();
    else { setConversations([]); setMessages([]); setCurrentConversationId(null); }
  }, [token, user]);
  useEffect(() => { messagesEndRef.current?.scrollIntoView({ behavior: "smooth" }); }, [messages]);

  const loadConversations = async () => {
    try { setConversations(await getConversations(token)); } catch (e) { console.error(e); }
  };

  const loadConversationMessages = async (conversationId) => {
    try {
      const data = await getConversationMessages(conversationId, token);
      const restored = data.messages.map((msg) => {
        let mapData = null, docData = null, route = "rag";
        if (msg.maps_data) {
          const p = msg.maps_data;
          if (p.type === "maps") {
            mapData = { results: p.results, placeType: p.place_type, city: p.city };
            route   = "maps";
          } else if (p.type === "documents") {
            docData = p.results;
            route   = "documents";
          }
        }
        return { role: msg.role, text: msg.content, mapData, docData, route };
      });
      setMessages(restored);
      setCurrentConversationId(conversationId);
      conversationIdRef.current = conversationId;
    } catch (e) { console.error(e); }
  };

  // ✅ Supprimer une conversation
  const handleDeleteConversation = async (convId) => {
    try {
      await deleteConversation(convId, token);
      if (currentConversationId === convId) {
        setMessages([]);
        setCurrentConversationId(null);
        conversationIdRef.current = null;
      }
      await loadConversations();
    } catch (e) { console.error("Erreur suppression:", e); }
  };

  const onLangToggle = () => setLng(lng === LOCALES.FR ? LOCALES.TN : LOCALES.FR);

  const doLogin = async ({ email, password }) => {
    try {
      const r = await login(email, password);
      setUser(r.user); setToken(r.access_token);
      localStorage.setItem("user", JSON.stringify(r.user));
      localStorage.setItem("token", r.access_token);
      setAuthOpen(null); await loadConversations();
    } catch (e) { alert(e.message); }
  };

  const doSignup = async ({ name, email, password }) => {
    try {
      const r = await signup(name, email, password);
      setUser(r.user); setToken(r.access_token);
      localStorage.setItem("user", JSON.stringify(r.user));
      localStorage.setItem("token", r.access_token);
      setAuthOpen(null); await loadConversations();
    } catch (e) { alert(e.message); }
  };

  const logout = () => {
    setUser(null); setToken(""); setMessages([]);
    setConversations([]); setCurrentConversationId(null);
    conversationIdRef.current = null;
    localStorage.removeItem("user"); localStorage.removeItem("token");
  };

  const newChat = () => {
    setMessages([]); setInput("");
    setCurrentConversationId(null);
    conversationIdRef.current = null;
  };

  const handleSendMessage = async () => {
    if (!input.trim()) return;
    if (!token) { alert(dict.errorAuth); setAuthOpen("login"); return; }

    const question     = input;
    const questionLang = detectLanguage(question);
    setMessages((prev) => [...prev, { text: question, role: "user", route: "user" }]);
    setInput("");
    setLoading(true);

    try {
      const data  = await sendMessage(question, conversationIdRef.current, questionLang, token);
      const route = data.route || "rag";

      if (!conversationIdRef.current && data.conversation_id) {
        conversationIdRef.current = data.conversation_id;
        setCurrentConversationId(data.conversation_id);
        await loadConversations();
      }

      const convId = conversationIdRef.current || data.conversation_id;

      if (route === "documents") {
        setMessages((prev) => [...prev, {
          role: "assistant", text: data.response, route,
          docData: data.documents || [], mapData: null, convId,
        }]);
      } else if (route === "maps") {
        setMessages((prev) => [...prev, {
          role: "assistant", text: data.response, route,
          mapData: data.maps_results?.length
            ? { results: data.maps_results, placeType: data.place_type, city: data.city }
            : null,
          docData: null, convId,
        }]);
      } else {
        setMessages((prev) => [...prev, {
          role: "assistant", text: data.response, route,
          mapData: null, docData: null, convId,
        }]);
      }

    } catch (error) {
      setMessages((prev) => [...prev, {
        role: "assistant", route: "rag",
        text: `${dict.errorSend}: ${error.message}`,
        convId: conversationIdRef.current,
      }]);
    } finally {
      setLoading(false);
    }
  };

  const activeLang = lng === LOCALES.FR ? "fr" : "ar";

  return (
    <div className="flex h-screen bg-gradient-to-br from-blue-50 via-white to-cyan-50 overflow-hidden">
      <Sidebar
        dict={dict} newChat={newChat} conversations={conversations}
        onSelectConversation={(conv) => loadConversationMessages(conv.id)}
        onDeleteConversation={handleDeleteConversation}
        currentConversationId={currentConversationId}
        user={user} onOpenLogin={() => setAuthOpen("login")}
        onOpenSignup={() => setAuthOpen("signup")} onLogout={logout}
        onLangToggle={onLangToggle} lng={lng}
      />
      <div className="flex-1 flex flex-col overflow-hidden">
        <Header lng={lng} dict={dict} onLangToggle={onLangToggle}
          user={user} onOpenLogin={() => setAuthOpen("login")}
          onOpenSignup={() => setAuthOpen("signup")} onLogout={logout}
        />
        <div className="flex-1 overflow-y-auto px-4 md:px-8 py-6">
          <div className="max-w-4xl mx-auto space-y-4">
            {messages.length === 0 ? (
              <WelcomeMessage title={dict.hi} subtitle={dict.sub} />
            ) : (
              messages.map((m, i) => (
                <MessageBubble
                  key={i} role={m.role} text={m.text} rtl={rtl}
                  mapData={m.mapData} docData={m.docData}
                  route={m.route || "rag"}
                  conversationId={m.convId || currentConversationId}
                  token={token}
                  isLastAssistant={m.role === "assistant" && i === messages.length - 1}
                  lang={activeLang}
                />
              ))
            )}
            {loading && <TypingIndicator dict={dict} rtl={rtl} />}
            <div ref={messagesEndRef} />
          </div>
        </div>
        <div className="border-t border-gray-200 bg-white/80 backdrop-blur-sm px-4 md:px-8 py-4">
          <div className="max-w-4xl mx-auto">
            <ChatInput value={input} onChange={setInput} onSend={handleSendMessage}
              disabled={loading} dict={dict} rtl={rtl} lang={activeLang} />
          </div>
        </div>
      </div>
      {authOpen && (
        <AuthModal open={true} onClose={() => setAuthOpen(null)} mode={authOpen}
          onSubmit={authOpen === "login" ? doLogin : doSignup} dict={dict} />
      )}
    </div>
  );
}