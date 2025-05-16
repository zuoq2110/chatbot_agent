import os

from langchain_core.language_models import BaseChatModel
from langchain_ollama import ChatOllama
from langchain.callbacks.manager import CallbackManager
from langchain.callbacks.tracers import LangChainTracer
from typing import Optional


class LLMConfig:
    """Configuration for language models used in the KMA Chat Agent."""
    
    DEFAULT_RAG_MODEL_NAME = "gemma3"
    DEFAULT_PROJECT_NAME = "KMA_CHAT"
    DEFAULT_GEMINI_MODEL = "gemini-2.0-flash"
    
    @classmethod
    def create_rag_llm(cls,
                  model_name: str = None,
                  callback_manager: Optional[CallbackManager] = None) -> ChatOllama:
        """Create a ChatOllama model instance with specified configuration.
        
        Args:
            model_name: Name of the model to use
            callback_manager: Optional callback manager for tracing
            
        Returns:
            Configured ChatOllama instance
        """
        from dotenv import load_dotenv

        # Load environment variables from .env file
        load_dotenv()

        # Get API key from environment
        rag_model = os.environ.get("RAG_MODEL")

        if model_name is None:
            if rag_model is not None:
                model_name = rag_model
            else:
                model_name = cls.DEFAULT_RAG_MODEL_NAME
        
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


# Utility function to get an LLM instance
def get_llm(model_name: str = None, project_name: str = None) -> BaseChatModel:
    """Get a configured LLM instance.
    
    Args:
        model_name: Optional model name to use
        project_name: Optional project name for LangSmith
        
    Returns:
        Configured ChatOllama instance
    """
    callback_manager = None
    if project_name:
        callback_manager = LLMConfig.create_callback_manager(project_name)

    return LLMConfig.create_rag_llm(model_name, callback_manager)


def get_gemini_llm():
    """Get a configured LLM instance for Gemini."""
    # Import here to avoid circular imports
    from dotenv import load_dotenv
    
    # Load environment variables from .env file
    load_dotenv()
    
    # Get API key from environment
    api_key = os.environ.get("GOOGLE_API_KEY")
    if not api_key:
        raise ValueError("GOOGLE_API_KEY not found in environment variables")
        
    from langchain_google_genai import ChatGoogleGenerativeAI

    model_name = os.environ.get("GEMINI_MODEL")
    if model_name is None:
        model_name = LLMConfig.DEFAULT_GEMINI_MODEL

    llm = ChatGoogleGenerativeAI(
        model=model_name,
        temperature=0,
        max_tokens=None,
        timeout=None,
        max_retries=2,
        google_api_key=api_key
    )

    return llm 