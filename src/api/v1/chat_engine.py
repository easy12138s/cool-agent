import json
import re
from dataclasses import dataclass
from typing import Any, Dict, Literal, Optional

from src.agents.llm import model_factory
from src.agents.llm.base import BaseModel
from src.agents.prompt.react import REACT_PROMPT
from src.agents.service.base_agent import BaseAgent
from src.agents.tools.registry import ToolRegistry


@dataclass(frozen=True)
class ParsedDecision:
    kind: Literal["final", "tool", "invalid"]
    final: str = ""
    tool_name: str = ""
    tool_args: Optional[Dict[str, Any]] = None
    error: str = ""


class FakeReActModel(BaseModel):
    def __init__(self, config: Dict[str, Any]):
        self._name = config.get("name", "fake-react")
        self._provider = config.get("provider", "fake-react")

    @property
    def name(self) -> str:
        return self._name

    @property
    def provider(self) -> str:
        return self._provider

    @property
    def function_calling(self) -> bool:
        return False

    async def generate(self, prompt: str, **kwargs) -> str:
        start = prompt.rfind("## 开始")
        scratch_region = prompt[start:] if start != -1 else prompt

        if "Observation:" in scratch_region:
            return "Final Answer: ok"

        workspace_dir = "."
        m = re.search(r"WORKSPACE_DIR\s*=\s*(.+)", prompt)
        if m:
            workspace_dir = m.group(1).strip().splitlines()[0].strip()

        tool_args = {
            "search_path": workspace_dir,
            "keyword": "TODO",
            "is_regex": False,
            "file_filter": ".txt",
            "case_sensitive": False,
        }
        return (
            "Thought: 我需要先检索关键信息。\n"
            "Action: batch-file-search\n"
            f"Action Input: {json.dumps(tool_args, ensure_ascii=False)}\n"
        )


def create_model_from_config(model_config: Dict[str, Any]) -> BaseModel:
    provider = str(model_config.get("provider", "")).lower()
    if provider in {"fake-react", "fake"}:
        return FakeReActModel(model_config)
    return model_factory.create_model(model_config)


def format_react_prompt(
    *,
    user_input: str,
    scratchpad: str,
    tools_desc: str,
    tool_names: str,
) -> str:
    return BaseAgent.format_prompt(
        REACT_PROMPT,
        {
            "tools": tools_desc,
            "tool_names": tool_names,
            "input": user_input,
            "agent_scratchpad": scratchpad,
        },
    )


def parse_react_decision(decision: str) -> ParsedDecision:
    if "Final Answer:" in decision:
        final_answer = decision.split("Final Answer:")[-1].strip()
        return ParsedDecision(kind="final", final=final_answer)

    action_match = re.search(r"Action:\s*([^\n]+)", decision)
    action_input_match = re.search(r"Action Input:\s*(.+)", decision, re.DOTALL)
    if not action_match or not action_input_match:
        return ParsedDecision(
            kind="invalid",
            error="无法从模型输出中解析 Action / Action Input。",
        )

    tool_name = action_match.group(1).strip()
    input_str = action_input_match.group(1).strip()

    input_str = input_str.strip("`")
    if input_str.startswith("json"):
        input_str = input_str[4:]

    try:
        start = input_str.find("{")
        end = input_str.rfind("}")
        if start == -1 or end == -1:
            return ParsedDecision(
                kind="invalid",
                error="Action Input 需要是 JSON 对象。",
            )
        tool_args = json.loads(input_str[start : end + 1])
        if not isinstance(tool_args, dict):
            return ParsedDecision(kind="invalid", error="Action Input 必须是 JSON 对象。")
        return ParsedDecision(kind="tool", tool_name=tool_name, tool_args=tool_args)
    except json.JSONDecodeError as e:
        return ParsedDecision(kind="invalid", error=f"Action Input JSON 解析失败: {e}")


def build_tools_metadata(tools: ToolRegistry) -> tuple[str, str]:
    tool_list = tools.list_tools()
    tools_desc_lines = []
    tool_names = []
    for tool in tool_list:
        tools_desc_lines.append(
            f"{tool.name}: {tool.description}\n"
            f"   Parameters: {json.dumps(tool.parameters, ensure_ascii=False)}"
        )
        tool_names.append(tool.name)
    return "\n".join(tools_desc_lines), ", ".join(tool_names)
