from typing import Any, Tuple, Sequence, List
import asyncio
import random, string

from playwright.async_api import TimeoutError

from autospider.types.action import IAction
from autospider.action.base import BaseAction


class IfAction(BaseAction):
    pass


class ElementAction(BaseAction):
    def __init__(
        self, child_actions: List["IAction"], element: str, context_id: str = ""
    ) -> None:
        super().__init__(child_actions, context_id)
        self._element = element

    async def run(self, context: Any):
        page = self.get_context("page")
        c = page.locator(self._element)
        await self.run_child(c)


class ForElementAction(BaseAction):
    def __init__(
        self,
        child_actions: List["IAction"],
        element: str,
        root: bool = False,
        context_id: str = "",
    ) -> None:
        super().__init__(child_actions, context_id)
        self._element = element
        self._root = root

    async def run(self, context: Any):
        if self._root:
            context = self.get_context("page")

        try:
            c = context.locator(self._element)
            count = await c.count()
            for i in range(count):
                cur = c.nth(i)
                # print(await cur.inner_html())
                # print(await cur.locator("div >> nth = 0").get_attribute("style"))
                await self.run_child(cur)
        except TimeoutError:
            print("超时")

    async def stop(self):
        pass


class NumForAction(BaseAction):
    def __init__(
        self, child_actions: List["IAction"], nums: int, context_id: str = ""
    ) -> None:
        super().__init__(child_actions, context_id)
        self._nums = nums

    async def run(self, context: Any):
        for _ in range(1, self._nums + 1):
            await self.run_child(context)


class NumBuildAction(BaseAction):
    def __init__(
        self,
        child_actions: List["IAction"],
        nums: int,
        build: str,
        context_id: str = "",
    ) -> None:
        super().__init__(child_actions, context_id)
        self.nums = nums
        self.build = build

    async def run(self, context: Any):
        for i in range(1, self.nums + 1):
            await self.run_child(self.build.format(i))


class NumRangeAction(BaseAction):
    def __init__(
        self,
        child_actions: List["IAction"],
        start: int,
        end: int,
        build: str,
        fill: int = 0,
        context_id: str = "",
    ) -> None:
        super().__init__(child_actions, context_id)
        self.start = start
        self.end = end
        self.build = build
        self.fill = fill

    async def run(self, context: Any):
        for i in range(self.start, self.end + 1):
            await self.run_child(self.build.format(str(i).zfill(self.fill)))


class SleepAction(BaseAction):
    def __init__(
        self, child_actions: List["IAction"], sleep_time: int, context_id: str = ""
    ) -> None:
        super().__init__(child_actions, context_id)
        self._sleep_time = sleep_time

    async def run(self, context: Any):
        await asyncio.sleep(self._sleep_time)
        await self.run_child(context)


class PrintAction(BaseAction):
    def __init__(
        self, child_actions: List["IAction"], text: str = "", context_id: str = ""
    ) -> None:
        super().__init__(child_actions, context_id)
        self._text = text

    async def run(self, context: Any):
        if self._text != "":
            print(self._text)
        else:
            print(context)

        await self.run_child(context)


class SaveAction(BaseAction):
    def __init__(
        self, child_actions: List["IAction"], file: str, context_id: str = ""
    ) -> None:
        super().__init__(child_actions, context_id)
        self._file = file

    async def run(self, context: Any):
        with open(self._file, "a+", encoding="utf8") as f:
            f.write(context + "\n")

        await self.run_child(context)


