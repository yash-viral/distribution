#!/usr/bin/env python3
import subprocess
import sys
from pathlib import Path
import shutil

def protect_client():
    backend_dir = Path("backend")
    dist_dir = Path("dist") / "backend"

    if dist_dir.exists():
        shutil.rmtree(dist_dir)
    dist_dir.mkdir(parents=True, exist_ok=True)

    cmd = [
        "pyarmor", "gen",
        "--output", str(dist_dir),
        "--recursive",
        str(backend_dir)
    ]

    print("🔒 Protecting modular client backend with PyArmor...")
    result = subprocess.run(cmd, capture_output=True, text=True)

    if result.returncode == 0:
        print("✅ Modular client backend protected successfully!")
        print(f"Protected files saved to: {dist_dir}")
        
        # Copy any missing dependencies
        for item in ["licenses", "public_key.pem", "requirements.txt"]:
            src = backend_dir / item
            dst = dist_dir / "backend" / item
            if src.exists() and not dst.exists():
                if src.is_dir():
                    shutil.copytree(src, dst)
                else:
                    shutil.copy2(src, dst)
                print(f"📁 Copied {item}")
        
        # Install dependencies in the protected environment
        req_file = dist_dir / "backend" / "requirements.txt"
        if req_file.exists():
            print("📦 Installing dependencies for protected environment...")
            pip_result = subprocess.run([sys.executable, "-m", "pip", "install", "-r", str(req_file)], 
                                      capture_output=True, text=True)
            if pip_result.returncode == 0:
                print("✅ Dependencies installed successfully")
            else:
                print(f"⚠️ Warning: Some dependencies may not have installed: {pip_result.stderr}")
    else:
        print("❌ PyArmor protection failed:")
        print(result.stderr)

    return result.returncode == 0

if __name__ == "__main__":
    protect_client()
