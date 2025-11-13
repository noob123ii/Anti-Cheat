from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, Dict, Any, List
import requests
import logging
import json
import os
from datetime import datetime, timedelta

app = FastAPI()

# Handle template directory for Netlify (functions run from netlify/functions/)
# Check if we're running on Netlify
_is_netlify = os.environ.get("NETLIFY") == "true" or os.environ.get("AWS_LAMBDA_FUNCTION_NAME") is not None
if _is_netlify:
    # On Netlify, templates are in the root directory relative to the function
    template_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "templates")
else:
    template_dir = "templates"

templates = Jinja2Templates(directory=template_dir)
logger = logging.getLogger(__name__)

# Add CORS middleware to fix Method Not Allowed issues
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configuration file paths
# On Netlify/Vercel, use /tmp for writable files (note: data won't persist between deployments)
# For production, consider using a database or external storage
NETLIFY_ENV = os.environ.get("NETLIFY") == "true" or os.environ.get("AWS_LAMBDA_FUNCTION_NAME") is not None
VERCEL_ENV = os.environ.get("VERCEL") == "1"
BASE_DIR = "/tmp" if (NETLIFY_ENV or VERCEL_ENV) else "."

CONFIG_FILE = os.path.join(BASE_DIR, "config.json")
BANNED_ACCOUNTS_FILE = os.path.join(BASE_DIR, "banned_accounts.json")
ALLOWED_ACCOUNTS_FILE = os.path.join(BASE_DIR, "allowed_accounts.json")

# Default configuration
DEFAULT_CONFIG = {
    "DEBUG_MODE": True,
    "BAN_DURATION_HOURS": 336,
    "KICK_DURATION_HOURS": 0,
    "BAN_WEBHOOK_URL": "https://discord.com/api/webhooks/1382442637218418689/xepEikNsDPCdcAgEF7-nLI3z1Q9sOXsJBNp6kfRsMEy3vYzYOn_cIQO9Jfiv2Mz5Fxhr",
    "ALLOWED_WEBHOOK_URL": "https://discord.com/api/webhooks/1385294311285067836/mWPvm76oHpXfBZVCWmAiK27GiFZyhECgsJlmfLFn3i7GOVvpAE59dFbVw0U16o8BYz_R",
    "ALLOWED_DEVICES": ["quest2", "oculus quest"],
    "AUTO_BAN_ENABLED": True,
    "VPN_DETECTION_ENABLED": True,
    "DEVICE_DETECTION_ENABLED": True,
    "PLAYER_DETECTION_ENABLED": True,
    "MAX_LOGIN_ATTEMPTS": 5,
    "LOGIN_COOLDOWN_SECONDS": 300,
    "ENABLE_WHITELIST": False,
    "ENABLE_BLACKLIST": True
}

# Load configuration from file
def load_config() -> Dict[str, Any]:
    """Load configuration from JSON file"""
    try:
        if os.path.exists(CONFIG_FILE):
            with open(CONFIG_FILE, 'r') as f:
                config = json.load(f)
                # Merge with defaults to ensure all keys exist
                return {**DEFAULT_CONFIG, **config}
        else:
            # Create default config file
            save_config(DEFAULT_CONFIG)
            return DEFAULT_CONFIG.copy()
    except Exception as e:
        logger.error(f"Error loading config: {e}")
        return DEFAULT_CONFIG.copy()

def save_config(config: Dict[str, Any]) -> bool:
    """Save configuration to JSON file"""
    try:
        with open(CONFIG_FILE, 'w') as f:
            json.dump(config, f, indent=2)
        return True
    except Exception as e:
        logger.error(f"Error saving config: {e}")
        return False

def get_config() -> Dict[str, Any]:
    """Get current configuration"""
    return load_config()

# Load banned accounts
def load_banned_accounts() -> List[Dict[str, Any]]:
    """Load banned accounts from JSON file"""
    try:
        if os.path.exists(BANNED_ACCOUNTS_FILE):
            with open(BANNED_ACCOUNTS_FILE, 'r') as f:
                return json.load(f)
        return []
    except Exception as e:
        logger.error(f"Error loading banned accounts: {e}")
        return []

