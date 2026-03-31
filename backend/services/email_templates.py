from config import settings

def _layout(content: str, lang: str = "fr") -> str:
    d = "rtl" if lang == "ar" else "ltr"
    return f"""<!DOCTYPE html><html lang="{lang}" dir="{d}">
<head><meta charset="UTF-8"><style>
body{{font-family:Arial,sans-serif;background:#f4f6f9;color:#1a1a2e;margin:0}}
.wrap{{max-width:600px;margin:0 auto;padding:24px 16px}}
.card{{background:#fff;border-radius:16px;overflow:hidden;box-shadow:0 4px 24px rgba(0,0,0,.08)}}
.hdr{{background:linear-gradient(135deg,#1e3a5f,#2563eb);padding:32px 40px;text-align:center;color:#fff}}
.hdr h1{{font-size:26px;font-weight:700;margin:0}}.hdr p{{color:#93c5fd;font-size:13px;margin:4px 0 0}}
.body{{padding:32px 40px}}.greet{{font-size:18px;font-weight:600;color:#1e3a5f;margin-bottom:14px}}
.txt{{font-size:14px;line-height:1.8;color:#374151}}
.box{{background:#eff6ff;border-left:4px solid #2563eb;border-radius:8px;padding:18px 22px;margin:20px 0}}
.box h3{{color:#1e3a5f;font-size:13px;font-weight:700;margin:0 0 8px;text-transform:uppercase}}
.box p{{font-size:13px;color:#374151;margin:0;white-space:pre-wrap;line-height:1.7}}
.btn{{display:inline-block;background:#2563eb;color:#fff;text-decoration:none;padding:12px 28px;border-radius:8px;font-weight:600;font-size:14px;margin:20px 0}}
.ftr{{background:#f9fafb;padding:20px 40px;text-align:center}}
.ftr p{{color:#9ca3af;font-size:11px;line-height:1.7;margin:0}}
</style></head><body><div class="wrap"><div class="card">{content}
<div class="ftr"><p>© 2025 iDaraty — {"جميع الحقوق محفوظة" if lang=="ar" else "Tous droits réservés"}</p></div>
</div></div></body></html>"""

def procedure_email(user_name, response, conv_id, lang="fr"):
    url = f"{settings.APP_URL}/conversation/{conv_id}"
    txt = response[:1500] + ("..." if len(response) > 1500 else "")
    if lang == "ar":
        subj = "📋 iDaraty — إجراءاتك الإدارية"
        body = f"""<div class="hdr"><h1>🏛️ iDaraty</h1><p>البوابة الإلكترونية للإدارة التونسية</p></div>
<div class="body"><p class="greet">مرحباً {user_name}،</p>
<p class="txt">فيما يلي الإجراء الإداري الذي طلبته:</p>
<div class="box"><h3>تفاصيل الإجراء</h3><p>{txt}</p></div>
<a href="{url}" class="btn">📂 عرض المحادثة الكاملة</a></div>"""
    else:
        subj = "📋 iDaraty — Votre procédure administrative"
        body = f"""<div class="hdr"><h1>🏛️ iDaraty</h1><p>Portail E-Administration Tunisienne</p></div>
<div class="body"><p class="greet">Bonjour {user_name},</p>
<p class="txt">Voici la procédure administrative que vous avez demandée :</p>
<div class="box"><h3>Détails de la procédure</h3><p>{txt}</p></div>
<a href="{url}" class="btn">📂 Voir la conversation complète</a></div>"""
    return subj, _layout(body, lang)

def reminder_email(user_name, procedure_name, days_left, lang="fr"):
    if lang == "ar":
        subj = f"⏰ iDaraty — تذكير: {procedure_name}"
        body = f"""<div class="hdr"><h1>🏛️ iDaraty</h1><p>تذكير إداري</p></div>
<div class="body"><p class="greet">مرحباً {user_name}،</p>
<div class="box"><h3>الإجراء</h3><p>{procedure_name}</p></div>
<p class="txt" style="color:#dc2626;font-weight:600">⚠️ تبقّى <strong>{days_left} يوم</strong> على الموعد.</p>
<a href="{settings.APP_URL}" class="btn">🏛️ الذهاب إلى iDaraty</a></div>"""
    else:
        subj = f"⏰ iDaraty — Rappel : {procedure_name}"
        body = f"""<div class="hdr"><h1>🏛️ iDaraty</h1><p>Rappel automatique</p></div>
<div class="body"><p class="greet">Bonjour {user_name},</p>
<div class="box"><h3>Procédure concernée</h3><p>{procedure_name}</p></div>
<p class="txt" style="color:#dc2626;font-weight:600">⚠️ Il reste <strong>{days_left} jour(s)</strong> avant l'échéance.</p>
<a href="{settings.APP_URL}" class="btn">🏛️ Aller sur iDaraty</a></div>"""
    return subj, _layout(body, lang)

def welcome_email(user_name, lang="fr"):
    if lang == "ar":
        subj = "🎉 مرحباً بك في iDaraty"
        body = f"""<div class="hdr"><h1>🏛️ iDaraty</h1><p>مرحباً بك!</p></div>
<div class="body"><p class="greet">مرحباً {user_name}! 🎉</p>
<div class="box"><h3>ماذا يمكنك أن تفعل؟</h3>
<p>📋 الاستعلام عن الإجراءات\n📄 تحميل الاستمارات\n🗺️ تحديد مواقع المؤسسات\n📧 استلام الإجراءات بالبريد</p></div>
<a href="{settings.APP_URL}" class="btn">🚀 ابدأ الاستخدام</a></div>"""
    else:
        subj = "🎉 Bienvenue sur iDaraty !"
        body = f"""<div class="hdr"><h1>🏛️ iDaraty</h1><p>Bienvenue!</p></div>
<div class="body"><p class="greet">Bienvenue {user_name} ! 🎉</p>
<div class="box"><h3>Ce que vous pouvez faire</h3>
<p>📋 Consulter les procédures\n📄 Télécharger les formulaires\n🗺️ Localiser les établissements\n📧 Recevoir les procédures par email</p></div>
<a href="{settings.APP_URL}" class="btn">🚀 Commencer</a></div>"""
    return subj, _layout(body, lang)