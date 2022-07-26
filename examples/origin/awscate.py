import asyncio
from typing import AsyncGenerator, Optional
from contextlib import asynccontextmanager
from dataclasses import dataclass

from playwright.async_api import async_playwright, Page

AMAZONHOME = "https://www.amazon.com/"

ErrDomNotFound = Exception("cant location this dom")


async def jshandle(page: Page, js: str):
    """
    处理js代码
    """
    data = await page.evaluate(js)
    return data


@dataclass
class AwsMenu:
    title: str
    level: int
    href: str
    children: list["AwsMenu"]

    @classmethod
    def fromDict(cls, data: list[dict]) -> list["AwsMenu"]:
        if not isinstance(data, list) or len(data) == 0:
            return []
        if not isinstance(data[0], dict):
            return []

        res: list["AwsMenu"] = []
        for item in data:
            res.append(
                cls(
                    item.get("title", ""),
                    item.get("level", -1),
                    item.get("href", ""),
                    cls.fromDict(item.get("children", [])),
                )
            )
        return res


class AmazonParser:
    @asynccontextmanager
    async def context(self) -> AsyncGenerator[Page, None]:
        async with async_playwright() as playwright:
            browser = await playwright.chromium.launch(headless=False, slow_mo=100)
            page = await browser.new_page()

            await page.goto(AMAZONHOME)

            yield page

    async def openCate(self, page: Page):
        """
        进入首页后，点击all菜单栏 展开

        已知验证:
        1、必须到某一个dom上触发hover
        """
        hoverVerify = await page.query_selector(
            "#gw-desktop-herotator > div > div > div > div.a-carousel-col.a-carousel-left.celwidget > a"
        )
        if hoverVerify is None:
            raise ErrDomNotFound

        await hoverVerify.hover()

        await jshandle(
            page,
            """
        document.querySelector("#nav-hamburger-menu").click();
        """,
        )
        await asyncio.sleep(1)

        await self.getCate(page)

    async def closeCate(self, page: Page):
        """
        关闭展开的菜单栏
        """
        await jshandle(
            page, "document.querySelector('#hmenu-canvas-background > div').click()"
        )
        await asyncio.sleep(1)

    async def getCate(self, page: Page) -> list[AwsMenu]:
        """
        在菜单栏中解析出类目的一级菜单和二级菜单
        1、点击see all将隐藏项也展开
        2、获取菜单栏中的一级菜单
        3、点击菜单选项获取二级菜单

        已知验证:
        1、需要先展开菜单栏
        """

        subjs = """
        () => {
            let menudata = [];

            let submenus = document.querySelectorAll('#hmenu-content > ul.hmenu.hmenu-visible > li:nth-child(n+3) > a');
            for (let subi of submenus) {
                menudata.push(
                    {
                        "title": subi.textContent,
                        "level": 1,
                        "href": subi.href,
                        "children": []
                    }
                )
            }
            return menudata;
        }
        """

        # see all 展开
        allDoms = await page.query_selector_all(
            "#hmenu-content > ul.hmenu.hmenu-visible > li a.hmenu-item.hmenu-compressed-btn"
        )
        if len(allDoms) == 0:
            raise ErrDomNotFound

        for item in allDoms:
            await item.hover()
            await item.click()

        # 处理一级目录
        menusdom = await page.query_selector_all(
            "#hmenu-content > ul.hmenu.hmenu-visible li > a[data-menu-id]"
        )
        if len(menusdom) == 0:
            raise ErrDomNotFound

        menus: list[AwsMenu] = []
        for menuitem in menusdom:
            await menuitem.hover()
            await menuitem.click()

            # 处理二级目录
            children = await jshandle(page, subjs)
            title = await menuitem.inner_text()
            menus.append(AwsMenu(title, 0, "", AwsMenu.fromDict(children)))
            back = await page.query_selector(
                "#hmenu-content > ul.hmenu.hmenu-visible > li:nth-child(1) > a"
            )
            if back is None:
                raise ErrDomNotFound

            await back.hover()
            await back.click()

        return menus


async def main():
    p = AmazonParser()
    async with p.context() as page:
        try:
            menus = await p.openCate(page)
            print(menus)
        except Exception as e:
            print(e)


if __name__ == "__main__":
    asyncio.run(main())