def save_banned_account(account: Dict[str, Any]) -> bool:
    """Save a banned account to the list"""
    try:
        accounts = load_banned_accounts()
        # Check if account already exists, update it if so
        existing_index = next((i for i, acc in enumerate(accounts) if acc.get("playerId") == account.get("playerId")), None)
        if existing_index is not None:
            accounts[existing_index] = account
        else:
            accounts.append(account)
        with open(BANNED_ACCOUNTS_FILE, 'w') as f:
            json.dump(accounts, f, indent=2)
        return True
    except Exception as e:
        logger.error(f"Error saving banned account: {e}")
        return False

# Load allowed accounts
def load_allowed_accounts() -> List[Dict[str, Any]]:
    """Load allowed accounts from JSON file"""
    try:
        if os.path.exists(ALLOWED_ACCOUNTS_FILE):
            with open(ALLOWED_ACCOUNTS_FILE, 'r') as f:
                return json.load(f)
        return []
    except Exception as e:
        logger.error(f"Error loading allowed accounts: {e}")
        return []

def save_allowed_accounts(accounts: List[Dict[str, Any]]) -> bool:
    """Save allowed accounts list"""
    try:
        with open(ALLOWED_ACCOUNTS_FILE, 'w') as f:
            json.dump(accounts, f, indent=2)
        return True
    except Exception as e:
        logger.error(f"Error saving allowed accounts: {e}")
        return False

def is_account_allowed(player_id: str) -> bool:
    """Check if an account is in the allowed list"""
    allowed = load_allowed_accounts()
    return any(acc.get("playerId") == player_id for acc in allowed)

def add_allowed_account(player_id: str, player_name: str = "Unknown") -> bool:
    """Add an account to the allowed list"""
    try:
        accounts = load_allowed_accounts()
        # Check if already exists
        if not any(acc.get("playerId") == player_id for acc in accounts):
            accounts.append({
                "playerId": player_id,
                "playerName": player_name,
                "addedAt": datetime.utcnow().isoformat()
            })
            return save_allowed_accounts(accounts)
        return True
    except Exception as e:
        logger.error(f"Error adding allowed account: {e}")
        return False

def remove_allowed_account(player_id: str) -> bool:
    """Remove an account from the allowed list"""
    try:
        accounts = load_allowed_accounts()
        accounts = [acc for acc in accounts if acc.get("playerId") != player_id]
        return save_allowed_accounts(accounts)
    except Exception as e:
        logger.error(f"Error removing allowed account: {e}")
        return False

# Initialize config
config = get_config()


class CloudScriptRequest(BaseModel):
    args: Optional[Dict[str, Any]] = {}
    context: Optional[Dict[str, Any]] = {}


def send_discord_webhook(webhook_url: str, content: str, embed: Dict[str, Any]) -> bool:
    """Send a Discord webhook notification"""
    try:
        payload = {
            "content": content,
            "embeds": [embed]
        }
        response = requests.post(webhook_url, json=payload, timeout=5)
        return response.status_code in [200, 204]
    except Exception as e:
        logger.error(f"Webhook failed: {e}")
        return False


def classify_device_type(type_str: str, model: str, platform: str) -> str:
    """Classify device type based on type string, model, and platform"""
    type_lower = type_str.lower()
    model_lower = model.lower()
    platform_lower = platform.lower()
    
    if "vr" in type_lower or "quest" in model_lower or "vive" in model_lower or "index" in model_lower:
        return "VR Headset"
    if "desktop" in type_lower or "windows" in platform_lower:
        return "Desktop"
    if "mobile" in type_lower or "android" in platform_lower or "ios" in platform_lower:
        return "Mobile"
    return "Unknown"


@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    """Load and render the config controller page"""
    current_config = get_config()
    return templates.TemplateResponse("index.html", {
        "request": request,
        "title": "AntiCheat Config Controller",
        "config": current_config
    })


@app.get("/AntiCheat/Config")
async def get_anticheat_config():
    """
    AntiCheat Config API endpoint - GET
    Returns current configuration
    """
    try:
        current_config = get_config()
        return JSONResponse({
            "ResultCode": 0,
            "Message": "Config retrieved successfully",
            "config": current_config
        })
    except Exception as e:
        logger.error(f"❌ Error in Config: {str(e)}")
        return JSONResponse({
            "ResultCode": 1,
            "Message": "Internal error retrieving config.",
            "error": str(e)
        }, status_code=500)


