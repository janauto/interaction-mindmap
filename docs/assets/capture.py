#!/usr/bin/env python3
"""重新生成 README 里的截图和动图（截图即代码）。先生成示例页面，再运行：
  python3 examples/demo/make_demo_images.py
  python3 scripts/build_assets.py examples/demo/recipe.json --src examples/demo/raw --out examples/demo/site/assets
  python3 scripts/build_page.py examples/demo/data.json -o examples/demo/site/index.html
  python3 docs/assets/capture.py
"""
import asyncio, functools, http.server, os, pathlib, socketserver, threading, subprocess, shutil
ROOT = pathlib.Path(__file__).resolve().parents[2]
SITE = ROOT / 'examples/demo/site'
OUT = pathlib.Path(__file__).resolve().parent


class Quiet(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *a):
        pass


async def main():
    from playwright.async_api import async_playwright
    httpd = socketserver.ThreadingTCPServer(('127.0.0.1', 0), functools.partial(Quiet, directory=str(SITE)))
    threading.Thread(target=httpd.serve_forever, daemon=True).start()
    url = f'http://127.0.0.1:{httpd.server_address[1]}/index.html'
    async with async_playwright() as p:
        try:
            b = await p.chromium.launch(channel='chrome')
        except Exception:  # noqa: BLE001
            b = await p.chromium.launch()
        # 1. 桌面：展开全部 + 打开「长按菜单」大图并自动放大细节
        pg = await b.new_page(viewport={'width': 1440, 'height': 900}, device_scale_factor=1)
        await pg.goto(url); await pg.wait_for_timeout(1200)
        await pg.click('#expand'); await pg.wait_for_timeout(900)
        await pg.screenshot(path=str(OUT / 'map.png'))
        idx = await pg.evaluate("__mindmap.all.findIndex(r => r.text.startsWith('长按菜单'))")
        await pg.evaluate(f'__mindmap.open({idx})'); await pg.wait_for_timeout(1800)
        await pg.screenshot(path=str(OUT / 'viewer.png'))
        # 2. 动图：逐个切换场景、自动放大细节
        frames = OUT / '_frames'; shutil.rmtree(frames, ignore_errors=True); frames.mkdir()
        await pg.evaluate('__mindmap.open(1)'); n = 0
        for step in range(7):
            for t in range(6):
                await pg.wait_for_timeout(220)
                await pg.screenshot(path=str(frames / f'{n:03d}.png'), clip={'x': 520, 'y': 0, 'width': 920, 'height': 900}); n += 1
            await pg.keyboard.press('ArrowRight')
        await pg.close()
        # 3. 手机深色
        pg = await b.new_page(viewport={'width': 390, 'height': 844}, color_scheme='dark', device_scale_factor=2)
        await pg.goto(url); await pg.wait_for_timeout(1200)
        await pg.evaluate('__mindmap.open(4)'); await pg.wait_for_timeout(1800)
        await pg.screenshot(path=str(OUT / 'phone.png'))
        await b.close()
    httpd.shutdown()
    subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-framerate', '5', '-i', str(frames / '%03d.png'),
                    '-vf', 'scale=640:-1:flags=lanczos,split[a][b];[a]palettegen=max_colors=96[p];[b][p]paletteuse=dither=bayer',
                    str(OUT / 'browse.gif')], check=True)
    shutil.rmtree(frames)
    print('README 截图已更新 →', OUT)


asyncio.run(main())
