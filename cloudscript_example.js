// Example CloudScript code to call the Python AntiCheat API
// Replace YOUR_API_URL with your actual server URL (e.g., "http://localhost:8000" or your deployed URL)

handlers.VerifyQuestDevice = function(args, context) {
    try {
        const API_URL = "YOUR_API_URL"; // e.g., "http://localhost:8000" or "https://your-domain.com"
        const currentPlayerId = currentPlayerId || "UNKNOWN_PLAYER";
        
        // Prepare the request payload
        const psEvent = context.playStreamEvent || {};
        const deviceInfo = psEvent.DeviceInfo || {};
        
        const requestPayload = {
            args: {
                playerId: currentPlayerId,
                deviceInfo: deviceInfo
            },
            context: {
                currentPlayerId: currentPlayerId,
                playStreamEvent: psEvent
            }
        };
        
        // Call the Python API endpoint
        const response = http.request(
            `${API_URL}/AntiCheat/DetectHeadset`,
            "POST",
            JSON.stringify(requestPayload),
            "application/json",
            null
        );
        
        if (!response || response.code !== 200) {
            log.error("⚠️ API request failed: " + (response ? response.code : "No response"));
            return { ResultCode: 1, Message: "Failed to verify device" };
        }
        
        const result = JSON.parse(response.body);
        
        // Check if ban is required
        if (result.shouldBan) {
            server.BanUsers({
                Bans: [{
                    PlayFabId: currentPlayerId,
                    DurationInHours: result.banDurationHours || 336,
                    Reason: result.reason || "Device verification failed"
                }]
            });
            log.info(`[BANNED] ${currentPlayerId} - ${result.reason}`);
        }
        
        return result;
        
    } catch (e) {
        log.error("❌ Error in VerifyQuestDevice: " + JSON.stringify(e));
        return { ResultCode: 1, Message: "Internal error during device check." };
    }
};

// Example: Player Detection Handler
handlers.DetectPlayerCheating = function(args, context) {
    try {
        const API_URL = "YOUR_API_URL";
        const currentPlayerId = currentPlayerId || "UNKNOWN_PLAYER";
        
        const requestPayload = {
            args: {
                playerId: currentPlayerId,
                playerData: args.playerData || {}
            },
            context: {
                currentPlayerId: currentPlayerId,
                playStreamEvent: context.playStreamEvent || {}
            }
        };
        
        const response = http.request(
            `${API_URL}/AntiCheat/DetectPlayer`,
            "POST",
            JSON.stringify(requestPayload),
            "application/json",
            null
        );
        
        if (!response || response.code !== 200) {
            return { ResultCode: 1, Message: "Failed to detect player" };
        }
        
        const result = JSON.parse(response.body);
        
        if (result.shouldBan) {
            server.BanUsers({
                Bans: [{
                    PlayFabId: currentPlayerId,
                    DurationInHours: result.banDurationHours || 336,
                    Reason: result.reason || "Cheating detected"
                }]
            });
        }
        
        return result;
        
    } catch (e) {
        log.error("❌ Error in DetectPlayerCheating: " + JSON.stringify(e));
        return { ResultCode: 1, Message: "Internal error during player detection." };
    }
};

// Example: VPN Detection Handler
handlers.DetectVpn = function(args, context) {
    try {
        const API_URL = "YOUR_API_URL";
        const currentPlayerId = currentPlayerId || "UNKNOWN_PLAYER";
        
        const requestPayload = {
            args: {
                playerId: currentPlayerId,
                ipAddress: args.ipAddress || "",
                networkData: args.networkData || {}
            },
            context: {
                currentPlayerId: currentPlayerId,
                playStreamEvent: context.playStreamEvent || {}
            }
        };
        
        const response = http.request(
            `${API_URL}/AntiCheat/DetectVpn`,
            "POST",
            JSON.stringify(requestPayload),
            "application/json",
            null
        );
        
        if (!response || response.code !== 200) {
            return { ResultCode: 1, Message: "Failed to detect VPN" };
        }
        
        const result = JSON.parse(response.body);
        
        if (result.shouldBan) {
            server.BanUsers({
                Bans: [{
                    PlayFabId: currentPlayerId,
                    DurationInHours: result.banDurationHours || 336,
                    Reason: result.reason || "VPN/Proxy detected"
                }]
            });
        }
        
        return result;
        
    } catch (e) {
        log.error("❌ Error in DetectVpn: " + JSON.stringify(e));
        return { ResultCode: 1, Message: "Internal error during VPN detection." };
    }
};