@app.post("/AntiCheat/Config")
async def post_anticheat_config(request_data: CloudScriptRequest):
    """
    AntiCheat Config API endpoint - POST
    Returns configuration for cloudscript
    """
    try:
        current_config = get_config()
        args = request_data.args or {}
        context = request_data.context or {}
        
        # If updating config from cloudscript
        if "updateConfig" in args:
            new_config = args.get("config", {})
            # Validate and update
            for key in DEFAULT_CONFIG.keys():
                if key in new_config:
                    current_config[key] = new_config[key]
            save_config(current_config)
            return JSONResponse({
                "ResultCode": 0,
                "Message": "Config updated successfully",
                "config": current_config
            })
        
        # Return configuration for cloudscript
        return JSONResponse({
            "ResultCode": 0,
            "Message": "Config retrieved successfully",
            "config": {
                "DEBUG_MODE": current_config.get("DEBUG_MODE", True),
                "BAN_DURATION_HOURS": current_config.get("BAN_DURATION_HOURS", 336),
                "ALLOWED_DEVICES": current_config.get("ALLOWED_DEVICES", []),
                "webhooks": {
                    "ban": current_config.get("BAN_WEBHOOK_URL") is not None,
                    "allowed": current_config.get("ALLOWED_WEBHOOK_URL") is not None
                }
            }
        })
    except Exception as e:
        logger.error(f"❌ Error in Config: {str(e)}")
        return JSONResponse({
            "ResultCode": 1,
            "Message": "Internal error retrieving config.",
            "error": str(e)
        }, status_code=500)


@app.post("/api/config/update")
async def update_config(request: Request):
    """Update configuration from web UI"""
    try:
        data = await request.json()
        current_config = get_config()
        
        # Update all config values that are in DEFAULT_CONFIG
        for key in DEFAULT_CONFIG.keys():
            if key in data:
                default_value = DEFAULT_CONFIG[key]
                if isinstance(default_value, bool):
                    current_config[key] = bool(data[key])
                elif isinstance(default_value, int):
                    current_config[key] = int(data[key])
                elif isinstance(default_value, list):
                    if isinstance(data[key], str):
                        current_config[key] = [d.strip() for d in data[key].split(",") if d.strip()]
                    elif isinstance(data[key], list):
                        current_config[key] = data[key]
                else:
                    current_config[key] = str(data[key])
        
        save_config(current_config)
        return JSONResponse({
            "success": True,
            "message": "Configuration updated successfully",
            "config": current_config
        })
    except Exception as e:
        logger.error(f"❌ Error updating config: {str(e)}")
        return JSONResponse({
            "success": False,
            "message": f"Error updating config: {str(e)}"
        }, status_code=500)


@app.post("/AntiCheat/DetectPlayer")
async def detect_player(request_data: CloudScriptRequest):
    """
    AntiCheat DetectPlayer API endpoint
    Python equivalent of player detection cloudscript function
    Called by cloudscript with args and context
    Detects suspicious player behavior
    """
    try:
        args = request_data.args or {}
        context = request_data.context or {}
        
        # Extract player information (matches cloudscript structure)
        player_id = args.get("playerId") or context.get("currentPlayerId", "UNKNOWN_PLAYER")
        player_data = args.get("playerData", {})
        
        # Extract additional data from context
        ps_event = context.get("playStreamEvent", {})
        player_info = ps_event.get("PlayerInfo", {})
        
        # Detection logic (similar to cloudscript pattern)
        suspicious_activities = []
        detected = False
        reason = ""
        
        # Example detection checks (customize based on your needs)
        # Add your detection logic here similar to the device detection pattern
        if player_data.get("suspiciousActivity"):
            suspicious_activities.append("Suspicious activity detected")
            detected = True
        
        if player_data.get("unusualBehavior"):
            suspicious_activities.append("Unusual behavior pattern")
            detected = True
        
        # Get current config
        current_config = get_config()
        ban_duration = current_config.get("BAN_DURATION_HOURS", 336)
        
        # Create response (matches cloudscript return structure)
        if detected:
            reason = "; ".join(suspicious_activities) if suspicious_activities else "Suspicious behavior detected"
            logger.info(f"[DETECTED] {player_id} - {reason}")
            
            # Track banned account
            save_banned_account({
                "playerName": args.get("playerName", "Unknown"),
                "playerId": player_id,
                "hwid": args.get("hwid", "Unknown"),
                "ip": args.get("ipAddress", "Unknown"),
                "reason": reason,
                "banDuration": ban_duration,
                "bannedAt": datetime.utcnow().isoformat()
            })
            
            return {
                "ResultCode": 0,
                "Message": f"Player detection: {reason}",
                "shouldBan": True,
                "banDurationHours": ban_duration,
                "reason": reason,
                "playerId": player_id
            }
        else:
            if current_config.get("DEBUG_MODE", True):
                logger.info(f"[CLEAN] {player_id} - No suspicious activity")
            return {
                "ResultCode": 0,
                "Message": "Player check passed"
            }
            
    except Exception as e:
        logger.error(f"❌ Error in DetectPlayer: {str(e)}")
        return {
            "ResultCode": 1,
            "Message": "Internal error during player detection."
        }


