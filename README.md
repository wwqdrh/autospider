# 示例

```Python
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


await ActionTree.factory_ymlstr(OPEN_CLICK).start()
```
