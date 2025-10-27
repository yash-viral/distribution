# Client Chat Application with PyArmor Integration

## Setup Instructions

### 1. Install Dependencies
```bash
pip install -r requirements.txt
cd frontend
npm install
```

### 2. Generate Sample License (for testing)
```bash
python generate_sample_license.py
```

### 3. Protect Backend with PyArmor
```bash
python protect_client.py
```

### 4. Run Protected Backend
```bash
python run_protected.py
```

### 5. Run Frontend (in separate terminal)
```bash
cd frontend
npm run dev
```

## License Validation Methods

### Method 1: PyArmor License File (.lic)
1. **Generate License**: Run `python generate_sample_license.py` or get from subscription server
2. **Upload License**: Use the "License File" option in the client app
3. **Select File**: Choose the `.lic` file
4. **Validate**: Click "Validate License"

### Method 2: JSON License Data (Fallback)
1. **Get JSON**: Copy license JSON from subscription server or `sample_license.json`
2. **Paste JSON**: Use the "JSON License Data" option
3. **Validate**: Click "Validate License"

### Method 3: Existing License File
- If `license.lic` exists in the backend directory, click "Check Existing License"

## Usage Flow

1. **Open Client App**: Go to http://localhost:3001
2. **Validate License**: Use one of the methods above
3. **Chat**: Select an agent and start chatting (respects rate limits from license)

## Architecture

- **PyArmor**: Handles license validation, expiry, and machine binding
- **Business Logic**: Enforces rate limits, agent access, and plan restrictions
- **Embedded Data**: License files contain plan info (agents, rate limits, etc.)

## Ports
- Client App: http://localhost:8001 (backend) + http://localhost:3001 (frontend)
- Licensing Server: http://localhost:8000 (backend) + http://localhost:3000 (frontend)