@app.post("/AntiCheat/DetectHeadset")
async def detect_headset(request_data: CloudScriptRequest):
    """
    AntiCheat DetectHeadset API endpoint - Device verification
    Python equivalent of VerifyQuestDevice cloudscript function
    Called by cloudscript with args and context
    """
    try:
        args = request_data.args or {}
        context = request_data.context or {}
        
        # Extract PlayStream event data from context (matches cloudscript structure)
        ps_event = context.get("playStreamEvent", {})
        info = ps_event.get("DeviceInfo", args.get("deviceInfo", {}))
        
        # Extract device information (exact match to JavaScript)
        model = (info.get("DeviceModel") or info.get("Model") or "Unknown").lower()
        platform = (info.get("Platform") or "Unknown").lower()
        os = info.get("OperatingSystem", "Unknown")
        cpu = info.get("CentralProcessingUnit", "Unknown")
        ram = info.get("SystemMemorySize", "Unknown")
        gpu = info.get("GraphicsDeviceName", "Unknown")
        gpu_memory = info.get("GraphicsMemorySize", "Unknown")
        shader_level = info.get("GraphicsShaderLevel", "Unknown")
        raw_device_type = info.get("DeviceType", "Unknown")
        device_id = info.get("DeviceID") or info.get("DeviceId", "Unknown")
        unique_id = info.get("DeviceUniqueId", "Unknown")
        
        # Extract HWID (matches JavaScript logic)
        hwid_raw = info.get("DataPath")
        if isinstance(hwid_raw, str):
            hwid_parts = hwid_raw.split("/")
            hwid = hwid_parts[3] if len(hwid_parts) > 3 else hwid_raw
        else:
            hwid = "Unknown"
        
        # Get current config
        current_config = get_config()
        allowed_devices = current_config.get("ALLOWED_DEVICES", ["quest2", "oculus quest"])
        ban_duration = current_config.get("BAN_DURATION_HOURS", 336)
        allowed_webhook = current_config.get("ALLOWED_WEBHOOK_URL", "")
        ban_webhook = current_config.get("BAN_WEBHOOK_URL", "")
        
        # Get player ID from args or context (matches cloudscript)
        player_id = args.get("playerId") or context.get("currentPlayerId", "UNKNOWN_PLAYER")
        
        # Anti-cheat checks
        detection_reasons = []
        
        # Check Oculus Custom ID validation
        oculus_custom_id = info.get("OculusCustomId") or info.get("CustomId") or info.get("OculusID") or ""
        if oculus_custom_id:
            oculus_custom_id_upper = oculus_custom_id.upper()
            # Check for OCULUS0 (impossible, indicates hacking)
            if oculus_custom_id_upper == "OCULUS0":
                detection_reasons.append("Invalid Oculus Custom ID (OCULUS0 is impossible)")
            # Check if it starts with OCULUS and has valid format (OCULUS1-9)
            elif oculus_custom_id_upper.startswith("OCULUS"):
                # Extract the number part
                try:
                    number_part = oculus_custom_id_upper.replace("OCULUS", "").strip()
                    if number_part:
                        num = int(number_part)
                        if num < 1 or num > 9:
                            detection_reasons.append(f"Invalid Oculus Custom ID number ({num}, must be 1-9)")
                except ValueError:
                    detection_reasons.append("Invalid Oculus Custom ID format")
            
            # Check Oculus Custom ID length (typically 7-20 characters)
            if len(oculus_custom_id) < 7 or len(oculus_custom_id) > 20:
                detection_reasons.append(f"Invalid Oculus Custom ID length ({len(oculus_custom_id)}, expected 7-20)")
        
        # Check Player ID length (PlayFab IDs are typically 17 characters, but can vary)
        # Suspicious if too short (likely fake) or too long (manipulated)
        if player_id and player_id != "UNKNOWN_PLAYER":
            player_id_len = len(player_id)
            # PlayFab IDs are usually 17 chars, but can be 8-32. Suspicious if outside this range
            if player_id_len < 8 or player_id_len > 32:
                detection_reasons.append(f"Suspicious Player ID length ({player_id_len}, expected 8-32)")
            # Very suspicious if exactly a common fake length
            elif player_id_len in [4, 5, 6, 7]:
                detection_reasons.append(f"Suspicious Player ID length ({player_id_len}, likely fake)")
        
        # Check if using valid Oculus integration
        # Look for Oculus-specific identifiers
        oculus_indicators = [
            info.get("OculusPlatform"),
            info.get("OculusUserID"),
            info.get("OculusSessionID"),
            unique_id if "oculus" in unique_id.lower() else None
        ]
        has_oculus_integration = any(indicator for indicator in oculus_indicators if indicator)
        
        # If device claims to be Quest/Oculus but no Oculus integration found, suspicious
        if ("quest" in model or "oculus" in model or "oculus" in platform) and not has_oculus_integration:
            if oculus_custom_id:  # Only flag if they provided a custom ID but no integration
                detection_reasons.append("Oculus device detected but no valid Oculus integration API found")
        
        # Classify device type (matches JavaScript classifyDeviceType function)
        device_type_classified = classify_device_type(raw_device_type, model, platform)
        
        # Check if device is allowed (matches JavaScript logic)
        is_allowed = any(allowed in model or allowed in platform for allowed in allowed_devices)
        
        # If any detection reasons found, mark as not allowed
        if detection_reasons:
            is_allowed = False
        
        # Check ban reasons (matches JavaScript REASON_MAP)
        reason_map = [
            {
                "condition": lambda i: "vbox" in (i.get("DeviceModel") or "").lower(),
                "reason": "VirtualBox Detected"
            },
            {
                "condition": lambda i: "unknown" in (i.get("Platform") or "").lower(),
                "reason": "Unknown platform"
            },
            {
                "condition": lambda i: device_type_classified == "Desktop",
                "reason": "Running on Desktop"
            },
            {
                "condition": lambda i: device_type_classified == "Mobile",
                "reason": "Running on Mobile"
            }
        ]
        
        matched_reasons = [r["reason"] for r in reason_map if r["condition"](info)]
        
        # Combine all detection reasons
        all_reasons = detection_reasons + matched_reasons
        reason = "Allowed device" if is_allowed else ("; ".join(all_reasons) if all_reasons else "Disallowed/unknown device")
        
        # Create Discord embed (exact match to JavaScript embed structure)
        embed = {
            "title": "✅ Allowed Device Logged" if is_allowed else "🚫 Banned Device Detected",
            "color": 65280 if is_allowed else 16711680,  # Green (65280) or Red (16711680)
            "description": (
                f"**🧍 User:** `{player_id}`\n"
                f"**📱 Device:** `{model}`\n"
                f"**📡 Platform:** `{platform}`\n"
                f"**🧠 Device Type:** `{device_type_classified}`\n"
                f"**🔒 HWID:** `{hwid}`\n"
                f"**🆔 Oculus Custom ID:** `{oculus_custom_id if oculus_custom_id else 'Not provided'}`\n"
                f"**📄 Reason:** `{reason}`"
            ),
            "fields": [
                {
                    "name": "💻 System",
                    "value": (
                        f"• OS: `{os}`\n"
                        f"• CPU: `{cpu}`\n"
                        f"• RAM: `{ram}MB`"
                    ),
                    "inline": True
                },
                {
                    "name": "🎮 Graphics",
                    "value": (
                        f"• GPU: `{gpu} ({gpu_memory}MB)`\n"
                        f"• Shader Level: `{shader_level}`"
                    ),
                    "inline": True
                },
                {
                    "name": "🔐 IDs",
                    "value": (
                        f"• Device ID: `{device_id}`\n"
                        f"• Unique ID: `{unique_id}`\n"
                        f"• Oculus Custom ID: `{oculus_custom_id if oculus_custom_id else 'Not provided'}`\n"
                        f"• Player ID Length: `{len(player_id)}`\n"
                        f"• Type (Raw): `{raw_device_type}`"
                    ),
                    "inline": False
                }
            ],
            "timestamp": datetime.utcnow().isoformat()
        }
        
        # Send Discord webhook (matches JavaScript webhook logic)
        webhook_url = allowed_webhook if is_allowed else ban_webhook
        content = "🟢 Allowed device accessed the system" if is_allowed else "🔴 Ban triggered"
        if webhook_url:
            webhook_sent = send_discord_webhook(webhook_url, content, embed)
            if not webhook_sent:
                logger.warning(f"⚠️ Webhook failed for player {player_id}")
        
        # Return response (matches JavaScript return structure)
        if is_allowed:
            if current_config.get("DEBUG_MODE", True):
                logger.info(f"[ALLOWED] {player_id} logged from {model}")
            return {
                "ResultCode": 0,
                "Message": "Access granted. Logged to allowed webhook."
            }
        else:
            # Track banned account
            save_banned_account({
                "playerName": args.get("playerName", "Unknown"),
                "playerId": player_id,
                "hwid": hwid,
                "ip": args.get("ipAddress", "Unknown"),
                "reason": reason,
                "banDuration": ban_duration,
                "bannedAt": datetime.utcnow().isoformat()
            })
            
            # Note: The actual ban is handled by cloudscript using server.BanUsers
            # This endpoint returns the ban recommendation
            logger.info(f"[BANNED] {player_id} - {reason}")
            return {
                "ResultCode": 0,
                "Message": f"Banned for: {reason}",
                "shouldBan": True,
                "banDurationHours": ban_duration,
                "reason": reason,
                "playerId": player_id
            }
            
    except Exception as e:
        logger.error(f"❌ Error in DetectHeadset: {str(e)}")
        return {
            "ResultCode": 1,
            "Message": "Internal error during device check."
        }


