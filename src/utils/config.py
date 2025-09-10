"""Environment configuration module with type-safe getters and validation."""

import os
from typing import Optional
from dotenv import load_dotenv

# Load variables from .env if present (doesn't override existing env by default)
load_dotenv(override=False)

# Constants for boolean parsing
_TRUTHY_VALUES = frozenset({"1", "true", "t", "yes", "y", "on"})
_FALSY_VALUES = frozenset({"0", "false", "f", "no", "n", "off"})


def get_bool(key: str, default: bool = False) -> bool:
    """Get boolean value from environment variable.

    Args:
        key: Environment variable name
        default: Default value if key doesn't exist or is invalid

    Returns:
        Boolean value parsed from environment variable
    """
    val = os.getenv(key)
    if val is None:
        return default

    normalized = val.strip().lower()
    if normalized in _TRUTHY_VALUES:
        return True
    if normalized in _FALSY_VALUES:
        return False
    return default


def get_str(key: str, default: Optional[str] = None) -> Optional[str]:
    """Get string value from environment variable.

    Args:
        key: Environment variable name
        default: Default value if key doesn't exist or is empty

    Returns:
        String value or default if not found/empty
    """
    val = os.getenv(key)
    return val if val is not None and val.strip() else default


def get_int(key: str, default: int) -> int:
    """Get integer value from environment variable.

    Args:
        key: Environment variable name
        default: Default value if key doesn't exist or is invalid

    Returns:
        Integer value parsed from environment variable
    """
    val = os.getenv(key, "").strip()
    if not val:
        return default

    try:
        return int(val)
    except ValueError:
        return default


def get_float(key: str, default: float) -> float:
    """Get float value from environment variable.

    Args:
        key: Environment variable name
        default: Default value if key doesn't exist or is invalid

    Returns:
        Float value parsed from environment variable
    """
    val = os.getenv(key, "").strip()
    if not val:
        return default

    try:
        return float(val)
    except ValueError:
        return default


# LLM Configuration
DEFAULT_LLM_PROVIDER = (get_str("DEFAULT_LLM_PROVIDER", "openai") or "openai").lower()
DEFAULT_LLM_MODEL = get_str("DEFAULT_LLM_MODEL")
LLM_TEMPERATURE = get_float("LLM_TEMPERATURE", 0.1)
LLM_MAX_TOKENS = get_int("LLM_MAX_TOKENS", 3000)

# API Keys
OPENROUTER_API_KEY = get_str("OPENROUTER_API_KEY")

# Docker and Browser Configuration
RUNNING_IN_DOCKER = get_bool("RUNNING_IN_DOCKER", False)
CHROME_BIN = get_str("CHROME_BIN", "")
CHROMEDRIVER = get_str("CHROMEDRIVER", "")


def validate_docker_config() -> None:
    """Validate Docker-specific configuration requirements.

    Raises:
        EnvironmentError: If required Docker environment variables are missing
    """
    if not RUNNING_IN_DOCKER:
        return

    missing = []
    if not CHROME_BIN:
        missing.append("CHROME_BIN")
    if not CHROMEDRIVER:
        missing.append("CHROMEDRIVER")

    if missing:
        raise EnvironmentError(
            f"Missing required environment variables when RUNNING_IN_DOCKER=true: {', '.join(missing)}"
        )


# Validate configuration on import
validate_docker_config()
