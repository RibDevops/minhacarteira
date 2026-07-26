import base64
import decimal
import logging
from cryptography.fernet import Fernet, InvalidToken
from django.conf import settings
from django.db import models

from cryptography.hazmat.backends import default_backend  # noqa: F401
from cryptography.hazmat.primitives import hashes  # noqa: F401
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC  # noqa: F401

logger = logging.getLogger(__name__)


def validate_fernet_key(key):
    """Valida e retorna um Fernet pronto para uso a partir da chave em settings."""
    try:
        decoded_key = base64.urlsafe_b64decode(key)
        if len(decoded_key) != 32:
            raise ValueError("Fernet key must be 32 url-safe base64-encoded bytes")
        return Fernet(key)
    except Exception as e:
        logger.error(f"Invalid Fernet key: {e}")
        raise


# Decodifica a chave base64 da configuração
fernet_key = settings.FERNET_SECRET_KEY.encode()  # string para bytes
fernet = Fernet(fernet_key)


def _maybe_decrypt(value):
    """
    Tenta descriptografar. Se o valor nao for um token Fernet valido (i.e. e
    texto puro de um registro legado anterior a criptografia), devolve o
    valor original sem erros. Isso permite a coexistencia de registros novos
    (criptografados) e antigos (texto puro) durante o periodo de migracao.
    """
    if value is None or value == "":
        return value
    # Se ja e um Decimal/int/float (valor vindo do DB como numerico), nao tenta descriptografar
    if isinstance(value, (decimal.Decimal, int, float)):
        return str(value)
    try:
        return fernet.decrypt(value.encode()).decode()
    except (InvalidToken, ValueError, AttributeError):
        # Nao e um token Fernet: provavelmente texto puro legado.
        return value


class EncryptedCharField(models.CharField):
    def __init__(self, *args, **kwargs):
        self.fernet = fernet
        super().__init__(*args, **kwargs)

    def get_internal_type(self):
        return "CharField"

    def from_db_value(self, value, expression, connection):
        if value is None:
            return value
        return _maybe_decrypt(value)

    def to_python(self, value):
        if value is None or isinstance(value, str):
            return value
        try:
            return self.fernet.decrypt(value.encode()).decode()
        except (InvalidToken, ValueError):
            return value

    def get_prep_value(self, value):
        if value is None or value == "":
            return value
        return self.fernet.encrypt(value.encode()).decode()


class EncryptedDecimalField(models.DecimalField):
    def __init__(self, *args, max_digits=None, decimal_places=None, **kwargs):
        self.max_digits = max_digits
        self.decimal_places = decimal_places
        self.fernet = fernet
        super().__init__(*args, max_digits=max_digits, decimal_places=decimal_places, **kwargs)

    def from_db_value(self, value, expression, connection):
        if value is None:
            return None
        decrypted = _maybe_decrypt(value)
        try:
            return decimal.Decimal(decrypted)
        except (decimal.InvalidOperation, TypeError, ValueError):
            return decimal.Decimal('0.00')

    def to_python(self, value):
        if value is None:
            return None
        if isinstance(value, decimal.Decimal):
            return value
        try:
            if isinstance(value, str):
                if '.' in value or value.lstrip('-').replace('.', '').isdigit():
                    return decimal.Decimal(value)
                decrypted = self.fernet.decrypt(value.encode()).decode()
                return decimal.Decimal(decrypted)
            return decimal.Decimal(str(value))
        except (decimal.InvalidOperation, TypeError, ValueError) as e:
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