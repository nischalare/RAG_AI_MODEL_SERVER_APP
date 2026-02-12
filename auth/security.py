"""
auth/security.py

Handles password hashing and verification.

Improvements:
- Uses bcrypt safely
- Prevents bcrypt 72-byte crash
- Pre-hashes long passwords using SHA256 (enterprise safe)
- Clean and production ready
"""

from passlib.context import CryptContext
import hashlib

# =====================================================
# PASSWORD HASHING CONFIGURATION
# =====================================================

# bcrypt is secure and widely used.
# deprecated="auto" ensures future compatibility.
pwd = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto"
)

# =====================================================
# HASH PASSWORD
# =====================================================

def hash_password(password: str) -> str:
    """
    Securely hash a password.

    ⚠ bcrypt has a hard 72-byte limit.
    If password exceeds this, we first SHA256-hash it
    and then apply bcrypt.

    This avoids:
        ValueError: password cannot be longer than 72 bytes
    """

    # Convert to bytes and check length
    if len(password.encode("utf-8")) > 72:
        password = hashlib.sha256(password.encode("utf-8")).hexdigest()

    # Return bcrypt hash
    return pwd.hash(password)


# =====================================================
# VERIFY PASSWORD
# =====================================================

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a password during login.

    Must apply same pre-hash logic if length > 72 bytes.
    """

    if len(plain_password.encode("utf-8")) > 72:
        plain_password = hashlib.sha256(
            plain_password.encode("utf-8")
        ).hexdigest()

    return pwd.verify(plain_password, hashed_password)
