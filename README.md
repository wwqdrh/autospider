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

# 如何使用

包安装好之后需要执行 `playwright install`, 安装playwright所需要的chromium