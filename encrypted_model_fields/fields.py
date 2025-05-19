import base64
import decimal
import logging
from cryptography.fernet import Fernet, InvalidToken
from django.conf import settings
from django.db import models

logger = logging.getLogger(__name__)

# Geração da chave (não inclua em produção!)
# print(Fernet.generate_key().decode())

# Usa chave do settings
FERNET_KEY = settings.SECRET_KEY[:32].encode()  # segura se < 32
fernet = Fernet(base64.urlsafe_b64encode(FERNET_KEY.ljust(32, b"0")))


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
        self.fernet = fernet
        super().__init__(*args, **kwargs)

    def get_internal_type(self):
        return "CharField"

    def from_db_value(self, value, expression, connection):
        return self.to_python(value)

    def to_python(self, value):
        if value is None or isinstance(value, decimal.Decimal):
            return value
        if isinstance(value, (int, float)):
            return decimal.Decimal(str(value))
        try:
            decrypted = self.fernet.decrypt(value.encode()).decode()
            return decimal.Decimal(decrypted)
        except (InvalidToken, ValueError, TypeError) as e:
            logger.warning(f"Decryption failed or invalid decimal: {e}")
            return decimal.Decimal("0.00")  # fallback seguro

    def get_prep_value(self, value):
        if value is None:
            return value
        try:
            value = decimal.Decimal(value)
        except (decimal.InvalidOperation, TypeError, ValueError):
            logger.warning(f"Invalid decimal for encryption: {value}")
            return None
        return self.fernet.encrypt(str(value).encode()).decode()
