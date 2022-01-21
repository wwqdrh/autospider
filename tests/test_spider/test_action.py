import pytest

from autospider.action import ActionTree


@pytest.mark.asyncio
async def test_action_openclick():
    await ActionTree.factory_ymlstr("""
- type: open
  headless: false
  next:
    - type: goto
      url: "https://wwqdrh.github.io/mall.html#/"
      next:
        - type: forelement
          element: '//*[@id="app"]/div/div/main/div/div[2]/div'
          next:
            - type: locator
              element: 'div >> nth = 0'
              next:
                - type: attr
                  name: 'style'
                  next:
                    - type: download
""").start()


@pytest.mark.asyncio
async def test_action_downonebg():
   await ActionTree.factory_ymlstr("""
- type: open
  headless: false
  next:
    - type: goto
      url: 'https://wwqdrh.github.io/mall.html#/'
      next:
        - type: locator
          element: '//*[@id="app"]/div/div/main/div/div[2]/div[1]/div[1]'
          next:
            - type: backgroundurl
              next:
                - type: download
                  path: './pic'
   """).start()


@pytest.mark.asyncio
async def test_action_downiterbg():
   await ActionTree.factory_ymlstr("""
- type: open
  headless: false
  next:
    - type: goto
      url: 'https://wwqdrh.github.io/mall.html#/'
      next:
        - type: forelement
          element: '//*[@id="app"]/div/div/main/div/div[2]/div'
          next:
            - type: locator
              element: 'div >> nth = 0'
              next:
                - type: backgroundurl
                  next:
                    - type: download
                      path: './pic'
   """).start()