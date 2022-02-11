# 测试获取易仓的apidoc中的数据

import pytest

from autospider.action import ActionTree


@pytest.mark.asyncio
async def test_action_ecapi():
    await ActionTree.factory_ymlstr(
        """
- type: open
  headless: false
  next:
    - type: goto
      url: "https://open.eccang.com/#/DocumentCenter"
      next:
        - type: forelement
          element: '//*[@id="app"]/section/main/div/section/aside/div/div/ul/li[2]/ul/li'
          next:
            - type: click
              next:
                - type: forelement
                  element: '//ul/li'
                  next:
                    - type: click
                      next:
                        - type: print
                          text: "=====\n"
                        - type: text
                          next:
                            - type: print
                        - type: element
                          element: ".fun_"
                          next:
                            - type: text
                              next: 
                                - type: print
                        - type: print
                          text: "=====\n"
                        - type: sleep
                          sleep_time: 1
                        - type: forelement
                          root: true
                          element: '.lake-table'
                          next:
                            - type: forelement
                              element: '//tbody/tr'
                              next:
                                - type: text
                                  next:
                                    - type: print
        - type: sleep
          sleep_time: 3

"""
    ).start()
