import os
from typing import Dict, Any
from langchain_openai import OpenAI, ChatOpenAI
from langchain.llms import Ollama
from langchain_anthropic import ChatAnthropic
from langchain_google_genai import GoogleGenerativeAI
from langchain.schema.language_model import BaseLanguageModel
from dotenv import load_dotenv

load_dotenv()


class LLMHandler:
    """
    Dynamic LLM handler for CrewAI agents.
    Supports multiple providers: OpenAI, Anthropic, Google, Ollama
    # Example usage and configuration
    # Example 1: Using the new dynamic handler
    openai_handler = LLMHandler.create_openai('gpt-4', temperature=0.2)
    openai_llm = openai_handler.get_llm()

    # Example 2: Using configuration dictionary
    config = {
        'provider': 'anthropic',
        'model': 'claude-3-sonnet-20240229',
        'temperature': 0.1,
        'max_tokens': 2000
    }
    claude_handler = LLMHandler.from_config(config)
    claude_llm = claude_handler.get_llm()

    # # Example 3: Using configuration dictionary for openrouter
    # config = {
    #     'provider': 'openrouter',
    #     'model': 'meta-llama/llama-3.1-70b-instruct',
    #     'temperature': 0.1,
    #     'max_tokens': 2000
    # }
    # llama_handler = LLMHandler.from_config(config)
    """

    # Default configurations for different providers
    DEFAULT_CONFIGS = {
        'openai': {
            'temperature': 0.1,
            'max_tokens': 3000,
            'top_p': 1,
            'frequency_penalty': 0,
            'presence_penalty': 0
        },
        # 'openrouter': {
        #     'temperature': 0.1,
        #     'max_tokens': 3000,
        #     'top_p': 1,
        #     'frequency_penalty': 0,
        #     'presence_penalty': 0
        # },
        'anthropic': {
            'temperature': 0.1,
            'max_tokens': 3000,
            'top_p': 1
        },
        'google': {
            'temperature': 0.1,
            'max_output_tokens': 3000,
            'top_p': 1
        },
        'ollama': {
            'temperature': 0.1,
            'num_predict': 3000,
            'top_p': 1
        }
    }

    # Available models for each provider
    AVAILABLE_MODELS = {
        'openai': [
            'gpt-4o', 'gpt-4o-mini', 'gpt-4-turbo', 'gpt-4',
            'gpt-3.5-turbo', 'gpt-3.5-turbo-16k'
        ],
        # 'openrouter': [
        #     # OpenAI models via OpenRouter
        #     'openai/gpt-4o', 'openai/gpt-4o-mini',
        #     # Anthropic models via OpenRouter
        #     'anthropic/claude-3.5-sonnet', 'anthropic/claude-3-opus',
        #     # Google models via OpenRouter
        #     'google/gemini-pro', 'google/gemini-pro-vision', 'google/gemma-3n-e4b-it:free', 'google/gemini-flash-1.5',
        #     # Meta models via OpenRouter
        #     'meta-llama/llama-3.1-405b-instruct', 'meta-llama/llama-3.1-70b-instruct',
        #     # Mistral models via OpenRouter
        #     'mistralai/mistral-large', 'mistralai/mistral-medium', 'mistralai/mistral-small-3.2-24b-instruct:free',
        #     # Other popular models
        #     'deepseek/deepseek-chat',
        # ],
        'anthropic': [
            'claude-3-5-sonnet-20241022', 'claude-3-opus-20240229',
            'claude-3-sonnet-20240229', 'claude-3-haiku-20240307'
        ],
        'google': [
            'gemini-pro', 'gemini-pro-vision', 'gemini-1.5-pro', 'gemini-2.0-flash',
            'gemini-1.5-flash', 'gemini-2.0-flash-lite'
        ],
        'ollama': [
            'llama3', 'llama3.1', 'llama3.2', 'mistral', 'codellama',
            'dolphin-mistral', 'neural-chat', 'starling-lm'
        ]
    }

    def __init__(self, provider: str = 'openai', model: str = None, **kwargs):
        """
        Initialize LLM handler.

        Args:
            provider: LLM provider ('openai', 'openrouter', 'anthropic', 'google', 'ollama')
            model: Specific model name (uses default if not specified)
            **kwargs: Additional configuration parameters
        """
        self.provider = provider.lower()
        self.model = model
        self.config = kwargs

        # Validate provider
        if self.provider not in self.DEFAULT_CONFIGS:
            raise ValueError(f"Unsupported provider: {provider}. "
                             f"Supported providers: {list(self.DEFAULT_CONFIGS.keys())}")

        # Set default model if not specified
        if not self.model:
            self.model = self._get_default_model()

        # Validate model
        if self.model not in self.AVAILABLE_MODELS[self.provider]:
            print(
                f"Warning: Model '{self.model}' not in known models for {self.provider}")

    def _get_default_model(self) -> str:
        """Get default model for the provider."""
        defaults = {
            'openai': 'gpt-3.5-turbo',
            # 'openrouter': 'openai/gpt-3.5-turbo',
            'anthropic': 'claude-3-haiku-20240307',
            'google': 'gemini-pro',
            'ollama': 'llama3'
        }
        return defaults[self.provider]

    def _merge_configs(self) -> Dict[str, Any]:
        """Merge default config with user-provided config."""
        base_config = self.DEFAULT_CONFIGS[self.provider].copy()
        base_config.update(self.config)
        return base_config

    def get_llm(self) -> BaseLanguageModel:
        """
        Get the configured LLM instance.

        Returns:
            BaseLanguageModel: Configured LLM instance
        """
        config = self._merge_configs()

        if self.provider == 'openai':
            return self._create_openai_llm(config)
        # elif self.provider == 'openrouter':
        #     return self._create_openrouter_llm(config)
        elif self.provider == 'anthropic':
            return self._create_anthropic_llm(config)
        elif self.provider == 'google':
            return self._create_google_llm(config)
        elif self.provider == 'ollama':
            return self._create_ollama_llm(config)
        else:
            raise ValueError(f"Unsupported provider: {self.provider}")

    def _create_openai_llm(self, config: Dict[str, Any]) -> ChatOpenAI:
        """Create OpenAI LLM instance."""
        return ChatOpenAI(
            model_name=self.model,
            **config
        )

    # def _create_openrouter_llm(self, config: Dict[str, Any]) -> ChatOpenAI:
    #     """Create OpenRouter LLM instance using OpenAI-compatible API."""
    #     # OpenRouter uses OpenAI-compatible API
    #     llm = OpenAI(
    #         model_name="openrouter/{self.model}",
    #         openai_api_base="https://openrouter.ai/api/v1",
    #         openai_api_key=os.getenv("OPENROUTER_API_KEY"),
    #         **config
    #     )
    #     return llm

    def _create_anthropic_llm(self, config: Dict[str, Any]) -> ChatAnthropic:
        """Create Anthropic LLM instance."""
        return ChatAnthropic(
            model=self.model,
            **config
        )

    def _create_google_llm(self, config: Dict[str, Any]) -> GoogleGenerativeAI:
        """Create Google LLM instance."""
        return GoogleGenerativeAI(
            model=self.model,
            **config
        )

    def _create_ollama_llm(self, config: Dict[str, Any]) -> Ollama:
        """Create Ollama LLM instance."""
        return Ollama(
            model=self.model,
            **config
        )

    @classmethod
    def create_openai(cls, model: str = 'gpt-3.5-turbo', **kwargs) -> 'LLMHandler':
        """Convenience method to create OpenAI LLM handler."""
        return cls(provider='openai', model=model, **kwargs)

    # @classmethod
    # def create_openrouter(cls, model: str = 'openai/gpt-3.5-turbo', **kwargs) -> 'LLMHandler':
    #     """Convenience method to create OpenRouter LLM handler."""
    #     return cls(provider='openrouter', model=model, **kwargs)

    @classmethod
    def create_anthropic(cls, model: str = 'claude-3-haiku-20240307', **kwargs) -> 'LLMHandler':
        """Convenience method to create Anthropic LLM handler."""
        return cls(provider='anthropic', model=model, **kwargs)

    @classmethod
    def create_google(cls, model: str = 'gemini-pro', **kwargs) -> 'LLMHandler':
        """Convenience method to create Google LLM handler."""
        return cls(provider='google', model=model, **kwargs)

    @classmethod
    def create_ollama(cls, model: str = 'llama3', **kwargs) -> 'LLMHandler':
        """Convenience method to create Ollama LLM handler."""
        return cls(provider='ollama', model=model, **kwargs)

    @classmethod
    def from_config(cls, config: Dict[str, Any]) -> 'LLMHandler':
        """
        Create LLM handler from configuration dictionary.

        Args:
            config: Configuration dictionary with 'provider', 'model', and other params

        Returns:
            LLMHandler: Configured LLM handler
        """
        provider = config.pop('provider', 'openai')
        model = config.pop('model', None)
        return cls(provider=provider, model=model, **config)

    def __repr__(self) -> str:
        return f"LLMHandler(provider='{self.provider}', model='{self.model}')"
