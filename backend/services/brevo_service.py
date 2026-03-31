"""
Service Brevo — Email + SMS
pip install sib-api-v3-sdk
"""
import sib_api_v3_sdk
from sib_api_v3_sdk.rest import ApiException
from config import settings
import logging

logger = logging.getLogger(__name__)

class BrevoService:
    def __init__(self):
        cfg = sib_api_v3_sdk.Configuration()
        cfg.api_key["api-key"] = settings.BREVO_API_KEY
        # ✅ Timeout explicite pour éviter le blocage infini
        cfg.timeout = 10
        client = sib_api_v3_sdk.ApiClient(cfg)
        self.email_api = sib_api_v3_sdk.TransactionalEmailsApi(client)
        self.sms_api   = sib_api_v3_sdk.TransactionalSMSApi(client)

    def send_email(self, to_email: str, to_name: str, subject: str, html: str) -> bool:
        try:
            self.email_api.send_transac_email(sib_api_v3_sdk.SendSmtpEmail(
                to=[{"email": to_email, "name": to_name}],
                sender={"email": settings.BREVO_SENDER_EMAIL, "name": settings.BREVO_SENDER_NAME},
                subject=subject,
                html_content=html
            ))
            logger.info(f"Email envoye a {to_email}")
            return True
        except ApiException as e:
            logger.error(f"Erreur Brevo email: {e}")
            return False
        except Exception as e:
            logger.error(f"Erreur reseau email: {e}")
            return False

    def send_sms(self, to_phone: str, content: str) -> bool:
        """
        SMS via Brevo — nécessite un compte Brevo avec SMS activé
        Note: SMS Brevo peut être bloqué dans certains réseaux
        """
        try:
            phone = to_phone.strip().replace(" ", "")
            if not phone.startswith("+"):
                phone = "+216" + phone

            self.sms_api.send_transac_sms(
                sib_api_v3_sdk.SendTransacSms(
                    sender=settings.BREVO_SMS_SENDER,
                    recipient=phone,
                    content=content[:160]
                )
            )
            logger.info(f"SMS envoye a {phone}")
            return True
        except ApiException as e:
            logger.error(f"Erreur Brevo SMS: {e}")
            return False
        except Exception as e:
            # ✅ Capturer le timeout sans crasher le serveur
            logger.warning(f"SMS non envoye (timeout/reseau): {e}")
            return False

brevo_service = BrevoService()