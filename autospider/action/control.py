import contextlib
from email import header
import pathlib
import re
import os
import asyncio
import random
import string
import os.path
from urllib.parse import urlparse, ParseResult, urljoin
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
        proxy: str = None,
        headless: bool = False,
        context_id: str = "",
    ) -> None:
        super().__init__(child_actions, context_id)
        self._browser_context: Any = None

        self._proxy = proxy
        self._headless = headless
        self._browser = async_playwright()

    async def run(self, context: Any):
        self._browser_context = await self._browser.start()

        if self._proxy is not None:
            context = await self._browser_context.chromium.launch(
                proxy={
                    "server": self._proxy,
                },
                headless=self._headless,
                slow_mo=100,
            )
        else:
            context = await self._browser_context.chromium.launch(
                headless=self._headless,
                slow_mo=100,
            )

        self.add_context("browser", context)
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
        注册当前的路由
        注册当前的rootpage
        """
        url = urlparse(self._url)
        self.add_context("domain", url.scheme + "://" + url.netloc)

        c = await context.new_page()
        # c.set_default_timeout(10000)  # 设为10秒
        await c.goto(self._url)
        self.add_context("page", c)

        await self.run_child(c)


class ClickAction(BaseAction):
    """
    点击操作
    """

    async def run(self, context: Any):
        await context.click()
        await self.run_child(context)


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

    需要提供添加header的方法
    :authority: img.xsnvshen.com
    :method: GET
    :path: /album/22162/37664/037.jpg
    :scheme: https
    """

    def __init__(
        self,
        child_actions: List["IAction"],
        path: str,
        proxy: str = None,
        https: bool = False,
        header: dict = None,
        wait: int = 1,
        context_id: str = "",
    ) -> None:
        super().__init__(child_actions, context_id)
        self.path = path
        self._proxy = proxy
        self._https = https
        self._header = header
        self._wait = wait

        os.makedirs(path, exist_ok=True)

    async def run(self, ctx: Any):
        """
        1、如果有多个下载 尽量随机避免被发现
        2、handleshake超时时间设置长一点 避免失败
        3、寻找设置proxy而导致连接失败的原因
        """
        if ctx is None:
            return

        parse = urlparse(ctx)
        new_parse = list(parse)
        if self._https:
            new_parse[0] = "https"
        else:
            new_parse[0] = "http"
        if new_parse[1] == "":
            new_parse[1] = self.get_context("domain")
        new_p = ParseResult(*new_parse)

        url = new_p.geturl()

        *_, fileName = ctx.rpartition("/")
        # fileName = "".join(random.sample(string.ascii_letters, 6)) + fileName

        # 构造header
        if isinstance(self._header, dict):
            for key in self._header.keys():
                val = self._header.get(key)
                if isinstance(val, str) and val.startswith("split"):
                    parts = val.split(",")
                    val = url.replace(parts[2], "")
                self._header[key] = val

        # 下载文件
        for i in range(20):  # 重试5次
            try:
                if self._proxy is not None:
                    r = httpx.get(
                        url,
                        headers=self._header,
                        proxies=self._proxy,
                        timeout=10,
                        verify=False,
                    )
                else:
                    r = httpx.get(url, headers=self._header, timeout=10, verify=False)
                r.raise_for_status()
            except httpx.HTTPError as exc:
                print(f"重试 {i+1}次: Error while requesting {exc}.")
                await asyncio.sleep(self._wait)
            else:
                break
        else:
            print("20次依然失败")
            return

        if r.status_code != 200:
            print("下载图片错误")
            return

        with open(os.path.join(self.path, fileName), "wb") as f:
            f.write(r.content)

        await self.run_child(self.path)
        # async with httpx.AsyncClient(proxies=self._proxy, verify=False) as client:
        #     r = await client.get(url)
        #     if r.status_code != 200:
        #         print("下载图片错误")
        #         return

        #     with open(os.path.join(self.path, fileName), "wb") as f:
        #         f.write(r.content)

        # await self.run_child(self.path)
