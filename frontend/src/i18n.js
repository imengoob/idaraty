export const LOCALES = {
  FR: "fr",
  AR: "ar",
  TN: "tn"
};

const dict = {
  fr: {
    brand: "iDaraty Tunisie",
    hi: "Bonjour !",
    sub: "Comment puis-je vous aider avec les procédures administratives tunisiennes ?",
    signup: "S'inscrire",
    login: "Se connecter",
    logout: "Déconnexion",
    langSwitch: "بالعربية",
    send: "Envoyer",
    typing: "En train d'écrire...",
    newChat: "Nouvelle conversation",
    conversations: "Conversations",
    placeholder: "Posez votre question sur les procédures administratives...",
    placeholders: {
      name: "Nom complet",
      email: "Adresse email",
      password: "Mot de passe"
    },
    noMessages: "Aucun message pour le moment",
    errorAuth: "Erreur d'authentification",
    errorSend: "Erreur lors de l'envoi",
  },

  ar: {
    brand: "إداراتي تونس",
    hi: "مرحبا!",
    sub: "كيف يمكنني مساعدتك في الإجراءات الإدارية التونسية؟",
    signup: "إنشاء حساب",
    login: "تسجيل الدخول",
    logout: "تسجيل الخروج",
    langSwitch: "Français",
    send: "إرسال",
    typing: "جاري الكتابة...",
    newChat: "محادثة جديدة",
    conversations: "المحادثات",
    placeholder: "اطرح سؤالك حول الإجراءات الإدارية...",
    placeholders: {
      name: "الاسم الكامل",
      email: "البريد الإلكتروني",
      password: "كلمة المرور"
    },
    noMessages: "لا توجد رسائل حتى الآن",
    errorAuth: "خطأ في المصادقة",
    errorSend: "خطأ في الإرسال",
  },

  tn: {
    brand: "iDaraty تونس",
    hi: "أهلا و سهلا!",
    sub: "شنية نجم نعاونك في الإجراءات الإدارية التونسية؟",
    signup: "سجّل مجانًا",
    login: "دخول",
    logout: "خروج",
    langSwitch: "Français",
    send: "ابعث",
    typing: "قاعد يكتب...",
    newChat: "محادثة جديدة",
    conversations: "المحادثات",
    placeholder: "اسأل على الإجراءات الإدارية...",
    placeholders: {
      name: "الاسم",
      email: "الإيمايل",
      password: "الباسوورد"
    },
    noMessages: "ما فماش رسائل للحظة",
    errorAuth: "غلطة في الدخول",
    errorSend: "غلطة في البعث",
  }
};

export const t = (lng, key) => {
  const keys = key.split('.');
  let value = dict[lng];
  for (const k of keys) {
    value = value?.[k];
  }
  return value ?? dict.fr[key];
};

export const tf = (lng) => dict[lng] ?? dict.fr;