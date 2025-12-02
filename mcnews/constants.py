PLUGIN_NAME = "astrbot_plugin_mcnews"

MC_VERSION_MANIFEST = "https://piston-meta.mojang.com/mc/game/version_manifest_v2.json"

MOJANG_SERVICES = [
    {
        "name": "Mojang Session Server",
        "url": "https://sessionserver.mojang.com/session/minecraft/profile/853c80ef3c3749fdaa49938b674adae6",
        "description": "Player profile & skin service"
    },
    {
        "name": "Minecraft Services API",
        "url": "https://api.minecraftservices.com/publickeys",
        "description": "Authentication & account service"
    },
    {
        "name": "Mojang API",
        "url": "https://api.mojang.com/users/profiles/minecraft/jeb_",
        "description": "Player lookup service"
    },
]

HTTP_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Accept": "application/json",
}

REQUEST_TIMEOUT = 30


REQUEST_TIMEOUT = 30
