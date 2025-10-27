# Global license storage
_current_license = None

def set_license(license_data):
    global _current_license
    _current_license = license_data
    print(f"DEBUG: License stored globally: {license_data}")

def get_license():
    global _current_license
    print(f"DEBUG: License retrieved globally: {_current_license}")
    return _current_license