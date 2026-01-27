"""
Utility functions for the Swiss History RAG project.
"""

import os
import yaml
from pathlib import Path
from dotenv import load_dotenv
from typing import Dict, Any

# Load environment variables
load_dotenv()


def load_config(config_path: str = "config/config.yaml") -> Dict[str, Any]:
    """
    Load configuration from YAML file.
    
    Args:
        config_path: Path to config file
        
    Returns:
        Dictionary with configuration
    """
    project_root = Path(__file__).parent.parent
    config_file = project_root / config_path
    
    with open(config_file, 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)
    
    return config


def get_env_variable(var_name: str, default: str = None) -> str:
    """
    Get environment variable with optional default.
    
    Args:
        var_name: Name of environment variable
        default: Default value if not found
        
    Returns:
        Value of environment variable
    """
    value = os.getenv(var_name, default)
    if value is None:
        raise ValueError(f"Environment variable {var_name} not set")
    return value


def get_project_root() -> Path:
    """
    Get the project root directory.
    
    Returns:
        Path to project root
    """
    return Path(__file__).parent.parent


def ensure_directories():
    """
    Ensure all necessary directories exist.
    """
    root = get_project_root()
    directories = [
        root / "data" / "raw",
        root / "data" / "processed",
        root / "data" / "chroma_db",
    ]
    
    for directory in directories:
        directory.mkdir(parents=True, exist_ok=True)
    
    print("✅ All directories created successfully")


if __name__ == "__main__":
    # Test configuration loading
    print("Testing configuration loading...")
    config = load_config()
    print(f"✅ Configuration loaded: {config['app']['title']}")
    
    # Ensure directories exist
    ensure_directories()
    
    # Test environment variables
    try:
        api_key = get_env_variable("OPENAI_API_KEY")
        print("✅ OpenAI API key found")
    except ValueError:
        print("⚠️  OpenAI API key not set - please configure .env file")
