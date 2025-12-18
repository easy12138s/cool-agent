"""Helper functions for the Intelligent Agent Project"""

import logging
import json
import yaml
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)

def load_json_file(file_path: str) -> Dict[str, Any]:
    """Load a JSON file"""
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Failed to load JSON file {file_path}: {e}")
        raise

def save_json_file(file_path: str, data: Any) -> None:
    """Save data to a JSON file"""
    try:
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    except Exception as e:
        logger.error(f"Failed to save JSON file {file_path}: {e}")
        raise

def load_yaml_file(file_path: str) -> Dict[str, Any]:
    """Load a YAML file"""
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return yaml.safe_load(f)
    except Exception as e:
        logger.error(f"Failed to load YAML file {file_path}: {e}")
        raise

def save_yaml_file(file_path: str, data: Any) -> None:
    """Save data to a YAML file"""
    try:
        with open(file_path, "w", encoding="utf-8") as f:
            yaml.dump(data, f, default_flow_style=False, allow_unicode=True)
    except Exception as e:
        logger.error(f"Failed to save YAML file {file_path}: {e}")
        raise

def format_response(text: str, **kwargs: Any) -> str:
    """Format a response with the given kwargs"""
    try:
        return text.format(**kwargs)
    except KeyError as e:
        logger.error(f"Missing key in response format: {e}")
        return text

def truncate_text(text: str, max_length: int = 100) -> str:
    """Truncate text to the given max length"""
    if len(text) <= max_length:
        return text
    return text[:max_length] + "..."

def extract_json_from_text(text: str) -> Optional[Dict[str, Any]]:
    """Extract JSON from a text string"""
    import re
    try:
        # Look for JSON objects
        json_match = re.search(r"\{[^{}]*\}", text)
        if json_match:
            return json.loads(json_match.group())
        # Look for JSON arrays
        array_match = re.search(r"\[[^\[\]]*\]", text)
        if array_match:
            return {"result": json.loads(array_match.group())}
        return None
    except Exception as e:
        logger.error(f"Failed to extract JSON from text: {e}")
        return None

def generate_unique_id(prefix: str = "", length: int = 8) -> str:
    """Generate a unique ID"""
    import uuid
    return f"{prefix}{uuid.uuid4().hex[:length]}"