@app.post("/AntiCheat/DetectVpn")
async def detect_vpn(request_data: CloudScriptRequest):
    """
    AntiCheat DetectVpn API endpoint
    Python equivalent of VPN detection cloudscript function
    Called by cloudscript with args and context
    Detects VPN/proxy usage
    """
    try:
        args = request_data.args or {}
        context = request_data.context or {}
        
        # Extract IP and network information (matches cloudscript structure)
        ip_address = args.get("ipAddress", "")
        network_data = args.get("networkData", {})
        player_id = args.get("playerId") or context.get("currentPlayerId", "UNKNOWN_PLAYER")
        
        # Extract from PlayStream event if available
        ps_event = context.get("playStreamEvent", {})
        location_info = ps_event.get("LocationInfo", {})
        
        # VPN detection logic (similar to cloudscript pattern)
        vpn_detected = False
        detection_reasons = []
        
        # Example detection checks (you can integrate with VPN detection APIs)
        if network_data.get("isVpn"):
            vpn_detected = True
            detection_reasons.append("VPN detected via network data")
        
        if network_data.get("isProxy"):
            vpn_detected = True
            detection_reasons.append("Proxy detected")
        
        if location_info.get("isVpn"):
            vpn_detected = True
            detection_reasons.append("VPN detected via location data")
        
        # Get current config
        current_config = get_config()
        ban_duration = current_config.get("BAN_DURATION_HOURS", 336)
        
        # Create response (matches cloudscript return structure)
        if vpn_detected:
            reason = "; ".join(detection_reasons) if detection_reasons else "VPN/Proxy detected"
            logger.info(f"[VPN DETECTED] {player_id} - {reason}")
            
            # Track banned account
            save_banned_account({
                "playerName": args.get("playerName", "Unknown"),
                "playerId": player_id,
                "hwid": args.get("hwid", "Unknown"),
                "ip": ip_address,
                "reason": reason,
                "banDuration": ban_duration,
                "bannedAt": datetime.utcnow().isoformat()
            })
            
            return {
                "ResultCode": 0,
                "Message": f"VPN/Proxy detected: {reason}",
                "shouldBan": True,
                "banDurationHours": ban_duration,
                "reason": reason,
                "ipAddress": ip_address,
                "playerId": player_id
            }
        else:
            if current_config.get("DEBUG_MODE", True):
                logger.info(f"[CLEAN IP] {player_id} - {ip_address}")
            return {
                "ResultCode": 0,
                "Message": "No VPN/Proxy detected"
            }
            
    except Exception as e:
        logger.error(f"❌ Error in DetectVpn: {str(e)}")
        return {
            "ResultCode": 1,
            "Message": "Internal error during VPN detection."
        }


