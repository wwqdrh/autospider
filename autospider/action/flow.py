from typing import Any, Tuple, Sequence, List

from autospider.types.action import IAction
from autospider.action.base import BaseAction


class IfAction(BaseAction):
    pass


class ForElementAction(BaseAction):
    def __init__(
        self,
        child_actions: List["IAction"],
        element: str,
        context_id: str = "",
    ) -> None:
        super().__init__(child_actions, context_id)
        self._element = element

    async def run(self, context: Any):
        c = context.locator(self._element)
        count = await c.count()
        for i in range(count):
            cur = c.nth(i)
            # print(await cur.inner_html())
            # print(await cur.locator("div >> nth = 0").get_attribute("style"))
            await self.run_child(cur)

    async def stop(self):
        pass
