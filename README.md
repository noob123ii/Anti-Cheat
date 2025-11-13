# AntiCheat API Server

FastAPI server with endpoints for AntiCheat functionality.

## 🚀 Deployment

### Netlify Deployment

This project is configured for Netlify deployment. To deploy:

1. **Push to GitHub** (already done!)
2. **Connect to Netlify**:
   - Go to [netlify.com](https://netlify.com)
   - Click "Add new site" → "Import an existing project"
   - Connect your GitHub account
   - Select the repository: `noob123ii/Anti-Cheat`
   - Netlify will auto-detect the configuration from `netlify.toml`
   - Click "Deploy site"!

3. **Important Notes for Netlify**:
   - File-based storage (JSON files) uses `/tmp` which is temporary
   - For production, consider using:
     - **Netlify Functions** with external storage
     - **Supabase** or **MongoDB** for database
     - **Environment Variables** for configuration (set in Netlify Dashboard → Site settings → Environment variables)

### Local Development

## Setup Instructions

### Fix Windows Store Python Alias Issue

The Windows Store Python alias is preventing the `python` command from working. To fix this:

1. **Option 1: Disable Windows Store Python Alias (Recommended)**
   - Press `Windows Key + I` to open Settings
   - Go to **Apps** → **Advanced app settings** → **App execution aliases**
   - Find **python.exe** and **python3.exe** and turn them **OFF**
   - Restart your terminal/PowerShell

2. **Option 2: Use Full Python Path**
   - Find your Python installation (usually in `C:\Users\YourName\AppData\Local\Programs\Python\Python3XX\`)
   - Use the full path: `C:\Users\YourName\AppData\Local\Programs\Python\Python3XX\python.exe main.py`

3. **Option 3: Install Python from python.org**
   - Download Python from https://www.python.org/downloads/
   - During installation, check "Add Python to PATH"
   - This will override the Windows Store alias

## Running the Server

After fixing the Python alias issue, you can run the server using one of these methods:

### Method 1: Using Python directly
```bash
python main.py
```

### Method 2: Using uvicorn module
```bash
python -m uvicorn main:app --host 127.0.0.1 --port 8000
```

### Method 3: Using the batch file
```bash
start_server.bat
```

### Method 4: Using the PowerShell script
```powershell
powershell -ExecutionPolicy Bypass -File start_server.ps1
```

## Accessing the Server

Once running, access the server at:
- **Dashboard**: http://localhost:8000/
- **API Documentation**: http://localhost:8000/docs
- **Alternative ReDoc**: http://localhost:8000/redoc

## API Endpoints

All endpoints accept POST requests with JSON body containing `args` and `context`:

- `POST /AntiCheat/Config` - Configuration endpoint
- `POST /AntiCheat/DetectPlayer` - Player detection
- `POST /AntiCheat/DetectHeadset` - Headset detection  
- `POST /AntiCheat/DetectVpn` - VPN detection

### Example Request
```json
{
  "args": {
    "playerId": "12345",
    "playerData": {}
  },
  "context": {
    "sessionId": "abc123",
    "timestamp": "2024-01-01T00:00:00Z"
  }
}
```

## Dependencies

Install dependencies with:
```bash
pip install -r requirements.txt
```

Required packages:
- fastapi
- uvicorn
- jinja2