def format_ban_duration(hours: float) -> str:
    """Format ban duration from hours to readable format (e.g., 1d, 3h, 20s)"""
    if hours <= 0:
        return "0s"
    
    total_seconds = int(hours * 3600)
    
    days = total_seconds // 86400
    remaining_seconds = total_seconds % 86400
    hours_part = remaining_seconds // 3600
    remaining_seconds = remaining_seconds % 3600
    minutes = remaining_seconds // 60
    seconds = remaining_seconds % 60
    
    parts = []
    if days > 0:
        parts.append(f"{days}d")
    if hours_part > 0:
        parts.append(f"{hours_part}h")
    if minutes > 0 and days == 0:  # Only show minutes if less than a day
        parts.append(f"{minutes}m")
    if seconds > 0 and days == 0 and hours_part == 0:  # Only show seconds if less than an hour
        parts.append(f"{seconds}s")
    
    return ", ".join(parts) if parts else "0s"


@app.get("/AntiCheat/BannedAccounts")
@app.post("/AntiCheat/BannedAccounts")
async def get_banned_accounts(request: Request):
    """
    Get all banned accounts with formatted display
    Returns list of banned accounts with player name, ID, HWID, IP, reason, and ban duration
    """
    try:
        accounts = load_banned_accounts()
        
        # Format accounts for display
        formatted_accounts = []
        for account in accounts:
            ban_duration_hours = account.get("banDuration", 336)
            formatted_duration = format_ban_duration(ban_duration_hours)
            
            formatted_accounts.append({
                "playerName": account.get("playerName", "Unknown"),
                "playerId": account.get("playerId", "Unknown"),
                "hwid": account.get("hwid", "Unknown"),
                "ip": account.get("ip", "Unknown"),
                "reason": account.get("reason", "Unknown"),
                "banDuration": formatted_duration,
                "banDurationHours": ban_duration_hours,
                "bannedAt": account.get("bannedAt", "Unknown")
            })
        
        return JSONResponse({
            "ResultCode": 0,
            "Message": "Banned accounts retrieved successfully",
            "accounts": formatted_accounts,
            "count": len(formatted_accounts)
        })
    except Exception as e:
        logger.error(f"❌ Error getting banned accounts: {str(e)}")
        return JSONResponse({
            "ResultCode": 1,
            "Message": "Internal error retrieving banned accounts.",
            "error": str(e)
        }, status_code=500)


