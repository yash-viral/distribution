import json
import base64
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding

PUBLIC_KEY_PEM = """-----BEGIN PUBLIC KEY-----
MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAq7wbETwQh02pw2/fncPK
sF27LjRdqmPaSwSA1v8UmRUgQZCoc5hyEZLGzcrpUUVs5Z8Dk+RlCed3vhLVMqi/
9ndFrdUVGWTjjmYH/NkAg/9rozH0pgObTDYcUWgHhXRO0WxdU6eomDYR5xZTpJV1
c6//yrt5/ZRgAZsFMWv+NCDcSJ92CVfzooVAAmkXloyOQOgHyV3vKoE0JJO7sWWi
lVGKj+hCCqyqYcfDoGkezuUpLrsmT74f0hdjv3r9xA2QSpBYjXZKr7WbX/C4BLmf
vMam3QpJjgeN8ZBlfjcQV6pjDJ1LZQ9cae5oLIUzH42hkzmck/PX9fTWhs/Opz5l
cwIDAQAB
-----END PUBLIC KEY-----"""

class CryptoUtils:
    @staticmethod
    def load_public_key():
        return serialization.load_pem_public_key(PUBLIC_KEY_PEM.encode())
    
    @staticmethod
    def decrypt_license_data(encrypted_data: str) -> dict:
        public_key = CryptoUtils.load_public_key()
        
        try:
            combined_data = json.loads(base64.b64decode(encrypted_data))
            data_bytes = base64.b64decode(combined_data["data"])
            signature = base64.b64decode(combined_data["signature"])
            
            public_key.verify(
                signature,
                data_bytes,
                padding.PSS(
                    mgf=padding.MGF1(hashes.SHA256()),
                    salt_length=padding.PSS.MAX_LENGTH
                ),
                hashes.SHA256()
            )
            
            return json.loads(data_bytes.decode('utf-8'))
            
        except Exception as e:
            raise ValueError(f"License decryption failed: {str(e)}")
    
    @staticmethod
    def verify_license_signature(data: dict, signature_hex: str) -> bool:
        public_key = CryptoUtils.load_public_key()
        message = json.dumps(data, sort_keys=True).encode("utf-8")
        signature = bytes.fromhex(signature_hex)

        try:
            public_key.verify(
                signature,
                message,
                padding.PSS(
                    mgf=padding.MGF1(hashes.SHA256()),
                    salt_length=padding.PSS.MAX_LENGTH
                ),
                hashes.SHA256()
            )
            return True
        except Exception:
            return False