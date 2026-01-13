import pytest

from src.agents.memory.context_desensitization import ContextDesensitization
from src.agents.memory.context_management import ContextManagement
from src.agents.memory.long_term_memory import LongTermMemory


def test_long_term_memory_add_get_delete_roundtrip() -> None:
    mem = LongTermMemory()

    item = mem.add("hello", {"k": "v"})
    got = mem.get(item.id)
    assert got is not None
    assert got.id == item.id
    assert got.content == "hello"
    assert got.metadata == {"k": "v"}

    assert mem.delete(item.id) is True
    assert mem.get(item.id) is None
    assert mem.delete(item.id) is False


def test_long_term_memory_add_validates_content() -> None:
    mem = LongTermMemory()
    with pytest.raises(ValueError):
        mem.add("")


def test_long_term_memory_list_recent_orders_by_created_at_desc() -> None:
    mem = LongTermMemory()
    first = mem.add("first")
    second = mem.add("second")

    recent = mem.list_recent(limit=2)
    assert [m.id for m in recent] == [second.id, first.id]


def test_long_term_memory_search_ranks_by_score_then_time() -> None:
    mem = LongTermMemory()

    low = mem.add("alpha betaX")
    high = mem.add("alpha beta")

    ranked = mem.search("alpha beta", limit=10)
    assert [r["id"] for r in ranked][:2] == [high.id, low.id]
    assert ranked[0]["score"] >= ranked[1]["score"]


def test_long_term_memory_search_empty_query_returns_recent() -> None:
    mem = LongTermMemory()
    a = mem.add("a")
    b = mem.add("b")

    ranked = mem.search("", limit=2)
    assert [r["id"] for r in ranked] == [b.id, a.id]
    assert all(r["score"] == 0.0 for r in ranked)


def test_context_desensitization_masks_secrets() -> None:
    d = ContextDesensitization()
    text = (
        "email=a@example.com sk-1234567890abcdef token=abc "
        "Authorization: Bearer supersecret"
    )
    masked = d.desensitize_text(text)
    assert "***@example.com" in masked
    assert "sk-***" in masked
    assert "token=***" in masked
    assert "Authorization: Bearer ***" in masked


def test_context_management_trims_and_desensitizes() -> None:
    d = ContextDesensitization()
    cm = ContextManagement(max_messages=2, max_chars=100, desensitizer=d)

    messages = [
        {"role": "user", "content": "a@example.com"},
        {"role": "assistant", "content": "x"},
        {"role": "user", "content": "sk-1234567890abcdef"},
        {"role": "assistant", "content": "y"},
        123,
        {"role": "user"},
    ]

    out = cm.build_context(messages)
    assert len(out) == 2
    assert out[0]["content"] == "sk-***"
    assert out[1]["content"] == "y"

