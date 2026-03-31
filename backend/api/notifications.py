from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional
from datetime import datetime, timedelta
import io

from database import get_db
from auth.utils import decode_token
from models import (User, Conversation, Message, Notification, NotificationPreference,
                    Reminder, NotificationType, NotificationStatus, ReminderStatus)
from services.brevo_service import brevo_service
from services.email_templates import procedure_email
from services.pdf_service import export_conversation_pdf

router = APIRouter(prefix="/notifications", tags=["Notifications"])

# ── Schemas ──────────────────────────────────────────────
class SendEmailReq(BaseModel):
    conversation_id: int
    message_id: Optional[int] = None

class SendSMSReq(BaseModel):
    conversation_id: int
    phone: Optional[str] = None

class UpdatePrefsReq(BaseModel):
    email_enabled: Optional[bool] = None
    sms_enabled: Optional[bool] = None
    phone: Optional[str] = None
    reminder_enabled: Optional[bool] = None
    language: Optional[str] = None

class CreateReminderReq(BaseModel):
    conversation_id: int
    procedure_name: str
    remind_in_days: int = 90
    type: str = "email"

# ── Helper ────────────────────────────────────────────────
def _get_prefs(user_id, db):
    p = db.query(NotificationPreference).filter_by(user_id=user_id).first()
    if not p:
        p = NotificationPreference(user_id=user_id)
        db.add(p); db.commit(); db.refresh(p)
    return p

def _log(db, user_id, conv_id, ntype, subject, content, status, error=None):
    db.add(Notification(user_id=user_id, conversation_id=conv_id, type=ntype,
        subject=subject, content=content, status=status,
        sent_at=datetime.utcnow() if status==NotificationStatus.sent else None,
        error_message=error))
    db.commit()

# ── Endpoints ─────────────────────────────────────────────

@router.post("/send-email")
def send_email(data: SendEmailReq, bg: BackgroundTasks,
               user_id: int = Depends(decode_token), db: Session = Depends(get_db)):
    user  = db.query(User).filter_by(id=user_id).first()
    prefs = _get_prefs(user_id, db)
    if not prefs.email_enabled:
        raise HTTPException(400, "Notifications email desactivees")
    conv = db.query(Conversation).filter_by(id=data.conversation_id, user_id=user_id).first()
    if not conv: raise HTTPException(404, "Conversation introuvable")
    msg = (db.query(Message).filter_by(id=data.message_id).first() if data.message_id
           else db.query(Message).filter_by(conversation_id=conv.id)
                .filter(Message.role=="assistant").order_by(Message.created_at.desc()).first())
    if not msg: raise HTTPException(404, "Message introuvable")
    lang = prefs.language or conv.language or "fr"
    subj, html = procedure_email(user.name, msg.content, conv.id, lang)
    def _send():
        ok = brevo_service.send_email(user.email, user.name, subj, html)
        _log(db, user_id, conv.id, NotificationType.email, subj, msg.content[:500],
             NotificationStatus.sent if ok else NotificationStatus.failed)
    bg.add_task(_send)
    return {"success": True, "message": f"Email en cours vers {user.email}"}

@router.post("/send-sms")
def send_sms(data: SendSMSReq, bg: BackgroundTasks,
             user_id: int = Depends(decode_token), db: Session = Depends(get_db)):
    user  = db.query(User).filter_by(id=user_id).first()
    prefs = _get_prefs(user_id, db)
    phone = data.phone or prefs.phone
    if not phone: raise HTTPException(400, "Numero manquant")
    conv = db.query(Conversation).filter_by(id=data.conversation_id, user_id=user_id).first()
    if not conv: raise HTTPException(404, "Conversation introuvable")
    msg = (db.query(Message).filter_by(conversation_id=conv.id)
           .filter(Message.role=="assistant").order_by(Message.created_at.desc()).first())
    if not msg: raise HTTPException(404, "Message introuvable")
    lang = prefs.language or "fr"
    sms_text = (f"iDaraty — {conv.title}\n{msg.content[:120]}..." if lang=="fr"
                else f"iDaraty — {conv.title}\n{msg.content[:120]}...")
    def _send():
        ok = brevo_service.send_sms(phone, sms_text)
        _log(db, user_id, conv.id, NotificationType.sms, conv.title, sms_text,
             NotificationStatus.sent if ok else NotificationStatus.failed)
    bg.add_task(_send)
    return {"success": True, "message": f"SMS en cours vers {phone}"}

