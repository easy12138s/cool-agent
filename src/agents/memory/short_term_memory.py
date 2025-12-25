"""
短期记忆模块
"""
from typing import List, Dict, Any

class ShortTermMemory:
    """
    短期记忆模块 - 管理当前会话的上下文
    """
    def __init__(self):
        self.messages: List[Dict[str, Any]] = []

    def add(self, role: str, content: str, **kwargs):
        """
        添加一条消息
        :param role: 角色 (system, user, assistant, function/tool)
        :param content: 内容
        """
        message = {
            "role": role,
            "content": content,
            **kwargs
        }
        self.messages.append(message)

    def get_context(self) -> List[Dict[str, Any]]:
        """获取完整上下文"""
        return self.messages

    def clear(self):
        """清空记忆"""
        self.messages = []

    def get_recent(self, k: int = 5) -> List[Dict[str, Any]]:
        """获取最近 k 条消息"""
        return self.messages[-k:]

