from pathlib import Path

import httpx
import pytest

from src.api.run import app


@pytest.mark.anyio
async def test_chat_tool_approval_flow(tmp_path: Path) -> None:
    (tmp_path / "a.txt").write_text("TODO: x", encoding="utf-8")

    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(
        transport=transport, base_url="http://testserver"
    ) as client:
        resp = await client.post(
            "/api/v1/chat/sessions",
            json={
                "model": {"provider": "fake-react", "name": "fake-react"},
                "workflow": "react",
                "require_tool_approval": True,
            },
        )
        assert resp.status_code == 200
        session_id = resp.json()["session_id"]

        resp2 = await client.post(
            f"/api/v1/chat/sessions/{session_id}/messages",
            json={"content": f"WORKSPACE_DIR={tmp_path}"},
        )
        assert resp2.status_code == 200
        payload = resp2.json()
        assert payload["status"] == "tool_approval_required"
        approval_id = payload["tool_call"]["approval_id"]
        assert payload["tool_call"]["tool_name"] == "batch-file-search"

        resp3 = await client.post(
            f"/api/v1/chat/sessions/{session_id}/approvals/{approval_id}",
            json={"decision": "approve", "reason": "ok"},
        )
        assert resp3.status_code == 200
        payload3 = resp3.json()
        assert payload3["status"] == "completed"
        assert payload3["assistant"] == "ok"


@pytest.mark.anyio
async def test_chat_tool_deny_flow_can_list_approvals(tmp_path: Path) -> None:
    (tmp_path / "a.txt").write_text("TODO: x", encoding="utf-8")

    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(
        transport=transport, base_url="http://testserver"
    ) as client:
        resp = await client.post(
            "/api/v1/chat/sessions",
            json={
                "model": {"provider": "fake-react", "name": "fake-react"},
                "workflow": "react",
                "require_tool_approval": True,
            },
        )
        assert resp.status_code == 200
        session_id = resp.json()["session_id"]

        tools_resp = await client.get("/api/v1/chat/tools")
        assert tools_resp.status_code == 200
        tools = tools_resp.json()
        assert any(t["name"] == "batch-file-search" for t in tools)

        resp2 = await client.post(
            f"/api/v1/chat/sessions/{session_id}/messages",
            json={"content": f"WORKSPACE_DIR={tmp_path}"},
        )
        assert resp2.status_code == 200
        payload = resp2.json()
        assert payload["status"] == "tool_approval_required"
        approval_id = payload["tool_call"]["approval_id"]

        approvals_resp = await client.get(
            f"/api/v1/chat/sessions/{session_id}/approvals?status=pending"
        )
        assert approvals_resp.status_code == 200
        approvals = approvals_resp.json()
        assert len(approvals) == 1
        assert approvals[0]["id"] == approval_id

        resp3 = await client.post(
            f"/api/v1/chat/sessions/{session_id}/approvals/{approval_id}",
            json={"decision": "deny", "reason": "no"},
        )
        assert resp3.status_code == 200
        payload3 = resp3.json()
        assert payload3["status"] == "completed"
        assert payload3["assistant"] == "ok"

        approvals2_resp = await client.get(
            f"/api/v1/chat/sessions/{session_id}/approvals?status=denied"
        )
        assert approvals2_resp.status_code == 200
        approvals2 = approvals2_resp.json()
        assert len(approvals2) == 1
        assert approvals2[0]["id"] == approval_id
