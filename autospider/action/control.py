import contextlib
import pathlib
import re
import os
import random
import string
import os.path
from urllib.parse import urlparse
from typing import Any, Tuple, List

from playwright.async_api import async_playwright
import httpx

from autospider.action.base import BaseAction
from autospider.types.action import IAction


class OpenAction(BaseAction):
    """
    打开浏览器
    """

    def __init__(
        self,
        child_actions: List["IAction"],
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
        self, child_actions: List["IAction"], url: str, context_id: str = ""
    ) -> None:
        super().__init__(child_actions, context_id)
        self._url = url

    async def run(self, context: Any):
        """
        需要注册当前的路由
        """
        url = urlparse(self._url)
        self.add_context("domain", url.scheme + "://" + url.netloc)

        c = await context.new_page()
        await c.goto(self._url)

        await self.run_child(c)


class ClickAction(BaseAction):
    """
    点击操作
    """

    def __init__(
        self, child_actions: List["IAction"], element: str, context_id: str = ""
    ) -> None:
        super().__init__(child_actions, context_id)
        self._element = element

    async def run(self, context: Any):
        c = await context.click()
        await self.run_child(c)


class LocatorAction(BaseAction):
    def __init__(
        self, child_actions: List["IAction"], element: str, context_id: str = ""
    ) -> None:
        super().__init__(child_actions, context_id)
        self._element = element

    async def run(self, context: Any):
        c = context.locator(self._element)
        await self.run_child(c)


class AttrAction(BaseAction):
    """
    获取属性值
    """

    def __init__(
        self, child_actions: List["IAction"], name: str, context_id: str = ""
    ) -> None:
        super().__init__(child_actions, context_id)
        self._name = name

    async def run(self, context: Any):
        if context is None:
            print("context为空")
            return

        c = await context.get_attribute(self._name)
        await self.run_child(c)


class BackgroundUrlAction(BaseAction):
    """
    获取style中的backgroundurl值
    """
    P_BACKURL = r"background-image:\s?url\((.*)\).*?"

    async def run(self, context: Any):
        if context is None:
            print("context为空")
            return

        c = await context.get_attribute("style")

        if res := re.search(self.P_BACKURL, c):
            url = res.group(1)[1:-1]
            await self.run_child(url)

class DownloadAction(BaseAction):
    """
    下载内容

    """

    def __init__(self, child_actions: List["IAction"], path: str, context_id: str = "") -> None:
        super().__init__(child_actions, context_id)
        self.path = path
        os.makedirs(path, exist_ok=True)

    async def run(self, ctx: Any):
        if ctx is None:
            return

        if ctx.startswith("/"):
            url = self.get_context("domain") + ctx
        else:
            url = self.get_context("domain") + "/" + ctx
        
        *_, fileName = ctx.rpartition("/")
        fileName = "".join(random.sample(string.ascii_letters, 6)) + fileName

        # 下载文件
        async with httpx.AsyncClient() as client:
            r = await client.get(url)
            if r.status_code != 200:
                print("下载图片错误")
                return

            with open(os.path.join(self.path, fileName), 'wb') as f:
                f.write(r.content)

        await self.run_child(self.path)
