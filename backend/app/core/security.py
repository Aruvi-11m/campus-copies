"""
Campus Copies ERP - Security & Cryptographic Utilities

Implements password hashing via pwdlib (bcrypt, 12 rounds) and HS256 JWT encoding/decoding.
Grounding: docs/BackendSpecification.md §3, docs/SecuritySpecification.md §2
"""

from datetime import datetime, timedelta, timezone
from typing import Any, Dict, Optional

import jwt
from pwdlib import PasswordHash
from pwdlib.hashers.bcrypt import BcryptHasher

from app.config import settings
from app.core.errors import AuthenticationError
from app.core.logging import logger

# Initialize pwdlib PasswordHash manager with Bcrypt
password_hash_manager = PasswordHash((BcryptHasher(rounds=12),))


def hash_password(password: str) -> str:
    """Hashes a plaintext password string using bcrypt with 12 rounds."""
    return password_hash_manager.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verifies a plaintext password against a stored bcrypt hash string."""
    try:
        return password_hash_manager.verify(plain_password, hashed_password)
    except Exception as err:
        logger.error("password_verification_error", error=str(err))
        return False


def create_jwt_token(
    data: Dict[str, Any], expires_delta: Optional[timedelta] = None
) -> str:
    """
    Encodes a JWT payload with expiration timestamp.
    """
    to_encode = data.copy()
    now = datetime.now(timezone.utc)
    if expires_delta:
        expire = now + expires_delta
    else:
        expire = now + timedelta(hours=settings.STUDENT_TOKEN_EXPIRE_HOURS)

    to_encode.update(
        {
            "iat": int(now.timestamp()),
            "exp": int(expire.timestamp()),
        }
    )

    return jwt.encode(to_encode, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)


def decode_jwt_token(token: str) -> Dict[str, Any]:
    """
    Decodes and validates an HS256 JWT token string.
    Raises AuthenticationError on expired or malformed token.
    """
    try:
        payload = jwt.decode(
            token,
            settings.JWT_SECRET,
            algorithms=[settings.JWT_ALGORITHM],
        )
        return payload
    except jwt.ExpiredSignatureError:
        raise AuthenticationError("JWT token has expired")
    except jwt.PyJWTError as err:
        logger.warning("jwt_decode_error", error=str(err))
        raise AuthenticationError("Invalid authentication token payload")
