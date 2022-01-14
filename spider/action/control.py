import contextlib
from typing import Any, Tuple, List
from playwright.async_api import async_playwright

from spider.action.base import BaseAction
from spider.types.action import IAction


class OpenAction(BaseAction):
    """
    打开浏览器
    """

    def __init__(
        self,
        child_actions: List["BaseAction"],
        headless: bool,
        context_id: str = "",
    ) -> None:
        super().__init__(child_actions, context_id)
        self._browser_context: Any = None

        self._headless = headless
        self._browser = async_playwright()

    async def run(self, context: Any):
        self._browser_context = await self._browser.start()

        context = await self._browser_context.chromium.launch(
            headless=self._headless, slow_mo=100
        )
        await self.run_child(context)

    async def stop(self):
        print("OpenAction退出中...")
        await self._browser.__aexit__()


class GotoAction(BaseAction):
    """
    跳转页面
    """

    def __init__(
        self, child_actions: List["BaseAction"], url: str, context_id: str = ""
    ) -> None:
        super().__init__(child_actions, context_id)
        self._url = url

    async def run(self, context: Any):
        c = await context.new_page()
        await c.goto(self._url)

        await self.run_child(c)


class ClickAction(BaseAction):
    """
    点击操作
    """

    def __init__(
        self, child_actions: List["BaseAction"], element: str, context_id: str = ""
    ) -> None:
        super().__init__(child_actions, context_id)
        self._element = element

    async def run(self, context: Any):
        c = await context.click()
        await self.run_child(c)
