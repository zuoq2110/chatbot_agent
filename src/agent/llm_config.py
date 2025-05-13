from langchain_ollama import ChatOllama
from langchain.callbacks.manager import CallbackManager
from langchain.callbacks.tracers import LangChainTracer
from typing import Optional


class LLMConfig:
    """Configuration for language models used in the KMA Chat Agent."""
    
    DEFAULT_MODEL_NAME = "llama3.2"
    DEFAULT_PROJECT_NAME = "KMARegulation"
    
    @classmethod
    def create_llm(cls,
                  model_name: str = None,
                  callback_manager: Optional[CallbackManager] = None) -> ChatOllama:
        """Create a ChatOllama model instance with specified configuration.
        
        Args:
            model_name: Name of the model to use
            callback_manager: Optional callback manager for tracing
            
        Returns:
            Configured ChatOllama instance
        """
        if model_name is None:
            model_name = cls.DEFAULT_MODEL_NAME
        
        return ChatOllama(
            model=model_name,
            callback_manager=callback_manager
        )
    
    @classmethod
    def create_callback_manager(cls, project_name: str = None) -> CallbackManager:
        """Create a callback manager with LangSmith tracer.
        
        Args:
            project_name: Name of the project for LangSmith tracing
            
        Returns:
            Configured CallbackManager
        """
        if project_name is None:
            project_name = cls.DEFAULT_PROJECT_NAME
        
        return CallbackManager([LangChainTracer(project_name=project_name)]) 