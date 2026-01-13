import asyncio
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, List, Literal, Optional
from uuid import uuid4

Role = Literal["system", "user", "assistant"]


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


@dataclass(frozen=True)
class ChatMessage:
    id: str
    role: Role
    content: str
    created_at: str


@dataclass
class PendingToolCall:
    approval_id: str
    tool_name: str
    tool_args: Dict[str, Any]
    created_at: str


ApprovalStatus = Literal["pending", "approved", "denied"]


@dataclass
class ToolApproval:
    id: str
    session_id: str
    tool_name: str
    tool_args: Dict[str, Any]
    status: ApprovalStatus
    created_at: str
    resolved_at: Optional[str] = None
    decision_reason: str = ""


@dataclass
class ChatSession:
    id: str
    created_at: str
    model_config: Dict[str, Any]
    workflow: str
    require_tool_approval: bool
    messages: List[ChatMessage] = field(default_factory=list)
    scratchpad: str = ""
    pending_tool_call: Optional[PendingToolCall] = None


class InMemoryChatStore:
    def __init__(self) -> None:
        self._lock = asyncio.Lock()
        self._sessions: Dict[str, ChatSession] = {}
        self._approvals: Dict[str, ToolApproval] = {}

    async def create_session(
        self,
        *,
        model_config: Dict[str, Any],
        workflow: str,
        require_tool_approval: bool,
    ) -> ChatSession:
        async with self._lock:
            session_id = str(uuid4())
            session = ChatSession(
                id=session_id,
                created_at=utc_now_iso(),
                model_config=model_config,
                workflow=workflow,
                require_tool_approval=require_tool_approval,
            )
            self._sessions[session_id] = session
            return session

    async def get_session(self, session_id: str) -> Optional[ChatSession]:
        async with self._lock:
            return self._sessions.get(session_id)

    async def add_message(
        self,
        session_id: str,
        *,
        role: Role,
        content: str,
    ) -> ChatMessage:
        async with self._lock:
            session = self._sessions.get(session_id)
            if session is None:
                raise KeyError(session_id)
            message = ChatMessage(
                id=str(uuid4()),
                role=role,
                content=content,
                created_at=utc_now_iso(),
            )
            session.messages.append(message)
            return message

    async def update_scratchpad(self, session_id: str, scratchpad: str) -> None:
        async with self._lock:
            session = self._sessions.get(session_id)
            if session is None:
                raise KeyError(session_id)
            session.scratchpad = scratchpad

    async def create_approval(
        self,
        *,
        session_id: str,
        tool_name: str,
        tool_args: Dict[str, Any],
    ) -> ToolApproval:
        async with self._lock:
            approval_id = str(uuid4())
            approval = ToolApproval(
                id=approval_id,
                session_id=session_id,
                tool_name=tool_name,
                tool_args=tool_args,
                status="pending",
                created_at=utc_now_iso(),
            )
            self._approvals[approval_id] = approval

            session = self._sessions.get(session_id)
            if session is None:
                raise KeyError(session_id)
            session.pending_tool_call = PendingToolCall(
                approval_id=approval_id,
                tool_name=tool_name,
                tool_args=tool_args,
                created_at=approval.created_at,
            )
            return approval

    async def resolve_approval(
        self,
        approval_id: str,
        *,
        decision: Literal["approve", "deny"],
        reason: str,
    ) -> ToolApproval:
        async with self._lock:
            approval = self._approvals.get(approval_id)
            if approval is None:
                raise KeyError(approval_id)
            if approval.status != "pending":
                return approval

            approval.status = "approved" if decision == "approve" else "denied"
            approval.resolved_at = utc_now_iso()
            approval.decision_reason = reason

            session = self._sessions.get(approval.session_id)
            if session and session.pending_tool_call:
                if session.pending_tool_call.approval_id == approval_id:
                    session.pending_tool_call = None
            return approval

    async def get_approval(self, approval_id: str) -> Optional[ToolApproval]:
        async with self._lock:
            return self._approvals.get(approval_id)

    async def list_approvals(
        self,
        *,
        session_id: str,
        status: Optional[ApprovalStatus] = None,
    ) -> List[ToolApproval]:
        async with self._lock:
            approvals = [
                a for a in self._approvals.values() if a.session_id == session_id
            ]
            if status:
                approvals = [a for a in approvals if a.status == status]
            approvals.sort(key=lambda a: a.created_at, reverse=True)
            return approvals
