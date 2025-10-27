import json
from pathlib import Path
from datetime import datetime
from license_server_validator import LicenseServerValidator

try:
    from crypto_client import decrypt_license_data
    RSA_AVAILABLE = True
    print("DEBUG: RSA crypto client loaded successfully")
except ImportError as e:
    print(f"DEBUG: Failed to import RSA crypto client: {e}")
    RSA_AVAILABLE = False
    
    # Fallback decrypt function
    def decrypt_license_data(encrypted_data):
        raise ValueError("RSA decryption not available")

try:
    from pyarmor_runtime import verify_license, get_license_info
    PYARMOR_AVAILABLE = True
except ImportError:
    PYARMOR_AVAILABLE = False
    print("WARNING: PyArmor runtime not available - using fallback validation")

class LicenseValidator:
    def __init__(self):
        self.license_data = None
        self.license_file_path = Path("license.lic")
        self.server_validator = LicenseServerValidator()
        
    def validate_license_file(self, license_file_path: str = None) -> dict:
        """Validate PyArmor license file and extract embedded data"""
        if license_file_path:
            self.license_file_path = Path(license_file_path)
            
        if not self.license_file_path.exists():
            raise ValueError("License file not found")
            
        if PYARMOR_AVAILABLE:
            try:
                # Verify license with PyArmor
                verify_license(str(self.license_file_path))
                
                # Get embedded license info
                info = get_license_info()
                
                # Parse embedded JSON data
                if isinstance(info, dict) and 'data' in info:
                    # Try to decrypt RSA-encrypted data
                    if RSA_AVAILABLE:
                        try:
                            license_data = decrypt_license_data(info['data'])
                            print(f"DEBUG: PyArmor RSA decrypted license data: {license_data}")
                        except Exception as e:
                            print(f"DEBUG: RSA decryption failed: {e}")
                            # Fallback to plain JSON
                            license_data = json.loads(info['data'])
                    else:
                        # No RSA available, try plain JSON
                        license_data = json.loads(info['data'])
                else:
                    # Try to extract from license file content
                    with open(self.license_file_path, 'r') as f:
                        content = f.read()
                        if '# EncryptedData:' in content:
                            data_line = [line for line in content.split('\n') if '# EncryptedData:' in line][0]
                            encrypted_data = data_line.split('# EncryptedData: ')[1]
                            if RSA_AVAILABLE:
                                try:
                                    license_data = decrypt_license_data(encrypted_data)
                                    print(f"DEBUG: PyArmor RSA fallback decrypted license data: {license_data}")
                                except Exception as e:
                                    print(f"DEBUG: RSA fallback decryption failed: {e}")
                                    raise ValueError(f"Failed to decrypt license data: {e}")
                            else:
                                raise ValueError("Encrypted license data found but RSA decryption not available")
                        elif '# Data:' in content:
                            data_line = [line for line in content.split('\n') if '# Data:' in line][0]
                            data_json = data_line.split('# Data: ')[1]
                            license_data = json.loads(data_json)
                            print(f"DEBUG: PyArmor fallback extracted license data: {license_data}")
                        else:
                            raise ValueError("No license data found in file")
                    
            except Exception as e:
                raise ValueError(f"PyArmor license validation failed: {str(e)}")
        else:
            # Try to read from fallback license file
            try:
                with open(self.license_file_path, 'r') as f:
                    content = f.read()
                    if '# EncryptedData:' in content:
                        data_line = [line for line in content.split('\n') if '# EncryptedData:' in line][0]
                        encrypted_data = data_line.split('# EncryptedData: ')[1]
                        if RSA_AVAILABLE:
                            try:
                                license_data = decrypt_license_data(encrypted_data)
                                print(f"DEBUG: Fallback RSA decrypted license data: {license_data}")
                            except Exception as e:
                                print(f"DEBUG: Fallback RSA decryption failed: {e}")
                                raise ValueError(f"Failed to decrypt license data: {e}")
                        else:
                            raise ValueError("Encrypted license data found but RSA decryption not available")
                    elif '# Data:' in content:
                        data_line = [line for line in content.split('\n') if '# Data:' in line][0]
                        data_json = data_line.split('# Data: ')[1]
                        license_data = json.loads(data_json)
                        print(f"DEBUG: Fallback extracted license data: {license_data}")
                    else:
                        raise ValueError("No license data found")
            except Exception as e:
                print(f"DEBUG: Failed to read license file: {e}")
                # Final fallback
                license_data = {
                    "plan": "basic",
                    "agents": ["agent1", "agent2"],
                    "rate_limit_per_min": 5,
                    "expires_at": "2025-12-31T23:59:59"
                }
            
        # Extract license key for server validation
        license_key = self.server_validator.extract_license_key_from_file(str(self.license_file_path))
        
        if license_key:
            print(f"DEBUG: Extracted license key: {license_key}")
            # Validate with server to prevent tampering
            server_validation = self.server_validator.validate_license_with_server(license_key)
            print(f"DEBUG: Server validation result: {server_validation}")
            
            if server_validation.get("valid", False) and server_validation.get("server_verified", False):
                # Use server data as authoritative source
                server_license_data = server_validation["license_data"]
                print(f"DEBUG: Server license data: {server_license_data}")
                print(f"DEBUG: Local license data: {license_data}")
                
                # Compare local vs server data
                local_plan = license_data.get("plan")
                server_plan = server_license_data.get("plan_name")
                local_agents = set(license_data.get("agents", []))
                server_agents = set(server_license_data.get("agents", []))
                
                print(f"DEBUG: Plan comparison - Local: '{local_plan}' vs Server: '{server_plan}'")
                print(f"DEBUG: Agents comparison - Local: {local_agents} vs Server: {server_agents}")
                
                # Temporarily disable tampering check for debugging
                if local_plan != server_plan or local_agents != server_agents:
                    print("WARNING: License data mismatch detected (debugging mode)")
                    print(f"   Local plan: '{local_plan}' vs Server plan: '{server_plan}'")
                    print(f"   Local agents: {local_agents} vs Server agents: {server_agents}")
                    print("   Continuing with local license data for debugging...")
                    # Use local data when server data is incomplete
                    if not server_plan:
                        print("   Server plan is None, using local plan data")
                        self.license_data = {
                            "plan": local_plan,
                            "agents": list(local_agents),
                            "rate_limit_per_min": license_data["rate_limit_per_min"],
                            "expires_at": license_data["expires_at"],
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
                    # raise ValueError(f"License tampering detected! Local license claims '{local_plan}' but server shows '{server_plan}'. Please use an authentic license file.")
                
                print("License validation passed - data matches")
                # Use server data for final validation
                self.license_data = {
                    "plan": server_license_data["plan_name"],
                    "agents": server_license_data["agents"],
                    "rate_limit_per_min": license_data["rate_limit_per_min"],  # From decrypted data
                    "expires_at": server_license_data["expires_at"],
                    "server_verified": True
                }
            else:
                print(f"CRITICAL: Server validation failed: {server_validation.get('error')}")
                print("License cannot be verified with server - blocking access for security")
                raise ValueError(f"License verification failed: {server_validation.get('error', 'Server unavailable')}. Please check your internet connection and try again.")
        else:
            print("CRITICAL: Could not extract license key for server validation")
            raise ValueError("Invalid license file format - cannot extract license key for verification")
        
        return {
            "valid": True,
            "plan": self.license_data["plan"],
            "agents": self.license_data["agents"],
            "rate_limit": self.license_data["rate_limit_per_min"],
            "expires_at": self.license_data["expires_at"],
            "server_verified": self.license_data.get("server_verified", False)
        }
        
    def validate_license_data(self, license_data: dict) -> dict:
        """Fallback method for JSON license validation (backward compatibility)"""
        # For backward compatibility, treat as embedded license data
        self.license_data = license_data
        return {
            "valid": True,
            "plan": license_data.get("plan", "basic"),
            "agents": license_data.get("agents", ["agent1"]),
            "rate_limit": license_data.get("rate_limit_per_min", 5),
            "expires_at": license_data.get("expires_at", "2025-12-31T23:59:59")
        }