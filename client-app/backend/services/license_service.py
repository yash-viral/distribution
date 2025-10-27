from validators.license_validator import LicenseValidator
from pathlib import Path
from services import license_store

class LicenseService:
    def __init__(self):
        self.license_validator = LicenseValidator()
    
    def validate_license_data(self, license_data: dict):
        result = self.license_validator.validate_license_data(license_data)
        license_store.set_license(result)
        return result
    
    def validate_license_file(self, file_path: str = None):
        if file_path:
            license_path = Path(file_path)
            with open(license_path, "rb") as f:
                content = f.read()
            with open("license.lic", "wb") as f:
                f.write(content)
            result = self.license_validator.validate_license_file("license.lic")
        else:
            result = self.license_validator.validate_license_file()
        
        license_store.set_license(result)
        return result
    
    def validate_existing_license(self):
        result = self.license_validator.validate_license_file()
        license_store.set_license(result)
        return result
    
    def get_current_license(self):
        return license_store.get_license()