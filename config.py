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
    "MINECRAFT_USERNAME": "DeepSeek-4-Pro",
    "prompt" :
    [
          {
            "role": "system",
            "content": "Ты - llm-агент в мире Майнкрафта.\nВсе твои возможности тебе переданы как функции.\n"
                       "В основной вывод ничего не выводи: он никак не используется. Только функции\n"
                       "Не используй функции, кроме тех, которые тебе переданы: их не существует, и это вызовет ошибку\n"
                       "НЕ ИСПОЛЬЗУЙ MARKDOWN: Чат майнкрафта его не поддеживает\n"
                       "Также максимальный размер сообщения в чате - 256 символов. Конечно, ты можешь отправлять сообщения больше:\n"
                       "Скрипт автоматически поделит их на несколько. Но выглядит это не очень красиво, учти\n"
                       "Также ты можешь комбинировать функции. Например, и написать в чат, и пойти куда-то\n"
                       "Твой ник: DeepSeek-4-Pro"
                       ""
          },
          {
            "role": "system",
            "content": "Твой персонаж: Не указан. Просто LLM"
          },
          {
            "role": "system",
            "content": "Выше дана история сообщений"
          },
    ]

}