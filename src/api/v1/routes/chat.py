from functools import lru_cache
from typing import Any, Dict, List, Literal, Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from src.agents.tools.registry import ToolRegistry
from src.api.v1.chat_engine import (
    build_tools_metadata,
    create_model_from_config,
    format_react_prompt,
    parse_react_decision,
)
from src.api.v1.chat_store import InMemoryChatStore


chat_router = APIRouter(prefix="/chat", tags=["chat"])


class ChatModelConfig(BaseModel):
    provider: str = Field(..., description="模型适配器类型，如 openai-compatible / deepseek")
    name: str = Field("", description="模型注册名或自定义名称")
    api_key: str = Field("", description="可选：运行时传入，不在服务端持久化")
    base_url: str = Field("", description="可选：OpenAI Compatible base_url")
    model: str = Field("", description="可选：具体模型名，如 gpt-4o-mini")
    max_tokens: int = 0
    temperature: float = 0.0

    def as_dict(self) -> Dict[str, Any]:
        raw = self.model_dump()
        return {k: v for k, v in raw.items() if v not in ("", 0, 0.0, None)}


class CreateSessionRequest(BaseModel):
    model: ChatModelConfig
    workflow: Literal["react"] = "react"
    require_tool_approval: bool = True


class CreateSessionResponse(BaseModel):
    session_id: str
    created_at: str


class SendMessageRequest(BaseModel):
    content: str
    require_tool_approval: Optional[bool] = None


class ToolCallRequest(BaseModel):
    approval_id: str
    tool_name: str
    tool_description: str
    tool_parameters: Dict[str, Any]
    tool_args: Dict[str, Any]


class SendMessageResponse(BaseModel):
    session_id: str
    status: Literal["completed", "tool_approval_required", "invalid_decision"]
    assistant: str = ""
    tool_call: Optional[ToolCallRequest] = None
    error: str = ""


class ResolveApprovalRequest(BaseModel):
    decision: Literal["approve", "deny"]
    reason: str = ""


class ResolveApprovalResponse(BaseModel):
    session_id: str
    status: Literal["completed", "tool_approval_required", "invalid_decision"]
    assistant: str = ""
    tool_call: Optional[ToolCallRequest] = None
    error: str = ""

class ToolInfo(BaseModel):
    name: str
    description: str
    parameters: Dict[str, Any]


class ApprovalInfo(BaseModel):
    id: str
    session_id: str
    tool_name: str
    tool_args: Dict[str, Any]
    status: Literal["pending", "approved", "denied"]
    created_at: str
    resolved_at: Optional[str] = None
    decision_reason: str = ""


@lru_cache
def get_store() -> InMemoryChatStore:
    return InMemoryChatStore()


@lru_cache
def get_tools() -> ToolRegistry:
    registry = ToolRegistry()
    registry.scan_skills()
    return registry


@chat_router.get("/tools", response_model=List[ToolInfo])
async def list_tools() -> List[ToolInfo]:
    tools = get_tools()
    return [
        ToolInfo(name=t.name, description=t.description, parameters=t.parameters)
        for t in tools.list_tools()
    ]


@chat_router.post("/sessions", response_model=CreateSessionResponse)
async def create_session(payload: CreateSessionRequest) -> CreateSessionResponse:
    store = get_store()
    session = await store.create_session(
        model_config=payload.model.as_dict(),
        workflow=payload.workflow,
        require_tool_approval=payload.require_tool_approval,
    )
    return CreateSessionResponse(session_id=session.id, created_at=session.created_at)


@chat_router.get("/sessions/{session_id}")
async def get_session(session_id: str) -> Dict[str, Any]:
    store = get_store()
    session = await store.get_session(session_id)
    if session is None:
        raise HTTPException(status_code=404, detail="session not found")
    return {
        "session_id": session.id,
        "created_at": session.created_at,
        "workflow": session.workflow,
        "require_tool_approval": session.require_tool_approval,
        "messages": [m.__dict__ for m in session.messages],
        "pending_tool_call": (
            session.pending_tool_call.__dict__ if session.pending_tool_call else None
        ),
    }


@chat_router.get("/sessions/{session_id}/approvals", response_model=List[ApprovalInfo])
async def list_approvals(
    session_id: str,
    status: Optional[Literal["pending", "approved", "denied"]] = None,
) -> List[ApprovalInfo]:
    store = get_store()
    session = await store.get_session(session_id)
    if session is None:
        raise HTTPException(status_code=404, detail="session not found")
    approvals = await store.list_approvals(session_id=session_id, status=status)
    return [
        ApprovalInfo(
            id=a.id,
            session_id=a.session_id,
            tool_name=a.tool_name,
            tool_args=a.tool_args,
            status=a.status,
            created_at=a.created_at,
            resolved_at=a.resolved_at,
            decision_reason=a.decision_reason,
        )
        for a in approvals
    ]


