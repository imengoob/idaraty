"""
Export conversation en PDF professionnel
pip install reportlab arabic-reshaper python-bidi
"""
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.colors import HexColor, white
from reportlab.lib.units import mm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, HRFlowable, Table, TableStyle
from reportlab.lib.enums import TA_LEFT, TA_RIGHT, TA_CENTER
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from datetime import datetime
import io
import os

# ── Enregistrer police Arabic (Tahoma ou Arial Unicode inclus dans Windows) ──
def _register_arabic_font():
    """Chercher une police supportant l'arabe sur Windows"""
    fonts_to_try = [
        ("Tahoma",    r"C:\Windows\Fonts\tahoma.ttf"),
        ("Arial",     r"C:\Windows\Fonts\arial.ttf"),
        ("TimesNR",   r"C:\Windows\Fonts\times.ttf"),
    ]
    for name, path in fonts_to_try:
        if os.path.exists(path):
            try:
                pdfmetrics.registerFont(TTFont(name, path))
                return name
            except Exception:
                continue
    return "Helvetica"  # fallback sans arabe

ARABIC_FONT = _register_arabic_font()

def _fix_arabic(text: str) -> str:
    """Reshaper le texte arabe pour l'affichage correct RTL"""
    try:
        import arabic_reshaper
        from bidi.algorithm import get_display
        reshaped = arabic_reshaper.reshape(text)
        return get_display(reshaped)
    except ImportError:
        return text

def _process_text(text: str) -> str:
    """Détecter si arabe et traiter en conséquence"""
    arabic_chars = sum(1 for c in text if '\u0600' <= c <= '\u06FF')
    if arabic_chars > 3:
        return _fix_arabic(text)
    return text

def export_conversation_pdf(messages: list, title: str,
                             user_name: str, lang: str = "fr") -> bytes:
    buffer  = io.BytesIO()
    page_w, page_h = A4

    doc = SimpleDocTemplate(
        buffer, pagesize=A4,
        leftMargin=20*mm, rightMargin=20*mm,
        topMargin=20*mm, bottomMargin=20*mm,
        title=title, author="iDaraty"
    )

    BLUE_DARK  = HexColor("#1e3a5f")
    BLUE_MID   = HexColor("#2563eb")
    BLUE_LIGHT = HexColor("#eff6ff")
    GRAY_BG    = HexColor("#f3f4f6")
    GRAY_TEXT  = HexColor("#374151")
    GRAY_MUTED = HexColor("#9ca3af")

    date_str = datetime.now().strftime("%d/%m/%Y %H:%M")
    is_ar    = lang == "ar"

    style_header_title = ParagraphStyle("HT", fontSize=18, fontName=ARABIC_FONT,
        textColor=white, alignment=TA_CENTER, spaceAfter=2)
    style_header_sub = ParagraphStyle("HS", fontSize=10, fontName=ARABIC_FONT,
        textColor=HexColor("#93c5fd"), alignment=TA_CENTER)
    style_meta = ParagraphStyle("HM", fontSize=9, fontName=ARABIC_FONT,
        textColor=GRAY_MUTED, alignment=TA_CENTER)
    style_user_label = ParagraphStyle("UL", fontSize=9, fontName=ARABIC_FONT,
        textColor=HexColor("#374151"))
    style_bot_label = ParagraphStyle("BL", fontSize=9, fontName=ARABIC_FONT,
        textColor=BLUE_MID)
    style_time = ParagraphStyle("TM", fontSize=8, fontName=ARABIC_FONT,
        textColor=GRAY_MUTED, alignment=TA_RIGHT)
    style_content = ParagraphStyle("CO", fontSize=11, fontName=ARABIC_FONT,
        textColor=GRAY_TEXT, leading=16, spaceAfter=4)
    style_footer = ParagraphStyle("FT", fontSize=8, fontName=ARABIC_FONT,
        textColor=GRAY_MUTED, alignment=TA_CENTER)

    ul = f"{'المستخدم' if is_ar else 'Utilisateur'}: {user_name}   |   {'التاريخ' if is_ar else 'Date'}: {date_str}"
    sub_txt = "البوابة الإلكترونية للإدارة التونسية" if is_ar else "Portail E-Administration Tunisienne"
    footer_txt = f"iDaraty © 2025 — {sub_txt}"

    story = []

    # ── En-tête ──
    header_table = Table([
        [Paragraph("iDaraty", style_header_title)],
        [Paragraph(sub_txt, style_header_sub)],
        [Paragraph(ul, style_meta)],
    ], colWidths=[page_w - 40*mm])
    header_table.setStyle(TableStyle([
        ("BACKGROUND",    (0,0), (-1,-1), BLUE_DARK),
        ("TOPPADDING",    (0,0), (-1,-1), 10),
        ("BOTTOMPADDING", (0,0), (-1,-1), 8),
        ("LEFTPADDING",   (0,0), (-1,-1), 16),
        ("RIGHTPADDING",  (0,0), (-1,-1), 16),
    ]))
    story.append(header_table)
    story.append(Spacer(1, 4*mm))

    # ── Titre conversation ──
    story.append(Paragraph(_process_text(title), ParagraphStyle(
        "CT", fontSize=13, fontName=ARABIC_FONT,
        textColor=BLUE_DARK, spaceAfter=4
    )))
    story.append(HRFlowable(width="100%", thickness=1,
        color=HexColor("#e5e7eb"), spaceAfter=4*mm))

    # ── Messages ──
    for msg in messages:
        role    = msg.get("role", "user")
        content = msg.get("content", "")
        time    = msg.get("created_at", "")[:16]
        is_user = role == "user"

        bg      = GRAY_BG if is_user else BLUE_LIGHT
        label   = ("أنت" if is_ar else "Vous") if is_user else "iDaraty"
        l_style = style_user_label if is_user else style_bot_label
        border  = HexColor("#d1d5db") if is_user else BLUE_MID

        # Traiter le texte arabe
        safe = _process_text(content)
        safe = safe.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
        safe = safe[:3000] + ("..." if len(safe) > 3000 else "")

        msg_table = Table([
            [Paragraph(label, l_style), Paragraph(time, style_time)],
            [Paragraph(safe, style_content), ""],
        ], colWidths=[page_w - 50*mm, 40*mm])

        msg_table.setStyle(TableStyle([
            ("BACKGROUND",    (0,0), (-1,-1), bg),
            ("TOPPADDING",    (0,0), (-1,-1), 8),
            ("BOTTOMPADDING", (0,0), (-1,-1), 8),
            ("LEFTPADDING",   (0,0), (-1,-1), 10),
            ("RIGHTPADDING",  (0,0), (-1,-1), 10),
            ("LINEBEFORE",    (0,0), (0,-1), 3, border),
            ("SPAN",          (0,1), (1,1)),
            ("VALIGN",        (0,0), (-1,-1), "TOP"),
        ]))
        story.append(msg_table)
        story.append(Spacer(1, 3*mm))

    # ── Pied de page ──
    story.append(Spacer(1, 4*mm))
    story.append(HRFlowable(width="100%", thickness=0.5,
        color=HexColor("#e5e7eb"), spaceAfter=3*mm))
    story.append(Paragraph(footer_txt, style_footer))

    doc.build(story)
    buffer.seek(0)
    return buffer.read()