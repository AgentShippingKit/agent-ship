"""Token encryption utilities for MCP OAuth tokens."""

import os
import logging
from typing import Optional
from cryptography.fernet import Fernet

logger = logging.getLogger(__name__)


class TokenEncryption:
    """Handle encryption/decryption of OAuth tokens using Fernet."""

    def __init__(self, encryption_key: Optional[str] = None):
        """Initialize token encryption.

        Args:
            encryption_key: Base64-encoded Fernet key (generates if not provided)
        """
        if encryption_key is None:
            encryption_key = os.getenv("MCP_TOKEN_ENCRYPTION_KEY")

        if encryption_key is None:
            logger.warning(
                "MCP_TOKEN_ENCRYPTION_KEY not set. Generating temporary key. "
                "This key will be lost on restart! Set MCP_TOKEN_ENCRYPTION_KEY "
                "environment variable for production."
            )
            encryption_key = Fernet.generate_key().decode()

        self.fernet = Fernet(encryption_key.encode() if isinstance(encryption_key, str) else encryption_key)

    def encrypt(self, token: str) -> str:
        """Encrypt a token.

        Args:
            token: Plain text token

        Returns:
            Encrypted token (base64-encoded)
        """
        if not token:
            return ""

        encrypted_bytes = self.fernet.encrypt(token.encode())
        return encrypted_bytes.decode()

    def decrypt(self, encrypted_token: str) -> str:
        """Decrypt a token.

        Args:
            encrypted_token: Encrypted token (base64-encoded)

        Returns:
            Plain text token
        """
        if not encrypted_token:
            return ""

        try:
            decrypted_bytes = self.fernet.decrypt(encrypted_token.encode())
            return decrypted_bytes.decode()
        except Exception as e:
            logger.error(f"Failed to decrypt token: {e}")
            raise ValueError("Failed to decrypt token") from e


# Global instance
_encryption = None


def get_token_encryption() -> TokenEncryption:
    """Get global TokenEncryption instance.

    Returns:
        TokenEncryption instance
    """
    global _encryption
    if _encryption is None:
        _encryption = TokenEncryption()
    return _encryption


def encrypt_token(token: str) -> str:
    """Encrypt a token using global encryption instance.

    Args:
        token: Plain text token

    Returns:
        Encrypted token
    """
    return get_token_encryption().encrypt(token)


def decrypt_token(encrypted_token: str) -> str:
    """Decrypt a token using global encryption instance.

    Args:
        encrypted_token: Encrypted token

    Returns:
        Plain text token
    """
    return get_token_encryption().decrypt(encrypted_token)


def generate_encryption_key() -> str:
    """Generate a new Fernet encryption key.

    Returns:
        Base64-encoded encryption key
    """
    return Fernet.generate_key().decode()


if __name__ == "__main__":
    # Generate a new key for setup
    print("Generated MCP_TOKEN_ENCRYPTION_KEY:")
    print(generate_encryption_key())
    print("\nAdd this to your .env file:")
    print(f"MCP_TOKEN_ENCRYPTION_KEY={generate_encryption_key()}")
