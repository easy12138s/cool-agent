from typing import Any, Dict, List, Optional

from .context_desensitization import ContextDesensitization


class ContextManagement:
    def __init__(
        self,
        *,
        max_messages: int = 20,
        max_chars: int = 8000,
        desensitizer: Optional[ContextDesensitization] = None,
    ) -> None:
        if max_messages <= 0:
            raise ValueError("max_messages 必须为正整数")
        if max_chars <= 0:
            raise ValueError("max_chars 必须为正整数")
        self.max_messages = max_messages
        self.max_chars = max_chars
        self.desensitizer = desensitizer

    def build_context(self, messages: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        safe: List[Dict[str, Any]] = []
        for msg in messages:
            if not isinstance(msg, dict):
                continue
            role = msg.get("role")
            content = msg.get("content")
            if not isinstance(role, str) or not isinstance(content, str):
                continue
            safe.append(dict(msg))

        safe = safe[-self.max_messages :]

        def _total_chars(items: List[Dict[str, Any]]) -> int:
            return sum(len(str(m.get("content", ""))) for m in items)

        while safe and _total_chars(safe) > self.max_chars:
            safe.pop(0)

        if self.desensitizer:
            return self.desensitizer.desensitize_messages(safe)
        return safe
