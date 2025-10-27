from fastapi import APIRouter, HTTPException, File, UploadFile
from pydantic import BaseModel
from services.license_service import LicenseService

router = APIRouter(prefix="/api/license", tags=["license"])
license_service = LicenseService()

class LicenseInput(BaseModel):
    license_data: dict

@router.post("/validate")
async def validate_license(license_input: LicenseInput):
    try:
        result = license_service.validate_license_data(license_input.license_data)
        return {"status": "success", "license": result}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/upload")
async def upload_license_file(file: UploadFile = File(...)):
    try:
        print(f"DEBUG: Received file upload: {file.filename}")
        content = await file.read()
        print(f"DEBUG: File size: {len(content)} bytes")
        
        with open("license.lic", "wb") as f:
            f.write(content)
        
        print("DEBUG: Starting license validation...")
        result = license_service.validate_license_file("license.lic")
        print(f"DEBUG: Validation successful: {result}")
        return {"status": "success", "license": result}
    except Exception as e:
        print(f"DEBUG: License upload failed: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/validate-file")
async def validate_existing_license_file():
    try:
        print("DEBUG: Validating existing license file...")
        result = license_service.validate_existing_license()
        print(f"DEBUG: Existing license validation successful: {result}")
        return {"status": "success", "license": result}
    except Exception as e:
        print(f"DEBUG: Existing license validation failed: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/status")
async def get_license_status():
    current_license = license_service.get_current_license()
    if not current_license:
        raise HTTPException(status_code=400, detail="No valid license")
    return current_license