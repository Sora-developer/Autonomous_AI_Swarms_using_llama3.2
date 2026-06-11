import ollama
import json
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field

class BaseAgent(BaseModel):
    name: str = Field(..., description="The unique name of the agent identifier.")
    model: str = Field(..., description="The specific local Ollama model string to target.")
    system_prompt: str = Field(..., description="The core persona guiding the agent's logic.")
    chat_history: List[Dict[str, str]] = Field(default_factory=list, description="Isolated multi-turn conversation log.")
    require_json: bool = Field(default=False, description="Forces the model to reply in strict JSON.")

    class Config:
        arbitrary_types_allowed = True

    def __init__(self, **data: Any):
        super().__init__(**data)
        if not self.chat_history:
            self.chat_history.append({"role": "system", "content": self.system_prompt})

    def execute(self, user_message: str) -> Optional[Dict[str, Any]]:
        self.chat_history.append({"role": "user", "content": user_message})
        
        try:
            # Pass format='json' if require_json is True
            response = ollama.chat(
                model=self.model,
                messages=self.chat_history,
                format='json' if self.require_json else ''
            )
            
            raw_content = response['message']['content']
            self.chat_history.append({"role": "assistant", "content": raw_content})
            
            # If JSON is required, parse it before returning so it's ready for the next agent
            if self.require_json:
                return json.loads(raw_content)
            return raw_content
            
        except Exception as e:
            print(f"Error executing agent '{self.name}': {str(e)}")
            return None