#!/usr/bin/env python3
"""
Sample license generator for testing PyArmor integration
This demonstrates how the subscription server would generate licenses
"""
import json
import subprocess
import sys
from pathlib import Path
from datetime import datetime, timedelta

def generate_sample_license():
    """Generate a sample PyArmor license with embedded plan data"""
    
    # Sample license data (this would come from your subscription server)
    license_data = {
        "plan": "starter",
        "agents": ["agent1", "agent2"],
        "rate_limit_per_min": 2,
        "expires_at": (datetime.now() + timedelta(days=30)).isoformat()
    }
    
    # Convert to JSON string for embedding
    data_json = json.dumps(license_data)
    
    # Calculate expiry date for PyArmor
    expiry_date = (datetime.now() + timedelta(days=30)).strftime("%Y-%m-%d")
    
    print(f"🔑 Generating sample license with data: {data_json}")
    
    try:
        # Generate PyArmor license with embedded data
        cmd = [
            "pyarmor", "licenses",
            "--expired", expiry_date,
            "--data", data_json,
            "sample_license"
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True, cwd=Path.cwd())
        
        if result.returncode == 0:
            print("✅ Sample license generated successfully!")
            
            # Look for the generated license file
            license_file = Path("licenses/sample_license/license.lic")
            if license_file.exists():
                print(f"📄 License file created: {license_file}")
                
                # Copy to current directory for easy access
                target_file = Path("license.lic")
                import shutil
                shutil.copy2(license_file, target_file)
                print(f"📋 License copied to: {target_file}")
                
                return True
            else:
                print("⚠️ License file not found in expected location")
                print("Available files:")
                licenses_dir = Path("licenses")
                if licenses_dir.exists():
                    for file in licenses_dir.rglob("*"):
                        print(f"  - {file}")
        else:
            print("❌ License generation failed:")
            print("STDOUT:", result.stdout)
            print("STDERR:", result.stderr)
            
    except FileNotFoundError:
        print("❌ PyArmor not found. Please install with: pip install pyarmor")
        return False
    except Exception as e:
        print(f"❌ Error generating license: {e}")
        return False
    
    return False

def generate_fallback_json():
    """Generate a fallback JSON license for testing without PyArmor"""
    license_data = {
        "plan": "starter",
        "agents": ["agent1", "agent2"],
        "rate_limit_per_min": 2,
        "expires_at": (datetime.now() + timedelta(days=30)).isoformat()
    }
    
    json_file = Path("sample_license.json")
    with open(json_file, "w") as f:
        json.dump(license_data, f, indent=2)
    
    print(f"📄 Fallback JSON license created: {json_file}")
    print("You can copy this JSON content to test the application")
    return True

if __name__ == "__main__":
    print("🚀 PyArmor License Generator")
    print("=" * 40)
    
    success = generate_sample_license()
    
    if not success:
        print("\n🔄 Generating fallback JSON license...")
        generate_fallback_json()
    
    print("\n✅ Done! You can now test the client application.")