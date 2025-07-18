from typing import List, Optional, Any
from langchain_core.language_models import BaseChatModel
from langchain_core.messages import BaseMessage, AIMessage, HumanMessage, SystemMessage
from huggingface_hub import InferenceClient
from pydantic import Field
import os

class HuggingFaceChatModel(BaseChatModel):
    """LangChain wrapper for Hugging Face InferenceClient."""
    
    client: InferenceClient = Field(default=None, exclude=True)
    model: str = Field(default="NousResearch/Hermes-2-Pro-Llama-3-8B")
    temperature: float = Field(default=0.7)
    max_tokens: int = Field(default=512)
    
    def __init__(self, model: str = "NousResearch/Hermes-2-Pro-Llama-3-8B", **kwargs):
        super().__init__(model=model, **kwargs)
        self.model = model
        self.client = InferenceClient(
            provider="novita",
            api_key=os.environ.get("HF_TOKEN"),
            model=model
        )
    
    def _generate(self, messages: List[BaseMessage], stop: Optional[List[str]] = None, **kwargs) -> AIMessage:
        hf_messages = []
        for msg in messages:
            role = "assistant" if isinstance(msg, AIMessage) else "user" if isinstance(msg, HumanMessage) else "system"
            hf_messages.append({"role": role, "content": msg.content})
        
        try:
            completion = self.client.chat.completions.create(
                model=self.model,
                messages=hf_messages,
                temperature=self.temperature,
                max_tokens=self.max_tokens,
                **kwargs
            )
            return AIMessage(content=completion.choices[0].message.content)
        except Exception as e:
            raise ValueError(f"Error invoking Hugging Face model: {str(e)}")
    
    async def _agenerate(self, messages: List[BaseMessage], stop: Optional[List[str]] = None, **kwargs) -> AIMessage:
        return self._generate(messages, stop, **kwargs)
    
    def bind_tools(self, tools: List[Any]) -> "HuggingFaceChatModel":
        self._tools = tools
        return self
    
    @property
    def _llm_type(self) -> str:
        return "huggingface_inference"

async def get_mistral_llm(model_name: str = "NousResearch/Hermes-2-Pro-Llama-3-8B") -> BaseChatModel:
    return HuggingFaceChatModel(model=model_name)