# 页面中元素定位相关
from typing import Any
import re

from autospider.action.base import BaseAction


class TextAction(BaseAction):
    r = re.compile(r"[^\t]+")
    b = re.compile(r"\s+")

    async def run(self, context: Any):
        res = await context.inner_text()
        # 按照\t分组
        res = " | ".join(
            re.sub(self.b, " ", i) for i in self.r.findall(res)
        )
        await self.run_child(res)
