from abc import ABC, abstractmethod
from openai import OpenAI
from fastapi import HTTPException


class IChatBotService(ABC):
    @abstractmethod
    async def generate_response(self, message: str) -> str:
        pass



class ChatGPTBotService(IChatBotService):
    def __init__(self, api_key: str):
        self.client = OpenAI(api_key=api_key)
        self.model = "gpt-4o-mini"
        self.api_key = api_key
        self.mock = mock


    def generate_response(self, message: str) -> str:
        if self.mock:
            return "This is a mock response"
            
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": message}],
                temperature=0.7,
            )
            return response.choices[0].message.content
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))