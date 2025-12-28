import json
import os
from datetime import datetime
from typing import Any, Dict, Optional

# Global sanitization setting
_global_sanitization_enabled = True


def set_sanitization_enabled(enabled: bool) -> None:
    """Sets the global sanitization setting"""
    global _global_sanitization_enabled
    _global_sanitization_enabled = enabled


def sanitize_for_logging(data: Any, enable_sanitization: bool = True) -> Any:
    """
    Sanitizes data for logging (removes sensitive information)
    Only redacts string values that match sensitive patterns, not numeric counters
    """
    if not enable_sanitization:
        return data

    if not data or not isinstance(data, dict):
        return data

    # Fields that should never be redacted (counters, statistics, IDs)
    allowed_fields = [
        "statusCode",
        "durationMs",
        "messageId",
        "keyId",
        "apiId",
        "username",
        "expiration",
        "exp",
        "sub",
    ]

    # Sensitive patterns that should trigger redaction (only for string values)
    sensitive_patterns = [
        r"^apiKey$",
        r"^key$",
        r"token",
        r"secret",
        r"password",
        r"authorization",
        r"credential",
        r"auth",
    ]

    import re

    sanitized = {**data}

    for key in sanitized:
        lower_key = key.lower()

        # Skip if field is in allowed list
        if any(lower_key == af.lower() for af in allowed_fields):
            continue

        # Only redact string values that match sensitive patterns
        if isinstance(sanitized[key], str) and any(
            re.search(pattern, key, re.IGNORECASE) for pattern in sensitive_patterns
        ):
            sanitized[key] = "[REDACTED]"
        elif isinstance(sanitized[key], dict) and sanitized[key] is not None:
            sanitized[key] = sanitize_for_logging(sanitized[key], enable_sanitization)
        elif isinstance(sanitized[key], list):
            # Handle lists by sanitizing each item if it's a dict
            sanitized[key] = [
                sanitize_for_logging(item, enable_sanitization) if isinstance(item, dict) else item
                for item in sanitized[key]
            ]

    return sanitized


class Logger:
    """Structured logging configuration"""

    def __init__(self, enable_sanitization: bool = True):
        self.enable_sanitization = enable_sanitization

    def info(self, message: str, data: Optional[Dict[str, Any]] = None) -> None:
        """Logs an info message"""
        log_entry = {
            "level": "INFO",
            "message": message,
            "timestamp": datetime.utcnow().isoformat() + "Z",
        }
        if data:
            log_entry.update(
                sanitize_for_logging(data, self.enable_sanitization)
            )
        print(json.dumps(log_entry))

    def error(
        self,
        message: str,
        error: Optional[Exception] = None,
        data: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Logs an error message"""
        error_info = {}
        if error:
            error_info = {
                "name": type(error).__name__,
                "message": str(error),
            }
            # Add error code if available
            if hasattr(error, "code"):
                error_info["code"] = error.code
            if hasattr(error, "response"):
                if hasattr(error.response, "get"):
                    metadata = error.response.get("ResponseMetadata", {})
                    if isinstance(metadata, dict):
                        http_status = metadata.get("HTTPStatusCode")
                        if http_status:
                            error_info["statusCode"] = http_status

        log_entry = {
            "level": "ERROR",
            "message": message,
            "timestamp": datetime.utcnow().isoformat() + "Z",
        }
        if error_info:
            log_entry["error"] = error_info
        if data:
            log_entry.update(
                sanitize_for_logging(data, self.enable_sanitization)
            )
        print(json.dumps(log_entry))

    def warn(self, message: str, data: Optional[Dict[str, Any]] = None) -> None:
        """Logs a warning message"""
        log_entry = {
            "level": "WARN",
            "message": message,
            "timestamp": datetime.utcnow().isoformat() + "Z",
        }
        if data:
            log_entry.update(
                sanitize_for_logging(data, self.enable_sanitization)
            )
        print(json.dumps(log_entry))


# Global logger instance
logger = Logger(
    enable_sanitization=os.environ.get("ENABLE_SANITIZATION", "true").lower()
    != "false"
)