@chat_router.post("/sessions/{session_id}/messages", response_model=SendMessageResponse)
async def send_message(
    session_id: str, payload: SendMessageRequest
) -> SendMessageResponse:
    store = get_store()
    session = await store.get_session(session_id)
    if session is None:
        raise HTTPException(status_code=404, detail="session not found")
    if session.pending_tool_call is not None:
        raise HTTPException(status_code=409, detail="session has pending tool approval")

    require_tool_approval = (
        payload.require_tool_approval
        if payload.require_tool_approval is not None
        else session.require_tool_approval
    )

    await store.add_message(session_id, role="user", content=payload.content)

    if session.workflow != "react":
        raise HTTPException(status_code=400, detail="unsupported workflow")

    tools = get_tools()
    tools_desc, tool_names = build_tools_metadata(tools)

    try:
        model = create_model_from_config(session.model_config)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"model init failed: {e}") from e

    scratchpad = session.scratchpad
    max_iterations = 10
    last_error = ""

    for _ in range(max_iterations):
        prompt = format_react_prompt(
            user_input=payload.content,
            scratchpad=scratchpad,
            tools_desc=tools_desc,
            tool_names=tool_names,
        )
        decision = await model.generate(prompt)
        scratchpad = f"{scratchpad}{decision}\n"

        parsed = parse_react_decision(decision)
        if parsed.kind == "final":
            await store.update_scratchpad(session_id, scratchpad)
            await store.add_message(session_id, role="assistant", content=parsed.final)
            return SendMessageResponse(
                session_id=session_id,
                status="completed",
                assistant=parsed.final,
            )

        if parsed.kind == "invalid" or not parsed.tool_args:
            last_error = parsed.error
            break

        tool = tools.get_tool(parsed.tool_name)
        if tool is None:
            last_error = f"tool not found: {parsed.tool_name}"
            break

        if require_tool_approval:
            approval = await store.create_approval(
                session_id=session_id,
                tool_name=parsed.tool_name,
                tool_args=parsed.tool_args,
            )
            await store.update_scratchpad(session_id, scratchpad)
            return SendMessageResponse(
                session_id=session_id,
                status="tool_approval_required",
                tool_call=ToolCallRequest(
                    approval_id=approval.id,
                    tool_name=tool.name,
                    tool_description=tool.description,
                    tool_parameters=tool.parameters,
                    tool_args=parsed.tool_args,
                ),
            )

        tool_result = await tool.run(**parsed.tool_args)
        scratchpad = f"{scratchpad}Observation: {tool_result}\n"

    await store.update_scratchpad(session_id, scratchpad)
    return SendMessageResponse(
        session_id=session_id,
        status="invalid_decision",
        error=last_error or "agent exceeded max iterations",
    )


@chat_router.post(
    "/sessions/{session_id}/approvals/{approval_id}",
    response_model=ResolveApprovalResponse,
)
async def resolve_approval(
    session_id: str,
    approval_id: str,
    payload: ResolveApprovalRequest,
) -> ResolveApprovalResponse:
    store = get_store()
    session = await store.get_session(session_id)
    if session is None:
        raise HTTPException(status_code=404, detail="session not found")

    approval = await store.get_approval(approval_id)
    if approval is None or approval.session_id != session_id:
        raise HTTPException(status_code=404, detail="approval not found")

    if approval.status != "pending":
        raise HTTPException(status_code=409, detail="approval already resolved")

    await store.resolve_approval(
        approval_id,
        decision=payload.decision,
        reason=payload.reason,
    )

    if session.workflow != "react":
        raise HTTPException(status_code=400, detail="unsupported workflow")

    tools = get_tools()
    tools_desc, tool_names = build_tools_metadata(tools)

    try:
        model = create_model_from_config(session.model_config)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"model init failed: {e}") from e

    scratchpad = session.scratchpad
    tool = tools.get_tool(approval.tool_name)
    if tool is None:
        return ResolveApprovalResponse(
            session_id=session_id,
            status="invalid_decision",
            error=f"tool not found: {approval.tool_name}",
        )

    if payload.decision == "approve":
        tool_result = await tool.run(**approval.tool_args)
        scratchpad = f"{scratchpad}Observation: {tool_result}\n"
    else:
        scratchpad = f"{scratchpad}Observation: User denied tool call.\n"

    max_iterations = 10
    last_error = ""

    for _ in range(max_iterations):
        prompt = format_react_prompt(
            user_input=session.messages[-1].content if session.messages else "",
            scratchpad=scratchpad,
            tools_desc=tools_desc,
            tool_names=tool_names,
        )
        decision = await model.generate(prompt)
        scratchpad = f"{scratchpad}{decision}\n"

        parsed = parse_react_decision(decision)
        if parsed.kind == "final":
            await store.update_scratchpad(session_id, scratchpad)
            await store.add_message(session_id, role="assistant", content=parsed.final)
            return ResolveApprovalResponse(
                session_id=session_id,
                status="completed",
                assistant=parsed.final,
            )

        if parsed.kind == "invalid" or not parsed.tool_args:
            last_error = parsed.error
            break

        tool2 = tools.get_tool(parsed.tool_name)
        if tool2 is None:
            last_error = f"tool not found: {parsed.tool_name}"
            break

        if session.require_tool_approval:
            approval2 = await store.create_approval(
                session_id=session_id,
                tool_name=parsed.tool_name,
                tool_args=parsed.tool_args,
            )
            await store.update_scratchpad(session_id, scratchpad)
            return ResolveApprovalResponse(
                session_id=session_id,
                status="tool_approval_required",
                tool_call=ToolCallRequest(
                    approval_id=approval2.id,
                    tool_name=tool2.name,
                    tool_description=tool2.description,
                    tool_parameters=tool2.parameters,
                    tool_args=parsed.tool_args,
                ),
            )

        tool_result2 = await tool2.run(**parsed.tool_args)
        scratchpad = f"{scratchpad}Observation: {tool_result2}\n"

    await store.update_scratchpad(session_id, scratchpad)
    return ResolveApprovalResponse(
        session_id=session_id,
        status="invalid_decision",
        error=last_error or "agent exceeded max iterations",
    )

