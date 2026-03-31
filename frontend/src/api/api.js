const BASE_URL = import.meta.env.VITE_BACKEND_URL || "http://localhost:8000";

export async function signup(name, email, password) {
  const r = await fetch(`${BASE_URL}/auth/register`, { method:"POST", headers:{"Content-Type":"application/json"}, body:JSON.stringify({name,email,password}) });
  if (!r.ok) { const e=await r.json(); throw new Error(e.detail||"Erreur inscription"); }
  return r.json();
}
export async function login(email, password) {
  const r = await fetch(`${BASE_URL}/auth/login`, { method:"POST", headers:{"Content-Type":"application/json"}, body:JSON.stringify({email,password}) });
  if (!r.ok) { const e=await r.json(); throw new Error(e.detail||"Identifiants invalides"); }
  return r.json();
}
export async function sendMessage(question, conversationId, language, token) {
  const r = await fetch(`${BASE_URL}/chat/ask`, {
    method:"POST",
    headers:{"Content-Type":"application/json","Authorization":`Bearer ${token}`},
    body:JSON.stringify({question,conversation_id:conversationId,language})
  });
  if (!r.ok) { const e=await r.json(); throw new Error(e.detail||"Erreur envoi"); }
  return r.json();
}
export const searchPlaces = async (placeType, city="", userLat=null, userLon=null) => {
  const r = await fetch(`${BASE_URL}/maps/search`, { method:"POST", headers:{"Content-Type":"application/json"}, body:JSON.stringify({place_type:placeType,city,user_lat:userLat,user_lon:userLon}) });
  if (!r.ok) throw new Error("Erreur recherche maps");
  return r.json();
};
export async function saveMapsConversation({question,mapsResponse,mapsResults,placeType,city,resultsCount,conversationId,language,token}) {
  const r = await fetch(`${BASE_URL}/chat/save-maps`, {
    method:"POST",
    headers:{"Content-Type":"application/json","Authorization":`Bearer ${token}`},
    body:JSON.stringify({question,maps_response:mapsResponse,maps_results:mapsResults||[],place_type:placeType,city,results_count:resultsCount,conversation_id:conversationId,language})
  });
  if (!r.ok) { const e=await r.json(); throw new Error(e.detail||"Erreur sauvegarde maps"); }
  return r.json();
}
export async function getConversations(token) {
  const r = await fetch(`${BASE_URL}/history/conversations`, { headers:{"Authorization":`Bearer ${token}`} });
  if (!r.ok) throw new Error("Erreur conversations");
  return r.json();
}
export async function getConversationMessages(conversationId, token) {
  const r = await fetch(`${BASE_URL}/history/conversation/${conversationId}`, { headers:{"Authorization":`Bearer ${token}`} });
  if (!r.ok) throw new Error("Erreur messages");
  return r.json();
}
// Ajouter cette fonction dans frontend/src/api/api.js

export async function deleteConversation(conversationId, token) {
  const response = await fetch(
    `${BASE_URL}/history/conversation/${conversationId}`,
    {
      method: "DELETE",
      headers: { Authorization: `Bearer ${token}` },
    }
  );
  if (!response.ok) throw new Error("Erreur suppression conversation");
  return response.json();
}