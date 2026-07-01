"""
Admin Models - Compatibility wrapper.

DEPRECATED: All models have been consolidated to shared/models.py
This file is maintained for backward compatibility only.

Import directly from shared.models instead.
"""

from shared.models import (
    Base,
    User,
    Conversation,
    Message,
    ContactAttempt,
)

__all__ = [
    "Base",
    "User",
    "Conversation",
    "Message",
    "ContactAttempt",
]
