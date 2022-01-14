from typing import List, Mapping, Any, MutableMapping, Optional
from weakref import WeakValueDictionary

import yaml
from spider.action.base import get_action

from spider.types.action import IAction


class ActionTree:
    """
    管理整个action的树形结构 调用逻辑 结构化 初始化 运行
    """

    def __init__(self, nodes: List[IAction]) -> None:
        self._nodes = nodes
        self._context_mapping: MutableMapping[str, Any] = dict()  # 存储上下文的映射

    @classmethod
    def factory_nodes(cls, nodes: List[IAction]) -> "ActionTree":
        """
        构造函数 将context

        递归将每个action转为actionnode
        """
        return cls(nodes)

    @classmethod
    def factory_ymlstr(cls, ymlstr: str) -> "ActionTree":
        data = yaml.safe_load(ymlstr)

        def dfs(conf: List[dict]) -> List["IAction"]:
            res = []
            for item in conf:
                args = dict()
                children = []
                action_type: Optional["IAction"] = None
                for key, value in item.items():
                    if key == "type":
                        action_type = get_action(value)
                    elif key == "next":
                        children = dfs(value)
                    else:
                        args[key] = value
                if action_type is not None:
                    res.append(action_type(child_actions=children, **args))
            return res

        
        return cls(dfs(data))

    def add_context_mapping(self, key: str, value: Any):
        self._context_mapping[key] = value

    async def start(self):
        """
        启动action
        """
        for action in self._nodes:
            await action.run(None)
            await action.stop()