class DownPicAction(BaseAction):
    """
        1、主要原理获取元素的src值 动态构造一个a标签设置href、download然后执行点击，
        但是对于非同源的图片还是会直接打开

        2、如果想转换成dataurl 需要服务器开启支持跨域
        function downloadIamge() {
            var image = new Image()
            // 解决跨域 Canvas 污染问题
            image.setAttribute('crossOrigin', 'anonymous')
            image.onload = function () {

                // 生成一个a元素
                var a = document.createElement('a')
                // 创建一个单击事件
                var event = new MouseEvent('click')

                // 将a的download属性设置为我们想要下载的图片名称，若name不存在则使用‘下载图片名称’作为默认名称
                a.download = '下载图片名称'
                // 将生成的URL设置为a.href属性
                a.href = "//img.xsnvshen.com/thumb_600x900/album/22162/37664/000.jpg"

                // 触发a的单击事件
                a.dispatchEvent(event)
            }

            image.src = "//img.xsnvshen.com/thumb_600x900/album/22162/37664/000.jpg"
        }

        3、新建iframe 然后使用document.execCommand("SaveAs") saveas 在只在ie中起作用，chrome、firefox不支持

        4、xmlhttprequest+blob下载内容 包括gif 无法设置跨域
        function download(link, filename){
      let xhr = new XMLHttpRequest()
      // 前端设置是否带cookie
    xhr.withCredentials = true;
      xhr.open('get', link, true)
      xhr.responseType = 'blob'
      xhr.onload = function(){
        let url = URL.createObjectURL(xhr.response)
        let a = document.createElement('a')
        let event = new MouseEvent('click')
        a.href = link
        a.download = filename || 'default.png'
        a.dispatchEvent(event)
        URL.revokeObjectURL(url)
      }
      xhr.send()
    }

    5、使用fetch fetch为什么为空
    fetch(new Request('//img.xsnvshen.com/thumb_600x900/album/22162/37664/000.jpg', {
      method: 'GET',
      headers: {
          'Origin': '*.xsnvshen.com'
        },
      mode: 'cors', // same-origin cors
      cache: 'default',
      referrerPolicy: 'no-referrer',
    }))
      .then(response => {
          console.log(response)
          return response.blob();
      })
      .then(myBlob => {
        let url = URL.createObjectURL(myBlob);
        console.log(myBlob, url)
        let a = document.createElement('a')
        let event = new MouseEvent('click')
        a.href = url
        a.download = 'default.png'
        a.dispatchEvent(event)
        URL.revokeObjectURL(url)
      });

      6、Refused to display 'https://img.xsnvshen.com/' in a frame because it set 'X-Frame-Options' to 'sameorigin'.
      var iframe = document.createElement("iframe");
        document.body.append(iframe)
        var script = document.createElement("script");  //创建一个script标签
        script.type = "text/javascript";
        script.text = `
        function download(link, filename){
      let xhr = new XMLHttpRequest()
      // 前端设置是否带cookie
    xhr.withCredentials = true;
      xhr.open('get', link, true)
      xhr.responseType = 'blob'
      xhr.onload = function(){
        let url = URL.createObjectURL(xhr.response)
        let a = document.createElement('a')
        let event = new MouseEvent('click')
        a.href = link
        a.download = filename || 'default.png'
        a.dispatchEvent(event)
        URL.revokeObjectURL(url)
      }
      xhr.send()
    }
    download({}, {})
        `
        var img = document.createElement("img")
        img.src = ""
        iframe.contentDocument.body.append(imt)
        iframe.contentDocument.body.append(script);


        7、只能在后端处理下 对于新页面就打开一个page
    """

    TARGET_EXEC = """
    function download(link, filename){
  let xhr = new XMLHttpRequest()
  // 前端设置是否带cookie
xhr.withCredentials = true;
  xhr.open('get', link, true)
  xhr.responseType = 'blob'
  xhr.onload = function(){
    let url = URL.createObjectURL(xhr.response)
    let a = document.createElement('a')
    let event = new MouseEvent('click')
    a.href = link
    a.download = filename || 'default.png'
    a.dispatchEvent(event)
    URL.revokeObjectURL(url)
  }
  xhr.send()
}
download({}, {})
    """

    def __init__(self, child_actions: List["IAction"], context_id: str = "") -> None:
        super().__init__(child_actions, context_id)

    async def run(self, context: Any):
        """
        # 在新的页面中下载图片 避免同源策略 以及x-Frame-options防范
        # 但是目标网站太牛了 也不知道限制访问的策略是什么 反正就想直接访问很大概率是拒绝的
        # 还是只能够用右键事件来处理 或者 加载了一个页面之后使用方法读取disk cache(成功几率不大 不知道缓存机制 且不一定提供了api使用 即使提供了 单纯的js脚本也不一定有能力操作)
        """
        pass
        # url = await context.get_attribute("src")
        # browser = self.get_context("browser")
        # page = await browser.new_page()
        # await page.goto("https:" + url)
        # *_, fileName = url.rpartition("/")
        # fileName = "".join(random.sample(string.ascii_letters, 6)) + fileName
        # script = self.TARGET_EXEC.format(url, fileName)
        # await page.close()
