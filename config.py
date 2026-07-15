from imports import *
config = {
    "default_llm": "custom",
    "llms": {
        "gemini": {
            "class": "Gemini",
            "module": "llm_providers.gemini",
            "api_key": os.environ['GEMINI_API_KEY'],
            "model": "gemini-3.1-flash-lite",
        },
        "custom": {
            "class": "Custom",
            "module": "llm_providers.custom",
            "api_key": os.environ['CUSTOM_API_KEY'],
            "model": "deepseek/deepseek-v4-pro",
            "base_url": "https://openrouter.ai/api/v1",
        }
    },
    "MINECRAFT_HOST": "localhost",
    "MINECRAFT_PORT": 25565,
    "MINECRAFT_VERSION": "1.21.1",
    "MINECRAFT_USERNAME": "AlyoshaGPT",
    "character": "default"

}