from abc import ABC, abstractmethod
from typing import List, AsyncGenerator
from openai import AsyncOpenAI
from fastapi import HTTPException
from modules.organization.models import AuditLog


class IChatBotService(ABC):
    @abstractmethod
    async def generate_response(self, question: str, audit_logs: List[AuditLog]) -> str:
        pass

    @abstractmethod
    def stream_response(self, question: str, audit_logs: List[AuditLog]) -> AsyncGenerator[str, None]:
        pass


class ChatGPTBotService(IChatBotService):
    def __init__(self, api_key: str, mock: bool = False):
        self.client = AsyncOpenAI(api_key=api_key)
        self.model = "gpt-4o-mini"
        self.mock = mock

    def _build_system_prompt(self, audit_logs: List[AuditLog]) -> str:
        logs_text = "\n".join(
            f"- [{log.created_at}] user_id={log.user_id}: {log.action}"
            for log in audit_logs
        )
        return (
            "You are an assistant analyzing organization activity logs. "
            "Answer questions based only on the audit logs provided below.\n\n"
            f"Audit Logs:\n{logs_text or 'No logs available.'}"
        )

    async def generate_response(self, question: str, audit_logs: List[AuditLog]) -> str:
        print("Mock: ", self.mock)
        if self.mock:
            return "This is a mock response for prompt " + self._build_system_prompt(audit_logs)
        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": self._build_system_prompt(audit_logs)},
                    {"role": "user", "content": question},
                ],
                temperature=0.7,
            )
            return response.choices[0].message.content
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    async def stream_response(self, question: str, audit_logs: List[AuditLog]) -> AsyncGenerator[str, None]:
        if self.mock:
            yield "This is a mock response"
            return
        try:
            stream = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": self._build_system_prompt(audit_logs)},
                    {"role": "user", "content": question},
                ],
                temperature=0.7,
                stream=True,
            )
            async for chunk in stream:
                content = chunk.choices[0].delta.content
                if content:
                    yield content
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
