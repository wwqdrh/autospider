import pytest

from autospider import ActionTree


@pytest.mark.asyncio
async def test_action_openclick():
    await ActionTree.factory_ymlstr(
        """
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
                      path: './pic'
"""
    ).start()


@pytest.mark.asyncio
async def test_action_downonebg():
    await ActionTree.factory_ymlstr(
        """
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
   """
    ).start()


@pytest.mark.asyncio
async def test_action_downiterbg():
    await ActionTree.factory_ymlstr(
        """
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
   """
    ).start()


@pytest.mark.asyncio
async def test_num_for():
    await ActionTree.factory_ymlstr(
        """
- type: open
  headless: false
  next:
    - type: goto
      url: 'https://wwqdrh.github.io/mall.html#/detail/1'
      next:
        - type: numfor
          nums: 3
          next:
            - type: click
              element: '//*[@id="app"]/div/div/main/div/div[2]/div[1]/div/span[2]/i'
   """
    ).start()


@pytest.mark.asyncio
async def test_pic_down():
    await ActionTree.factory_ymlstr(
        """
- type: open
  proxy: '127.0.0.1:7890'
  headless: false
  next:
    - type: goto
      url: "https://www.xsnvshen.com/album/37664"
      next:
        - type: click
          element: '//*[@id="showlists"]'
        - type: forelement
          element: '//html/body/div[4]/div/div[4]/ul/li'
          next:
            - type: locator
              element: 'div img'
              next:
                - type: downpic
    """
    ).start()


@pytest.mark.asyncio
async def test_pic_down_2():
    await ActionTree.factory_ymlstr(
        """
- type: open
  headless: false
  next:
    - type: numrange
      start: 36
      end: 36
      build: "https://img.f2mm.com/gallery3/20220110/25266/{}.jpg"
      next:
        - type: download
          path: './pic'
          proxy: "http://127.0.0.1:7890"
          https: true
    """
    ).start()


@pytest.mark.asyncio
async def test_pic_down_3():
    await ActionTree.factory_ymlstr(
        """
- type: open
  headless: false
  next:
    - type: numrange
      start: 23
      end: 79
      build: "https://i.nshens.com/storage/image2/xiuren/no.4341/8cc9a7526c3f048e235bad1c0577cdd8/{}.jpg"
      next:
        - type: download
          path: './pic'
          proxy: "http://127.0.0.1:7890"
          https: true
    """
    ).start()


@pytest.mark.asyncio
async def test_pic_down_4():
    await ActionTree.factory_ymlstr(
        """
- type: open
  headless: false
  next:
    - type: numrange
      start: 0
      end: 61
      fill: 3
      build: "https://img.xsnvshen.com/album/22162/36367/{}.jpg"
      next:
        - type: download
          path: './pic'
          proxy: "http://127.0.0.1:7890"
          https: true
          wait: 2
    """
    ).start()
