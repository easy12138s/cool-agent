import json
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

from ..llm.base import BaseModel
from ..prompt.plan_and_execute_skills import PLANNER_SKILLS_PROMPT
from ..tools.registry import ToolRegistry
from .base_workflow import BaseWorkflow


@dataclass(frozen=True)
class PlanStep:
    tool: str
    args: Dict[str, Any]
    name: Optional[str] = None


class PlanAndExecuteWorkflow(BaseWorkflow):
    def __init__(self, model: BaseModel, tools: ToolRegistry):
        self.model = model
        self.tools = tools

    async def run(self, **kwargs: Any) -> Dict[str, Any]:
        user_input = kwargs.get("user_input")
        if not isinstance(user_input, str) or not user_input.strip():
            raise ValueError("user_input 不能为空")

        max_steps = kwargs.get("max_steps", 10)
        if not isinstance(max_steps, int) or max_steps <= 0:
            raise ValueError("max_steps 必须为正整数")

        skills_metadata = self._build_skills_metadata()
        plan_prompt = self._format_prompt(
            PLANNER_SKILLS_PROMPT,
            {"skills_metadata": skills_metadata, "input": user_input},
        )
        plan_prompt = self._wrap_json_plan_instructions(plan_prompt)

        raw_plan = await self.model.generate_with_retry(plan_prompt)
        steps = self._parse_plan_steps(raw_plan)

        executed_steps: List[Dict[str, Any]] = []
        for idx, step in enumerate(steps[:max_steps], start=1):
            tool = self.tools.get_tool(step.tool)
            if tool is None:
                executed_steps.append(
                    {
                        "index": idx,
                        "tool": step.tool,
                        "name": step.name,
                        "args": step.args,
                        "ok": False,
                        "result": {"error": f"Tool '{step.tool}' not found."},
                    }
                )
                break

            result = await tool.run(**step.args)
            ok = self._is_ok_result(result)
            executed_steps.append(
                {
                    "index": idx,
                    "tool": step.tool,
                    "name": step.name,
                    "args": step.args,
                    "ok": ok,
                    "result": result,
                }
            )
            if not ok:
                break

        return {"user_input": user_input, "steps": executed_steps}

    def _build_skills_metadata(self) -> str:
        skills = []
        for tool in self.tools.list_tools():
            skills.append(
                {
                    "name": tool.name,
                    "description": tool.description,
                    "parameters": tool.parameters,
                }
            )
        return json.dumps(skills, ensure_ascii=False)

    @staticmethod
    def _format_prompt(prompt_template: str, placeholder_dict: Dict[str, Any]) -> str:
        class _SafeDict(dict):
            def __missing__(self, key: str) -> str:
                return ""

        return prompt_template.format_map(_SafeDict(placeholder_dict))

    @staticmethod
    def _wrap_json_plan_instructions(base_prompt: str) -> str:
        return (
            f"{base_prompt}\n\n"
            "请只输出 JSON，不要输出任何额外文本。JSON 格式如下：\n"
            "{\n"
            '  "steps": [\n'
            "    {\n"
            '      "name": "步骤名称",\n'
            '      "tool": "skill-name",\n'
            '      "args": {"key": "value"}\n'
            "    }\n"
            "  ]\n"
            "}\n"
        )

    @staticmethod
    def _extract_json(text: str) -> str:
        start = text.find("{")
        end = text.rfind("}")
        if start == -1 or end == -1 or end <= start:
            raise ValueError("无法从模型输出中提取 JSON")
        return text[start : end + 1]

    @classmethod
    def _parse_plan_steps(cls, raw_plan: str) -> List[PlanStep]:
        plan_json = cls._extract_json(raw_plan)
        try:
            obj = json.loads(plan_json)
        except json.JSONDecodeError as e:
            raise ValueError(f"计划 JSON 解析失败: {e}") from e

        steps = obj.get("steps")
        if not isinstance(steps, list) or not steps:
            raise ValueError("计划 JSON 中 steps 不能为空")

        parsed_steps: List[PlanStep] = []
        for step in steps:
            if not isinstance(step, dict):
                raise ValueError("steps 中的每个元素必须是对象")
            tool = step.get("tool")
            args = step.get("args", {})
            name = step.get("name")
            if not isinstance(tool, str) or not tool.strip():
                raise ValueError("steps.tool 必须是非空字符串")
            if not isinstance(args, dict):
                raise ValueError("steps.args 必须是对象")
            if name is not None and not isinstance(name, str):
                raise ValueError("steps.name 必须是字符串")
            parsed_steps.append(PlanStep(tool=tool, args=args, name=name))

        return parsed_steps

    @staticmethod
    def _is_ok_result(result: Any) -> bool:
        if not isinstance(result, dict):
            return True
        if result.get("error"):
            return False
        error_msg = result.get("error_msg")
        if isinstance(error_msg, str) and error_msg.strip():
            return False
        return True