@router.get("/export-pdf/{conversation_id}")
def export_pdf(conversation_id: int,
               user_id: int = Depends(decode_token), db: Session = Depends(get_db)):
    user = db.query(User).filter_by(id=user_id).first()
    conv = db.query(Conversation).filter_by(id=conversation_id, user_id=user_id).first()
    if not conv: raise HTTPException(404, "Conversation introuvable")
    msgs = db.query(Message).filter_by(conversation_id=conversation_id).order_by(Message.created_at).all()
    data = [{"role": m.role.value, "content": m.content,
             "created_at": m.created_at.isoformat() if m.created_at else ""} for m in msgs]
    pdf  = export_conversation_pdf(data, conv.title or "Conversation", user.name, conv.language or "fr")
    return StreamingResponse(io.BytesIO(pdf), media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="idaraty-{conversation_id}.pdf"'})

@router.get("/preferences")
def get_prefs(user_id: int = Depends(decode_token), db: Session = Depends(get_db)):
    p = _get_prefs(user_id, db)
    return {"email_enabled": p.email_enabled, "sms_enabled": p.sms_enabled,
            "phone": p.phone, "reminder_enabled": p.reminder_enabled, "language": p.language}

@router.put("/preferences")
def update_prefs(data: UpdatePrefsReq, user_id: int = Depends(decode_token), db: Session = Depends(get_db)):
    p = _get_prefs(user_id, db)
    if data.email_enabled    is not None: p.email_enabled    = data.email_enabled
    if data.sms_enabled      is not None: p.sms_enabled      = data.sms_enabled
    if data.phone            is not None: p.phone            = data.phone
    if data.reminder_enabled is not None: p.reminder_enabled = data.reminder_enabled
    if data.language         is not None: p.language         = data.language
    db.commit()
    return {"success": True}

@router.post("/reminders")
def create_reminder(data: CreateReminderReq, user_id: int = Depends(decode_token), db: Session = Depends(get_db)):
    conv = db.query(Conversation).filter_by(id=data.conversation_id, user_id=user_id).first()
    if not conv: raise HTTPException(404, "Conversation introuvable")
    remind_at = datetime.utcnow() + timedelta(days=data.remind_in_days)
    r = Reminder(user_id=user_id, conversation_id=data.conversation_id,
                 procedure_name=data.procedure_name, remind_at=remind_at,
                 type=NotificationType.email if data.type=="email" else NotificationType.sms)
    db.add(r); db.commit(); db.refresh(r)
    return {"success": True, "reminder_id": r.id,
            "remind_at": remind_at.isoformat(),
            "message": f"Rappel cree pour le {remind_at.strftime('%d/%m/%Y')}"}

@router.get("/reminders")
def list_reminders(user_id: int = Depends(decode_token), db: Session = Depends(get_db)):
    rs = db.query(Reminder).filter_by(user_id=user_id).order_by(Reminder.remind_at).all()
    return {"reminders": [{"id": r.id, "procedure_name": r.procedure_name,
            "remind_at": r.remind_at.isoformat(), "type": r.type.value,
            "status": r.status.value} for r in rs]}

@router.delete("/reminders/{reminder_id}")
def cancel_reminder(reminder_id: int, user_id: int = Depends(decode_token), db: Session = Depends(get_db)):
    r = db.query(Reminder).filter_by(id=reminder_id, user_id=user_id).first()
    if not r: raise HTTPException(404, "Rappel introuvable")
    r.status = ReminderStatus.cancelled; db.commit()
    return {"success": True}

@router.get("/history")
def notif_history(user_id: int = Depends(decode_token), db: Session = Depends(get_db)):
    ns = db.query(Notification).filter_by(user_id=user_id).order_by(Notification.created_at.desc()).limit(50).all()
    return {"notifications": [{"id": n.id, "type": n.type.value, "subject": n.subject,
            "status": n.status.value, "sent_at": n.sent_at.isoformat() if n.sent_at else None,
            "created_at": n.created_at.isoformat()} for n in ns]}