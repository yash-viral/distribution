import json
from pathlib import Path
from utils.crypto_utils import CryptoUtils
from validators.server_validator import ServerValidator

try:
    from pyarmor_runtime import verify_license, get_license_info
    PYARMOR_AVAILABLE = True
except ImportError:
    PYARMOR_AVAILABLE = False

class LicenseValidator:
    def __init__(self):
        self.license_data = None
        self.license_file_path = Path("license.lic")
        self.server_validator = ServerValidator()
        
    def validate_license_file(self, license_file_path: str = None) -> dict:
        try:
            if license_file_path:
                self.license_file_path = Path(license_file_path)
                
            if not self.license_file_path.exists():
                raise ValueError("License file not found")
                
            print(f"DEBUG: Extracting license data from {self.license_file_path}")
            
            # Debug: Show file content
            with open(self.license_file_path, 'r') as f:
                content = f.read()
                print(f"DEBUG: License file content preview: {content[:500]}...")
            
            license_data = self._extract_license_data()
            print(f"DEBUG: Extracted license data: {license_data}")
            
            license_key = self.server_validator.extract_license_key_from_file(str(self.license_file_path))
            print(f"DEBUG: Extracted license key: {license_key}")
            
            if license_key:
                print("DEBUG: Validating with server...")
                server_validation = self.server_validator.validate_license_with_server(license_key)
                print(f"DEBUG: Server validation result: {server_validation}")
                
                if server_validation.get("valid", False) and server_validation.get("server_verified", False):
                    server_license_data = server_validation["license_data"]
                    self.license_data = {
                        "plan": server_license_data["plan_name"],
                        "agents": server_license_data["agents"],
                        "rate_limit_per_min": license_data["rate_limit_per_min"],
                        "expires_at": server_license_data["expires_at"],
                        "server_verified": True
                    }
                else:
                    print(f"DEBUG: Server validation failed: {server_validation}")
                    # For debugging, allow fallback to local data
                    self.license_data = {
                        "plan": license_data.get("plan", "basic"),
                        "agents": license_data.get("agents", ["agent1", "agent2"]),
                        "rate_limit_per_min": license_data.get("rate_limit_per_min", 5),
                        "expires_at": license_data.get("expires_at", "2025-12-31T23:59:59"),
                        "server_verified": False
                    }
                    print(f"DEBUG: Using fallback license data: {self.license_data}")
            else:
                print("DEBUG: No license key found, using fallback data")
                self.license_data = {
                    "plan": license_data.get("plan", "basic"),
                    "agents": license_data.get("agents", ["agent1", "agent2"]),
                    "rate_limit_per_min": license_data.get("rate_limit_per_min", 5),
                    "expires_at": license_data.get("expires_at", "2025-12-31T23:59:59"),
                    "server_verified": False
                }
            
            return {
                "valid": True,
                "plan": self.license_data["plan"],
                "agents": self.license_data["agents"],
                "rate_limit": self.license_data["rate_limit_per_min"],
                "expires_at": self.license_data["expires_at"],
                "server_verified": self.license_data.get("server_verified", False)
            }
        except Exception as e:
            print(f"DEBUG: License validation exception: {str(e)}")
            import traceback
            traceback.print_exc()
            raise e
    
    def _extract_license_data(self):
        if PYARMOR_AVAILABLE:
            try:
                verify_license(str(self.license_file_path))
                info = get_license_info()
                
                if isinstance(info, dict) and 'data' in info:
                    try:
                        return CryptoUtils.decrypt_license_data(info['data'])
                    except:
                        return json.loads(info['data'])
                else:
                    return self._extract_from_file_content()
            except Exception as e:
                raise ValueError(f"PyArmor license validation failed: {str(e)}")
        else:
            return self._extract_from_file_content()
    
    def _extract_from_file_content(self):
        with open(self.license_file_path, 'r') as f:
            content = f.read()
            if '# EncryptedData:' in content:
                data_line = [line for line in content.split('\n') if '# EncryptedData:' in line][0]
                encrypted_data = data_line.split('# EncryptedData: ')[1]
                try:
                    return CryptoUtils.decrypt_license_data(encrypted_data)
                except Exception as e:
                    print(f"DEBUG: RSA decryption failed: {e}, trying plain JSON fallback")
                    # Try to extract plain JSON data as fallback
                    if '# Data:' in content:
                        data_line = [line for line in content.split('\n') if '# Data:' in line][0]
                        data_json = data_line.split('# Data: ')[1]
                        return json.loads(data_json)
                    else:
                        raise e
            elif '# Data:' in content:
                data_line = [line for line in content.split('\n') if '# Data:' in line][0]
                data_json = data_line.split('# Data: ')[1]
                return json.loads(data_json)
            else:
                return {
                    "plan": "basic",
                    "agents": ["agent1", "agent2"],
                    "rate_limit_per_min": 5,
                    "expires_at": "2025-12-31T23:59:59"
                }
        
    def validate_license_data(self, license_data: dict) -> dict:
        self.license_data = license_data
        return {
            "valid": True,
            "plan": license_data.get("plan", "basic"),
            "agents": license_data.get("agents", ["agent1"]),
            "rate_limit": license_data.get("rate_limit_per_min", 5),
            "expires_at": license_data.get("expires_at", "2025-12-31T23:59:59")
        }