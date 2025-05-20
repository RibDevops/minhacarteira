import base64
import decimal
import logging
from cryptography.fernet import Fernet, InvalidToken
from django.conf import settings
from django.db import models

from django.conf import settings
import base64
from cryptography.fernet import Fernet
logger = logging.getLogger(__name__)

import base64
from cryptography.fernet import Fernet
from django.conf import settings

# Adicione no início do fields.py
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import os

def validate_fernet_key(key):
    try:
        # A chave Fernet deve ser 32 bytes codificados em URL-safe base64
        decoded_key = base64.urlsafe_b64decode(key)
        if len(decoded_key) != 32:
            raise ValueError("Fernet key must be 32 url-safe base64-encoded bytes")
        return Fernet(key)
    except Exception as e:
        logger.error(f"Invalid Fernet key: {e}")
        raise


# Decodifica a chave base64 da configuração
fernet_key = settings.FERNET_SECRET_KEY.encode()  # string para bytes
# Aqui você pode testar se é válida
fernet = Fernet(fernet_key)


class EncryptedCharField(models.CharField):
    def __init__(self, *args, **kwargs):
        self.fernet = fernet
        super().__init__(*args, **kwargs)

    def get_internal_type(self):
        return "CharField"

    def from_db_value(self, value, expression, connection):
        if value is None:
            return value
        try:
            return self.fernet.decrypt(value.encode()).decode()
        except InvalidToken as e:
            logger.warning(f"Decryption failed: {e}")
            return ""

    def to_python(self, value):
        if value is None or isinstance(value, str):
            return value
        try:
            return self.fernet.decrypt(value.encode()).decode()
        except InvalidToken as e:
            logger.warning(f"Decryption failed: {e}")
            return ""

    def get_prep_value(self, value):
        if value is None or value == "":
            return value
        return self.fernet.encrypt(value.encode()).decode()


class EncryptedDecimalField(models.Field):
    def __init__(self, *args, max_digits=None, decimal_places=None, **kwargs):
        self.max_digits = max_digits
        self.decimal_places = decimal_places
        self.fernet = validate_fernet_key(settings.FERNET_SECRET_KEY)
        super().__init__(*args, **kwargs)

    def from_db_value(self, value, expression, connection):
        if value is None:
            return None
        try:
            decrypted = self.fernet.decrypt(value.encode()).decode()
            return decimal.Decimal(decrypted)
        except Exception as e:
            logger.error(f"Decryption failed: {e}")
            return decimal.Decimal('0.00')

    def to_python(self, value):
        if value is None:
            return None
        if isinstance(value, decimal.Decimal):
            return value
        try:
            if isinstance(value, str):
                # Se já for string descriptografada
                if '.' in value or value.isdigit():
                    return decimal.Decimal(value)
                # Se for string criptografada
                decrypted = self.fernet.decrypt(value.encode()).decode()
                return decimal.Decimal(decrypted)
            return decimal.Decimal(str(value))
        except Exception as e:
            logger.error(f"Conversion to Decimal failed: {e}")
            return decimal.Decimal('0.00')

    def get_prep_value(self, value):
        if value is None:
            return None
        try:
            value = decimal.Decimal(value)
            return self.fernet.encrypt(str(value).encode()).decode()
        except (decimal.InvalidOperation, TypeError, ValueError) as e:
            logger.error(f"Invalid decimal value '{value}' for encryption: {e}")
            raise