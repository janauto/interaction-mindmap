#!/usr/bin/env python3
"""按清单用 Playwright 打开网页、执行操作、截取元素或整页，批量产出真实界面截图。

用法：
  python3 shoot.py shots.json --out shots/

shots.json：
  [
    {"url": "http://127.0.0.1:8791/proto/index.html", "viewport": [1440, 1000], "wait": 2000,
     "steps": [
       {"eval": "state.screen = 'lock'; render()"},
       {"wait": 300},
       {"shot": ".device", "out": "device.png"},
       {"click": "[data-scene='media']"},
       {"shot": ".lab-device", "out": "media.png"},
       {"shot": null, "out": "full.png", "full_page": true}
     ]}
  ]
url 可以是 http(s):// 或本地文件路径。优先用系统 Chrome（channel=chrome），没有就用 Playwright 自带 Chromium。
"""
import argparse, asyncio, json, os, pathlib


async def run(cfg, out):
    from playwright.async_api import async_playwright
    async with async_playwright() as p:
        try:
            browser = await p.chromium.launch(channel='chrome')
        except Exception:  # noqa: BLE001
            browser = await p.chromium.launch()
        for job in cfg:
            vw, vh = job.get('viewport', [1440, 1000])
            page = await browser.new_page(viewport={'width': vw, 'height': vh}, device_scale_factor=job.get('scale', 2))
            url = job['url']
            if '://' not in url:
                url = pathlib.Path(url).resolve().as_uri()
            await page.goto(url)
            await page.wait_for_timeout(job.get('wait', 1200))
            for st in job.get('steps', []):
                if 'eval' in st:
                    await page.evaluate(st['eval'])
                if 'click' in st:
                    await page.locator(st['click']).first.click()
                    await page.wait_for_timeout(st.get('after', 350))
                if 'wait' in st and len(st) == 1:
                    await page.wait_for_timeout(st['wait'])
                if 'out' in st:
                    path = os.path.join(out, st['out'])
                    if st.get('shot'):
                        await page.locator(st['shot']).first.screenshot(path=path)
                    else:
                        await page.screenshot(path=path, full_page=st.get('full_page', False))
                    print('saved', path)
            await page.close()
        await browser.close()


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('config')
    ap.add_argument('--out', required=True)
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    with open(a.config, encoding='utf-8') as f:
        asyncio.run(run(json.load(f), a.out))


if __name__ == '__main__':
    main()
