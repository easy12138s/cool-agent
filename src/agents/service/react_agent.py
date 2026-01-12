import json
import logging
import re
from typing import Any, Dict, Optional

from ..llm.base import BaseModel
from ..memory.short_term_memory import ShortTermMemory
from ..prompt.react import REACT_PROMPT
from ..tools.registry import ToolRegistry
from .base_agent import BaseAgent

logger = logging.getLogger(__name__)


class ReActAgent(BaseAgent):
    """
    基于 ReAct Agent 实现
    """

    def __init__(
        self,
        model: BaseModel,
        tools: ToolRegistry,
        memory: Optional[ShortTermMemory] = None,
        max_iterations: int = 10,
    ):
        super().__init__()
        self.model = model
        self.tools = tools
        self.memory = memory or ShortTermMemory()
        self.max_iterations = max_iterations

    @property
    def agent_card(self) -> Dict[str, Any]:
        return {
            "name": "Cool ReAct Agent",
            "description": "基于 ReAct 模式的通用智能助手",
            "skill_list": [
                {"tool": t.name, "tool_description": t.description}
                for t in self.tools.list_tools()
            ],
            "permission": "local",
        }

    @property
    def sys_prompt(self) -> str:
        return REACT_PROMPT

    def _format_tools(self) -> tuple[str, str]:
        """格式化工具描述和名称列表"""
        tool_list = self.tools.list_tools()
        tools_desc = []
        tool_names = []

        for tool in tool_list:
            # 尝试获取 JSON Schema 格式的参数描述
            params = tool.parameters
            # 简化显示，或者直接显示 JSON
            desc = (
                f"{tool.name}: {tool.description}\n"
                f"   Parameters: {json.dumps(params, ensure_ascii=False)}"
            )
            tools_desc.append(desc)
            tool_names.append(tool.name)

        return "\n".join(tools_desc), ", ".join(tool_names)

    async def think(self, input_data: str, scratchpad: str) -> str:
        """
        生成思考
        """
        tools_desc_str, tool_names_str = self._format_tools()

        prompt = self.format_prompt(
            self.sys_prompt,
            {
                "tools": tools_desc_str,
                "tool_names": tool_names_str,
                "input": input_data,
                "agent_scratchpad": scratchpad,
            },
        )

        # 调用模型 - 非流式生成
        response = await self.model.generate(prompt)
        return response

    async def act(self, decision: str) -> tuple[str, str, bool]:
        """
        执行决策
        返回: (Action名称, Observation结果, 是否结束)
        """
        # 检查是否是最终答案
        if "Final Answer:" in decision:
            final_answer = decision.split("Final Answer:")[-1].strip()
            return "Final Answer", final_answer, True

        # 解析 Action 和 Action Input
        # 匹配 Action: tool_name
        action_match = re.search(r"Action:\s*([^\n]+)", decision)
        # 匹配 Action Input: {json} 或 string

        action_input_match = re.search(r"Action Input:\s*(.+)", decision, re.DOTALL)

        if action_match and action_input_match:
            tool_name = action_match.group(1).strip()
            input_str = action_input_match.group(1).strip()

            # 清理可能的 Markdown 代码块标记
            input_str = input_str.strip("`")
            if input_str.startswith("json"):
                input_str = input_str[4:]

            # 尝试解析 JSON 参数
            try:
                # 尝试找到第一个 { 和 最后一个 }
                start = input_str.find("{")
                end = input_str.rfind("}")
                if start != -1 and end != -1:
                    json_str = input_str[start : end + 1]
                    tool_args = json.loads(json_str)
                else:
                    return (
                        tool_name,
                        (
                            "Error: Action Input must be a valid JSON string. "
                            f"Got: {input_str}"
                        ),
                        False,
                    )
            except json.JSONDecodeError as e:
                return tool_name, f"Error: Invalid JSON in Action Input: {e}", False

            # 3. 执行工具
            tool = self.tools.get_tool(tool_name)
            if not tool:
                return tool_name, f"Error: Tool '{tool_name}' not found.", False

            try:
                logger.info(f"Executing tool: {tool_name} with args: {tool_args}")
                observation = await tool.run(**tool_args)
                return tool_name, str(observation), False
            except Exception as e:
                return tool_name, f"Error executing tool: {e}", False

        # 如果没有匹配到 Action，可能模型还在思考或者格式错误
        return (
            "Unknown",
            "Error: Could not parse Action and Action Input from response.",
            False,
        )

    async def run(self, user_input: str) -> str:
        """
        运行 Agent 循环
        """
        self.reset()
        self.status = self.STATUS_WORKING

        # 记录用户输入
        self.memory.add("user", user_input)

        scratchpad = ""
        final_response = ""

        for i in range(self.max_iterations):
            logger.info(f"Iteration {i + 1}/{self.max_iterations}")

            # 1. Think
            response = await self.think(user_input, scratchpad)
            logger.info(f"LLM Response: {response}")

            # 记录到 scratchpad (Thought)
            # 简单的处理：直接追加 LLM 的回复
            scratchpad += response + "\n"

            # 2. Act
            action_type, result, is_done = await self.act(response)

            if is_done:
                final_response = result
                scratchpad += f"Final Answer: {result}\n"
                break

            # 3. Observation
            observation = f"Observation: {result}"
            logger.info(observation)

            # 记录到 scratchpad
            scratchpad += observation + "\n"

        if not final_response:
            final_response = (
                "I'm sorry, I couldn't complete the task within the maximum number of "
                "steps."
            )

        self.memory.add("assistant", final_response)
        self.status = self.STATUS_COMPLETED
        return final_response
