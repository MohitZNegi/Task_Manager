from datetime import datetime, timedelta, timezone
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from app.config import settings
from app.database import get_db
from app.models import User
from app.schemas import TokenData

# CryptContext tells passlib to use bcrypt.
# bcrypt is the right choice for passwords — it's slow by design,
# making brute-force attacks computationally expensive.
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# OAuth2PasswordBearer extracts the token from the Authorization header.
# tokenUrl tells Swagger UI where to send login requests so it can
# automatically authenticate and test protected endpoints.
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


# ── Password helpers ──────────────────────────────────────────────────────────

def hash_password(plain: str) -> str:
    """Hash a plain-text password. Call this on registration."""
    return pwd_context.hash(plain)

def verify_password(plain: str, hashed: str) -> bool:
    """
    Verify a plain-text password against a stored hash.
    Never compare plain passwords directly — always use this.
    """
    return pwd_context.verify(plain, hashed)


# ── JWT helpers ───────────────────────────────────────────────────────────────

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    Create a signed JWT token.

    A JWT has three parts: header.payload.signature
    - Header:    algorithm used to sign
    - Payload:   claims (data) — we store user_id as "sub"
    - Signature: HMAC-SHA256 of header+payload, signed with SECRET_KEY

    Anyone can decode the header and payload (they're just base64).
    But only the server can VERIFY the signature — that's the security.
    """
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (
        expires_delta or timedelta(minutes=settings.access_token_expire_minutes)
    )
    to_encode["exp"] = expire   # "exp" is a standard JWT claim for expiry
    return jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm)


def decode_token(token: str) -> TokenData:
    """
    Decode and verify a JWT token.
    Raises HTTPException if the token is invalid, expired, or tampered with.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
        # WWW-Authenticate header tells the client what auth scheme to use
    )
    try:
        payload = jwt.decode(
            token,
            settings.secret_key,
            algorithms=[settings.algorithm],
        )
        user_id: int = payload.get("sub")
        if user_id is None:
            raise credentials_exception
        return TokenData(user_id=user_id)
    except JWTError:
        # JWTError covers: expired token, invalid signature, malformed token
        raise credentials_exception


# ── FastAPI dependency ────────────────────────────────────────────────────────

def get_current_user(
    token: str       = Depends(oauth2_scheme),
    db:    Session   = Depends(get_db),
) -> User:
    """
    This is a FastAPI dependency — add it to any route you want to protect:
        current_user: User = Depends(get_current_user)

    What it does on every protected request:
    1. OAuth2PasswordBearer extracts the token from the Authorization header
    2. decode_token verifies the signature and expiry
    3. We look up the user in the database
    4. If anything fails, we raise 401 — the route handler never runs

    The route handler receives a fully-loaded User object.
    It never has to think about authentication — that's already done.
    """
    token_data = decode_token(token)
    user = db.query(User).filter(User.id == token_data.user_id).first()
    if user is None or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or inactive",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user


def get_current_active_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """
    Convenience dependency — wraps get_current_user and additionally
    checks is_active. Use this in routes where a deactivated account
    should be treated as unauthorised.
    """
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user",
        )
    return current_user