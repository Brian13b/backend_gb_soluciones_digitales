import hmac
import hashlib
from fastapi import HTTPException, status
from bot.core.config import settings

def verify_webhook_signature(body: bytes, signature: str) -> bool:
    if not signature:
        return False

    try:
        expected_hash = signature.split("sha256=")[1]
    except IndexError:
        return False

    calculated_hash = hmac.new(
        settings.WHATSAPP_APP_SECRET.encode(),
        body,
        hashlib.sha256
    ).hexdigest()

    return hmac.compare_digest(calculated_hash, expected_hash)


async def validate_webhook_signature(body: bytes, x_hub_signature_256: str = None) -> bool:
    if not x_hub_signature_256:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing X-Hub-Signature-256 header"
        )

    if not verify_webhook_signature(body, x_hub_signature_256):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid webhook signature"
        )

    return True
