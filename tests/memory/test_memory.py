import pytest

from src.agents.memory.context_desensitization import ContextDesensitization
from src.agents.memory.context_management import ContextManagement
from src.agents.memory.long_term_memory import LongTermMemory


def test_context_desensitization_masks_secrets() -> None:
    d = ContextDesensitization()
    text = "email=a@b.com sk-1234567890abcdef token=abcd Authorization: Bearer xyz"
    safe = d.desensitize_text(text)
    assert "***@b.com" in safe
    assert "sk-***" in safe
    assert "token=***" in safe
    assert "Authorization: Bearer ***" in safe


def test_context_management_trims_messages_and_chars() -> None:
    cm = ContextManagement(max_messages=2, max_chars=5)
    messages = [
        {"role": "user", "content": "123"},
        {"role": "assistant", "content": "45"},
        {"role": "user", "content": "6789"},
    ]
    ctx = cm.build_context(messages)
    assert ctx == [{"role": "user", "content": "6789"}]


def test_long_term_memory_add_and_search() -> None:
    mem = LongTermMemory()
    mem.add("今天要整理合同与发票", {"tag": "work"})
    mem.add("周末去爬山", {"tag": "life"})
    res = mem.search("合同", limit=5)
    assert len(res) == 1
    assert "合同" in res[0]["content"]

