"""
Security utilities for WhatsApp webhook verification.
Validates HMAC SHA-256 signatures from Meta to prevent spoofed webhooks.
"""

import hmac
import hashlib
from fastapi import HTTPException, status
from bot.core.config import settings


def verify_webhook_signature(body: bytes, signature: str) -> bool:
    """
    Verify WhatsApp webhook signature using HMAC SHA-256.

    Args:
        body: The raw request body as bytes
        signature: The X-Hub-Signature-256 header value (format: sha256=<hex>)

    Returns:
        bool: True if signature is valid, False otherwise

    Reference:
        https://developers.facebook.com/docs/whatsapp/cloud-api/webhooks/verify-updates-webhook
    """
    if not signature:
        return False

    try:
        # Extract the hash part from "sha256=<hex>"
        expected_hash = signature.split("sha256=")[1]
    except IndexError:
        return False

    # Calculate HMAC SHA-256 using the app secret
    calculated_hash = hmac.new(
        settings.WHATSAPP_APP_SECRET.encode(),
        body,
        hashlib.sha256
    ).hexdigest()

    # Use constant-time comparison to prevent timing attacks
    return hmac.compare_digest(calculated_hash, expected_hash)


async def validate_webhook_signature(body: bytes, x_hub_signature_256: str = None) -> bool:
    """
    Dependency function to validate webhook signatures.
    Raises HTTPException if signature is invalid.

    Args:
        body: Raw request body
        x_hub_signature_256: Value from X-Hub-Signature-256 header

    Raises:
        HTTPException: 401 if signature is missing or invalid
    """
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