@app.get("/AntiCheat/AllowedAccounts")
@app.post("/AntiCheat/AllowedAccounts")
async def get_allowed_accounts(request: Request):
    """Get all allowed accounts"""
    try:
        accounts = load_allowed_accounts()
        return JSONResponse({
            "ResultCode": 0,
            "Message": "Allowed accounts retrieved successfully",
            "accounts": accounts,
            "count": len(accounts)
        })
    except Exception as e:
        logger.error(f"❌ Error getting allowed accounts: {str(e)}")
        return JSONResponse({
            "ResultCode": 1,
            "Message": "Internal error retrieving allowed accounts.",
            "error": str(e)
        }, status_code=500)


@app.post("/api/console/command")
async def console_command(request: Request):
    """Execute console commands (ban, kick, config, etc.)"""
    try:
        data = await request.json()
        command = data.get("command", "").strip().lower()
        args = data.get("args", {})
        
        if command == "ban":
            player_id = args.get("playerId")
            player_name = args.get("playerName", "Unknown")
            reason = args.get("reason", "Manual ban from console")
            duration = args.get("duration", get_config().get("BAN_DURATION_HOURS", 336))
            
            if not player_id:
                return JSONResponse({
                    "success": False,
                    "message": "playerId is required"
                }, status_code=400)
            
            save_banned_account({
                "playerName": player_name,
                "playerId": player_id,
                "hwid": args.get("hwid", "Unknown"),
                "ip": args.get("ip", "Unknown"),
                "reason": reason,
                "banDuration": duration,
                "bannedAt": datetime.utcnow().isoformat(),
                "bannedBy": "Console"
            })
            
            logger.info(f"[CONSOLE BAN] {player_id} - {reason} ({duration}h)")
            return JSONResponse({
                "success": True,
                "message": f"Player {player_id} banned for {duration} hours",
                "playerId": player_id,
                "duration": duration
            })
        
        elif command == "kick":
            player_id = args.get("playerId")
            player_name = args.get("playerName", "Unknown")
            reason = args.get("reason", "Kicked from console")
            
            if not player_id:
                return JSONResponse({
                    "success": False,
                    "message": "playerId is required"
                }, status_code=400)
            
            # Kick = ban for 0 hours
            save_banned_account({
                "playerName": player_name,
                "playerId": player_id,
                "hwid": args.get("hwid", "Unknown"),
                "ip": args.get("ip", "Unknown"),
                "reason": reason,
                "banDuration": 0,
                "bannedAt": datetime.utcnow().isoformat(),
                "bannedBy": "Console (Kick)"
            })
            
            logger.info(f"[CONSOLE KICK] {player_id} - {reason}")
            return JSONResponse({
                "success": True,
                "message": f"Player {player_id} kicked",
                "playerId": player_id
            })
        
        elif command == "unban":
            player_id = args.get("playerId")
            if not player_id:
                return JSONResponse({
                    "success": False,
                    "message": "playerId is required"
                }, status_code=400)
            
            accounts = load_banned_accounts()
            accounts = [acc for acc in accounts if acc.get("playerId") != player_id]
            with open(BANNED_ACCOUNTS_FILE, 'w') as f:
                json.dump(accounts, f, indent=2)
            
            logger.info(f"[CONSOLE UNBAN] {player_id}")
            return JSONResponse({
                "success": True,
                "message": f"Player {player_id} unbanned",
                "playerId": player_id
            })
        
        elif command == "allow":
            player_id = args.get("playerId")
            player_name = args.get("playerName", "Unknown")
            
            if not player_id:
                return JSONResponse({
                    "success": False,
                    "message": "playerId is required"
                }, status_code=400)
            
            add_allowed_account(player_id, player_name)
            logger.info(f"[CONSOLE ALLOW] {player_id}")
            return JSONResponse({
                "success": True,
                "message": f"Player {player_id} added to allowed list",
                "playerId": player_id
            })
        
        elif command == "disallow":
            player_id = args.get("playerId")
            if not player_id:
                return JSONResponse({
                    "success": False,
                    "message": "playerId is required"
                }, status_code=400)
            
            remove_allowed_account(player_id)
            logger.info(f"[CONSOLE DISALLOW] {player_id}")
            return JSONResponse({
                "success": True,
                "message": f"Player {player_id} removed from allowed list",
                "playerId": player_id
            })
        
        elif command == "config":
            config_key = args.get("key")
            config_value = args.get("value")
            
            if not config_key:
                return JSONResponse({
                    "success": False,
                    "message": "key is required"
                }, status_code=400)
            
            current_config = get_config()
            if config_key in DEFAULT_CONFIG:
                # Type conversion based on default value type
                default_value = DEFAULT_CONFIG[config_key]
                if isinstance(default_value, bool):
                    current_config[config_key] = str(config_value).lower() in ("true", "1", "yes")
                elif isinstance(default_value, int):
                    current_config[config_key] = int(config_value)
                elif isinstance(default_value, list):
                    if isinstance(config_value, str):
                        current_config[config_key] = [v.strip() for v in config_value.split(",") if v.strip()]
                    else:
                        current_config[config_key] = config_value
                else:
                    current_config[config_key] = config_value
                
                save_config(current_config)
                logger.info(f"[CONSOLE CONFIG] {config_key} = {config_value}")
                return JSONResponse({
                    "success": True,
                    "message": f"Config {config_key} updated to {config_value}",
                    "key": config_key,
                    "value": current_config[config_key]
                })
            else:
                return JSONResponse({
                    "success": False,
                    "message": f"Unknown config key: {config_key}"
                }, status_code=400)
        
        else:
            return JSONResponse({
                "success": False,
                "message": f"Unknown command: {command}. Available: ban, kick, unban, allow, disallow, config"
            }, status_code=400)
            
    except Exception as e:
        logger.error(f"❌ Error executing console command: {str(e)}")
        return JSONResponse({
            "success": False,
            "message": f"Error executing command: {str(e)}"
        }, status_code=500)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)

