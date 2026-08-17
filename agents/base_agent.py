import json
from typing import Any, Dict, List, Optional, Type

import ollama
from ollama import AsyncClient
from pydantic import BaseModel, Field


class AgentExecutionError(Exception):
    """Raised when an agent fails to reach Ollama or produce a usable response."""


class BaseAgent(BaseModel):
    name: str = Field(..., description="The unique name of the agent identifier.")
    model: str = Field(..., description="The specific local Ollama model string to target.")
    system_prompt: str = Field(..., description="The core persona guiding the agent's logic.")
    chat_history: List[Dict[str, str]] = Field(default_factory=list, description="Isolated multi-turn conversation log.")
    require_json: bool = Field(default=False, description="Forces the model to reply in strict JSON.")
    response_schema: Optional[Type[BaseModel]] = Field(
        default=None,
        description=(
            "Optional Pydantic model describing the expected JSON shape. When set together with "
            "require_json=True, Ollama is given the actual JSON Schema instead of generic JSON mode."
        ),
    )

    class Config:
        arbitrary_types_allowed = True

    def __init__(self, **data: Any):
        super().__init__(**data)
        if not self.chat_history:
            self.chat_history.append({"role": "system", "content": self.system_prompt})

    def _response_format(self):
        if not self.require_json:
            return ""
        return self.response_schema.model_json_schema() if self.response_schema else "json"

    def _handle_raw_content(self, raw_content: str) -> Any:
        self.chat_history.append({"role": "assistant", "content": raw_content})

        if not self.require_json:
            return raw_content

        try:
            parsed = json.loads(raw_content)
        except json.JSONDecodeError as e:
            raise AgentExecutionError(
                f"Agent '{self.name}' returned invalid JSON: {e}\nRaw output: {raw_content!r}"
            ) from e

        if self.response_schema:
            try:
                validated = self.response_schema.model_validate(parsed)
            except Exception as e:
                raise AgentExecutionError(
                    f"Agent '{self.name}' returned JSON that doesn't match its expected schema: {e}"
                ) from e
            return validated.model_dump()

        return parsed

    def execute(self, user_message: str) -> Optional[Dict[str, Any]]:
        """Synchronous single-shot call. Prefer `aexecute` when agents need to run concurrently."""
        self.chat_history.append({"role": "user", "content": user_message})
        try:
            response = ollama.chat(model=self.model, messages=self.chat_history, format=self._response_format())
            raw_content = response["message"]["content"]
        except Exception as e:
            raise AgentExecutionError(f"Agent '{self.name}' failed to reach Ollama: {e}") from e
        return self._handle_raw_content(raw_content)

    async def aexecute(self, user_message: str) -> Optional[Dict[str, Any]]:
        """
        Async single-shot call. This is what lets multiple agents (e.g. several
        Critic personas) hit Ollama at the same time via asyncio.gather /
        asyncio.as_completed instead of blocking one another sequentially.
        """
        self.chat_history.append({"role": "user", "content": user_message})
        try:
            client = AsyncClient()
            response = await client.chat(model=self.model, messages=self.chat_history, format=self._response_format())
            raw_content = response["message"]["content"]
        except Exception as e:
            raise AgentExecutionError(f"Agent '{self.name}' failed to reach Ollama: {e}") from e
        return self._handle_raw_content(raw_content)

    def prune_context(self, max_history: int = 5):
        """
        Truncates the chat history to the system prompt + the last N messages
        to prevent context window overflow.
        """
        if len(self.chat_history) > max_history + 1:
            self.chat_history = [self.chat_history[0]] + self.chat_history[-max_history:]
