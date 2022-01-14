import pytest

from spider.action import ActionTree
from spider.action.control import OpenAction, GotoAction, ClickAction
from spider.action.flow import ForElementAction


OPEN_CLICK = """
- type: open
  headless: false
  next:
    - type: goto
      url: "https://wwqdrh.github.io/compass#/#Python"
      next:
        - type: forelement
          element: '//*[@id="app"]/div/div[2]/div[1]/div[1]/ul/a'
          next:
            - type: click
              element: '.'
"""


@pytest.mark.asyncio
async def test_ymlstr():
    await ActionTree.factory_ymlstr(OPEN_CLICK).start()


@pytest.mark.asyncio
async def test_open_click():
    await ActionTree.factory_nodes(
        [
            OpenAction(
                "",
                False,
                GotoAction(
                    "",
                    "https://wwqdrh.github.io/compass#/#Python",
                    ForElementAction(
                        "",
                        '//*[@id="app"]/div/div[2]/div[1]/div[1]/ul/a',
                        ClickAction(
                            "#click1",
                            ".",
                        ),
                    ),
                ),
            )
        ]
    ).start()


# //*[@id="app"]/div/div[2]/div[1]/div[1]/ul/a[4]
