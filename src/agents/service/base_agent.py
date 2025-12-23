from abc import ABC, abstractmethod
from typing import Dict, Any, Union, Optional
import string


class BaseAgent(ABC):
    """
    Agent抽象基类
    """

    STATUS_IDLE = "idle"  # 空闲
    STATUS_WORKING = "working"  # 执行中
    STATUS_ERROR = "error"  # 异常
    STATUS_COMPLETED = "completed"  # 完成

    def __init__(self):
        self.status = self.STATUS_IDLE
        self.error_info: Optional[str] = None

    @abstractmethod
    @property
    def agent_card(self) -> Dict[str, Any]:
        """
        agent名片
        需要包含当前agent的名字、描述、能力

        示例：
        {
            "name": "文件命名助手",
            "description": "一名文件命名助手，可以帮助命名各种文件",
            "skill_list": [{
                "tool": "rename_file",
                "tool_description": "重命名文件"
            }],
            "permission": "local"
        }
        """
        raise NotImplementedError("子类必须编写agent的名片信息")

    @abstractmethod
    @property
    def sys_prompt(self) -> str:
        """
        agent系统提示词
        """
        raise NotImplementedError("子类必须编写agent的系统提示词")

    @abstractmethod
    async def think(self, input_data: Any) -> Union[Dict[str, Any], str, None]:
        """
        核心抽象方法：思考/决策逻辑
        """
        raise NotImplementedError("子类必须实现think方法，定义Agent的决策逻辑")

    @abstractmethod
    async def act(self, decision: Any) -> Union[Dict[str, Any], str, None]:
        """
        核心抽象方法：执行/行动逻辑
        """
        raise NotImplementedError("子类必须实现act方法，定义Agent的执行逻辑")

    def get_status(self) -> Dict[str, Any]:
        """
        通用方法：获取Agent当前状态
        """
        return {
            "status": self.status,
            "error_info": self.error_info,
        }

    def reset(self) -> None:
        """
        通用方法：重置Agent状态（恢复到初始空闲状态）
        """
        self.status = self.STATUS_IDLE
        self.error_info = None

    def feedback(self, feedback_data: Any) -> None:
        """
        通用方法：接收外部反馈
        """
        pass

    def run(self, input_data: Any) -> Union[Dict[str, Any], str, None]:
        """
        通用方法：封装Agent的完整执行流程（思考→执行）
        """
        try:
            self.status = self.STATUS_WORKING
            # 1. 思考决策
            decision = self.think(input_data)
            # 2. 执行行动
            result = self.act(decision)
            self.status = self.STATUS_COMPLETED
            return result
        except Exception as e:
            self.status = self.STATUS_ERROR
            self.error_info = str(e)

    @staticmethod
    def format_prompt(
        prompt_template: str, placeholder_dict: Dict[str, Any], default: Any = ""
    ) -> str:
        """
        通用方法：动态拼接提示词，替换模板中的占位符
        """
        try:
            template = string.Template(prompt_template)
            full_placeholders = {
                placeholder: placeholder_dict.get(placeholder, default)
                for placeholder in template.pattern.findall(prompt_template)
            }
            return template.safe_substitute(full_placeholders)
        except Exception as e:
            raise RuntimeError(f"提示词拼接失败：{e}") from e
