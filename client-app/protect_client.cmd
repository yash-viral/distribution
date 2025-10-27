@echo off
setlocal enabledelayedexpansion

echo 🔒 Protecting modular client backend with PyArmor...

:: Define paths
set "BACKEND_DIR=backend"
set "DIST_DIR=dist\backend"

:: Step 1: Clean existing dist directory
if exist "%DIST_DIR%" (
    echo 🧹 Removing old protected build...
    rmdir /S /Q "%DIST_DIR%"
)
mkdir "%DIST_DIR%"

:: Step 2: Run PyArmor protection
pyarmor gen --output "%DIST_DIR%" --recursive "%BACKEND_DIR%"
if %errorlevel% neq 0 (
    echo ❌ PyArmor protection failed.
    exit /b 1
)

echo ✅ Modular client backend protected successfully!
echo Protected files saved to: %DIST_DIR%

:: Step 3: Copy extra files if present
for %%F in (licenses public_key.pem requirements.txt) do (
    if exist "%BACKEND_DIR%\%%F" (
        if not exist "%DIST_DIR%\backend\%%F" (
            echo 📁 Copying %%F...
            if exist "%BACKEND_DIR%\%%F\" (
                xcopy "%BACKEND_DIR%\%%F" "%DIST_DIR%\backend\%%F" /E /I /Y >nul
            ) else (
                copy "%BACKEND_DIR%\%%F" "%DIST_DIR%\backend\%%F" >nul
            )
        )
    )
)

:: Step 4: Install dependencies if requirements.txt exists
if exist "%DIST_DIR%\backend\requirements.txt" (
    echo 📦 Installing dependencies for protected environment...
    python -m pip install -r "%DIST_DIR%\backend\requirements.txt"
    if %errorlevel% equ 0 (
        echo ✅ Dependencies installed successfully
    ) else (
        echo ⚠️ Warning: Some dependencies may not have installed.
    )
)

echo 🎉 Protection process complete!
endlocal
