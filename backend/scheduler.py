"""
Rappels automatiques — APScheduler
pip install apscheduler
"""
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from datetime import datetime
from sqlalchemy.orm import Session
import logging

from database import SessionLocal
from models import Reminder, ReminderStatus, NotificationType, User, NotificationPreference
from services.brevo_service import brevo_service
from services.email_templates import reminder_email

logger = logging.getLogger(__name__)

def process_pending_reminders():
    db: Session = SessionLocal()
    try:
        now = datetime.utcnow()
        due = db.query(Reminder).filter(
            Reminder.status == ReminderStatus.pending,
            Reminder.remind_at <= now
        ).all()

        if not due:
            return

        logger.info(f"{len(due)} rappel(s) a envoyer")

        for r in due:
            user  = db.query(User).filter_by(id=r.user_id).first()
            prefs = db.query(NotificationPreference).filter_by(user_id=r.user_id).first()
            if not user:
                r.status = ReminderStatus.cancelled
                continue

            lang      = prefs.language if prefs else "fr"
            days_left = max(0, (r.remind_at - r.created_at).days)
            ok        = False

            if r.type == NotificationType.email:
                subj, html = reminder_email(user.name, r.procedure_name, days_left, lang)
                ok = brevo_service.send_email(user.email, user.name, subj, html)
            elif r.type == NotificationType.sms:
                phone = prefs.phone if prefs else None
                if phone:
                    sms = (f"iDaraty — تذكير: {r.procedure_name}. تبقّى {days_left} يوم."
                           if lang == "ar" else
                           f"iDaraty — Rappel: {r.procedure_name}. Il reste {days_left} jour(s).")
                    ok = brevo_service.send_sms(phone, sms)

            r.status  = ReminderStatus.sent if ok else ReminderStatus.cancelled
            r.sent_at = datetime.utcnow() if ok else None

        db.commit()
    except Exception as e:
        logger.error(f"Erreur cron: {e}")
        db.rollback()
    finally:
        db.close()

def start_scheduler():
    scheduler = BackgroundScheduler(timezone="Africa/Tunis")
    scheduler.add_job(
        process_pending_reminders,
        trigger=CronTrigger(minute=0),
        id="process_reminders",
        replace_existing=True
    )
    scheduler.start()
    logger.info("Scheduler demarre")
    return scheduler