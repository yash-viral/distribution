import requests
from typing import Dict, Optional

class ServerValidator:
    def __init__(self, server_url: str = "http://localhost:8000"):
        self.server_url = server_url
    
    def validate_license_with_server(self, license_key: str) -> Dict:
        try:
            url = f"{self.server_url}/api/licenses/{license_key}"
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                server_data = response.json()
                return {
                    "valid": True,
                    "server_verified": True,
                    "license_data": server_data["license_data"],
                    "message": "License verified with server"
                }
            elif response.status_code == 404:
                return {
                    "valid": False,
                    "server_verified": False,
                    "error": "License not found on server"
                }
            else:
                return {
                    "valid": False,
                    "server_verified": False,
                    "error": f"Server validation failed: {response.status_code}"
                }
                
        except requests.exceptions.RequestException as e:
            return {
                "valid": False,
                "server_verified": False,
                "error": f"Server unavailable: {str(e)}",
                "message": "Server validation required but unavailable"
            }
    
    def extract_license_key_from_file(self, license_file_path: str) -> Optional[str]:
        try:
            with open(license_file_path, 'r') as f:
                content = f.read()
                for line in content.split('\n'):
                    if line.startswith('# Key:'):
                        return line.split('# Key: ')[1].strip()
            return None
        except Exception:
            return None