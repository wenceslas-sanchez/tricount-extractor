from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.backends import default_backend

RSA_KEY_SIZE = 2048
RSA_PUBLIC_EXPONENT = 65537


def generate_public_rsa_key() -> str:
    """
    Generate public RSA key.

    Note: The private key is generated but never used. Only the public key
    is sent to the API during session installation. The Tricount API validates
    the key, so it must be a properly formatted RSA public key.
    """

    return (
        rsa.generate_private_key(
            public_exponent=RSA_PUBLIC_EXPONENT,
            key_size=RSA_KEY_SIZE,
            backend=default_backend(),
        )
        .public_key()
        .public_bytes(
            encoding=serialization.Encoding.PEM, format=serialization.PublicFormat.PKCS1
        )
        .decode("utf-8")
    )
