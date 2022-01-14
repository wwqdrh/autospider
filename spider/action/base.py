from typing import List, Optional, Protocol, Sequence, Any, MutableMapping, Type

from spider.types.action import IAction


_action_mapping: MutableMapping[str, Type["BaseAction"]] = dict()


def register(t: Type["IAction"]):
    _action_mapping[str.removesuffix(t.__name__.lower(), "action")] = t


def get_action(name: str) -> Optional[Type["IAction"]]:
    return _action_mapping.get(name, None)


class BaseAction:
    """
    action的基类 提供公共方法
    """

    def __init__(self, child_action: Sequence["IAction"], context_id: str) -> None:
        self.context_id = context_id
        self.child_action = child_action

    def __init_subclass__(subcls) -> None:
        register(subcls)

    async def run_child(self, context: Any):
        for child in self.child_action:
            await child.run(context)
            await child.stop()

    def get_context(self):
        """
        在树形结构下 如何拿到某个指定层级的上下文对象

        1、手动进行注册 初始化action的时候手动传递contextid
        2、BaseAction需要维护一个node字段 获取配置 从中根据needid获取对应的上下文对象
        """
        pass

    async def run(self, context: Any):
        pass

    async def stop(self):
        pass
