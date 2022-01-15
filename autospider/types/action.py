import contextlib
from typing import Any, Protocol, List
from dataclasses import dataclass, field


class IAction(Protocol):
    """
    action的接口类
    """

    context_id: str
    child_actions: List["IAction"]

    def __init__(self, *args, **kwargs) -> None:
        super().__init__()

    def add_context(self, context_id: str, context: Any):
        raise NotImplementedError

    def get_context(self, context_id: str):
        raise NotImplementedError

    async def run(self, context: Any):
        """
        执行action命令 需要传入依赖的context
        """
        raise NotImplementedError

    async def stop(self):
        raise NotImplementedError
