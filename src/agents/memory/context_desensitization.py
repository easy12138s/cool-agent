import re
from typing import Any, Dict, Iterable, List


class ContextDesensitization:
    def __init__(self) -> None:
        self._email_re = re.compile(
            r"(?P<local>[A-Za-z0-9._%+-]{1,64})"
            r"@(?P<domain>[A-Za-z0-9.-]+\.[A-Za-z]{2,})"
        )
        self._openai_key_re = re.compile(r"\bsk-[A-Za-z0-9]{16,}\b")
        self._kv_secret_re = re.compile(
            r"(?i)\b(api[_-]?key|token|secret|password)\b\s*[:=]\s*([^\s,;\"']+)"
        )
        self._bearer_re = re.compile(r"(?i)\bAuthorization\b\s*:\s*Bearer\s+(\S+)")

    def desensitize_text(self, text: str) -> str:
        if not text:
            return text

        text = self._openai_key_re.sub("sk-***", text)

        def _mask_email(m: re.Match[str]) -> str:
            domain = m.group("domain")
            return f"***@{domain}"

        text = self._email_re.sub(_mask_email, text)

        def _mask_kv(m: re.Match[str]) -> str:
            key = m.group(1)
            return f"{key}=***"

        text = self._kv_secret_re.sub(_mask_kv, text)
        text = self._bearer_re.sub("Authorization: Bearer ***", text)
        return text

    def desensitize_messages(
        self, messages: Iterable[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        safe_messages: List[Dict[str, Any]] = []
        for msg in messages:
            if not isinstance(msg, dict):
                continue
            copied: Dict[str, Any] = dict(msg)
            content = copied.get("content")
            if isinstance(content, str):
                copied["content"] = self.desensitize_text(content)
            safe_messages.append(copied)
        return safe_messages
