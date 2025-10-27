"""
Server-side license validation to prevent plan tampering
"""

import requests
import json
from typing import Dict, Optional

class LicenseServerValidator:
    def __init__(self, server_url: str = "http://localhost:8000"):
        self.server_url = server_url
    
    def validate_license_with_server(self, license_key: str) -> Dict:
        """
        Validate license key with subscription server to prevent tampering
        """
        print(f"DEBUG: Validating license key with server: {license_key}")
        print(f"DEBUG: Server URL: {self.server_url}")
        
        try:
            # Call server to verify license authenticity
            url = f"{self.server_url}/api/licenses/{license_key}"
            print(f"DEBUG: Making request to: {url}")
            
            response = requests.get(url, timeout=10)
            print(f"DEBUG: Server response status: {response.status_code}")
            print(f"DEBUG: Server response content: {response.text[:500]}...")
            
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
            print(f"DEBUG: Server request failed: {str(e)}")
            # Server unavailable - block access for security
            return {
                "valid": False,
                "server_verified": False,
                "error": f"Server unavailable: {str(e)}",
                "message": "Server validation required but unavailable"
            }
    
    def extract_license_key_from_file(self, license_file_path: str) -> Optional[str]:
        """
        Extract license key from license file
        """
        try:
            with open(license_file_path, 'r') as f:
                content = f.read()
                for line in content.split('\n'):
                    if line.startswith('# Key:'):
                        return line.split('# Key: ')[1].strip()
            return None
        except Exception:
            return None