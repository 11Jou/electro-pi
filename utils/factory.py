from core.config import settings
from modules.organization.services.chat_bot_service import *


def get_chat_bot_service() -> IChatBotService:
    print("Chat bot service: ", settings.CHAT_BOT_SERVICE)
    if settings.CHAT_BOT_SERVICE == "openai":
        return ChatGPTBotService(api_key=settings.OPENAI_API_KEY, mock=settings.MOCK)
    raise ValueError(f"Invalid chat bot service: {settings.CHAT_BOT_SERVICE}")