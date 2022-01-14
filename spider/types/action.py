import contextlib
from typing import Any, Protocol, List
from dataclasses import dataclass, field


class IAction(Protocol):
    """
    action的接口类
    """

    context_id: str
    child_action: List["IAction"]

    async def run(self, children_actions: List["IAction"]):
        """
        执行action命令 需要传入依赖的context
        """
        raise NotImplementedError

    async def stop(self):
        raise NotImplementedError
