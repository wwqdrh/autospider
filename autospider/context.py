from typing import Dict, List, Optional, Protocol, Sequence, Any, MutableMapping, Type
import io
import atexit

from autospider.types.action import IAction


_out = ""
_out_buf = io.StringIO()
_action_mapping: Dict[str, Type["IAction"]] = dict()
_context_mapping: Dict[str, Any] = dict()


def set_action(t: Type["IAction"]):
    _action_mapping[str.removesuffix(t.__name__.lower(), "action")] = t


def get_action(name: str) -> Optional[Type["IAction"]]:
    return _action_mapping.get(name, None)


def set_context(context_id: str, context: Any):
    _context_mapping[context_id] = context


def get_context(context_id: str):
    return _context_mapping[context_id]


def set_out(out: str):
    global _out
    _out = out


def get_out_str() -> str:
    return _out


def get_out(word):
    if _out == "":
        print(word)

    _out_buf.write(word)


@atexit.register
def exit():
    # print("执行退出")
    if _out != "":
        print("输出到文件中")
        with open(_out, mode="w+", encoding="utf8") as f:
            f.write(_out_buf.getvalue())
        _out_buf.close()

    # print("OpenAction退出中...")


class BaseAction:
    """
    action的基类 提供公共方法
    """

    def __init__(self, child_actions: List["IAction"], context_id: str = "") -> None:
        self.context_id = context_id
        self.child_actions = child_actions

    def __init_subclass__(subcls) -> None:
        set_action(subcls)

    async def run_child(self, context: Any):
        for child in self.child_actions:
            await child.run(context)
            await child.stop()

    def add_context(self, context_id: str, context: Any):
        """
        page: 全局的locator对象
        """
        set_context(context_id, context)

    def get_context(self, context_id: str):
        """
        在树形结构下 如何拿到某个指定层级的上下文对象
        """
        return get_context(context_id)

    async def run(self, context: Any):
        pass

    async def stop(self):
        pass

        # 打印输出

    def set_out(self, out: str):
        set_out(out)

    def get_out(self) -> str:
        return get_out_str()

    async def out(self, word: str):
        get_out(word + "\n")
