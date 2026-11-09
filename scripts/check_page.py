#!/usr/bin/env python3
"""发布前自检：在桌面宽度（浅色）和手机宽度（深色）各打开一次页面，检查
节点是否都有缩略图、图片是否都能加载、有没有脚本报错、页面是否横向溢出，
并打开第一张大图、试一次细节放大，各截一张图供目视检查。

用法：
  python3 check_page.py site/index.html [--shots 截图目录]
退出码：0 全部通过；1 有问题。
"""
import argparse, asyncio, functools, http.server, os, pathlib, socketserver, sys, threading


def serve(root):
    class Quiet(http.server.SimpleHTTPRequestHandler):
        def log_message(self, *a):
            pass
    handler = functools.partial(Quiet, directory=root)
    httpd = socketserver.TCPServer(('127.0.0.1', 0), handler)
    threading.Thread(target=httpd.serve_forever, daemon=True).start()
    return httpd


async def check(url, shots):
    from playwright.async_api import async_playwright
    bad = []
    async with async_playwright() as p:
        try:
            b = await p.chromium.launch(channel='chrome')
        except Exception:  # noqa: BLE001
            b = await p.chromium.launch()
        for name, vp, scheme in [('desktop', (1440, 960), 'light'), ('phone', (390, 844), 'dark')]:
            pg = await b.new_page(viewport={'width': vp[0], 'height': vp[1]}, color_scheme=scheme)
            errs = []
            pg.on('pageerror', lambda e: errs.append(str(e)))
            await pg.goto(url)
            await pg.wait_for_timeout(1200)
            await pg.click('#expand')
            await pg.wait_for_timeout(800)
            res = await pg.evaluate('''async () => {
              const nodes = [...document.querySelectorAll('.node')];
              const noThumb = nodes.filter(n => !n.querySelector('.th')).map(n => n.textContent.trim().slice(0, 24));
              const imgs = [...document.querySelectorAll('.th img')];
              imgs.forEach(i => i.loading = 'eager');
              await new Promise(r => setTimeout(r, 2500));
              const broken = [...new Set(imgs.filter(i => !i.complete || !i.naturalWidth).map(i => i.getAttribute('src')))];
              return {nodes: nodes.length, noThumb, broken, overflow: document.documentElement.scrollWidth - innerWidth};
            }''')
            await pg.click('#collapse')
            await pg.wait_for_timeout(400)
            await pg.locator('.lv1 > .node .th').first.click()
            await pg.wait_for_timeout(1600)
            if shots:
                await pg.screenshot(path=os.path.join(shots, f'check_{name}.png'))
            print(f"[{name}] 节点 {res['nodes']}，无图 {len(res['noThumb'])}，坏图 {len(res['broken'])}，横向溢出 {res['overflow']}px，脚本错误 {len(errs)}")
            for x in res['noThumb']:
                bad.append(f'[{name}] 节点无缩略图：{x}')
            for x in res['broken']:
                bad.append(f'[{name}] 图片加载失败：{x}')
            if res['overflow'] > 0:
                bad.append(f'[{name}] 页面横向溢出 {res["overflow"]}px')
            bad += [f'[{name}] 脚本错误：{e}' for e in errs]
            await pg.close()
        await b.close()
    return bad


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('page')
    ap.add_argument('--shots')
    a = ap.parse_args()
    page = pathlib.Path(a.page).resolve()
    if a.shots:
        os.makedirs(a.shots, exist_ok=True)
    httpd = serve(str(page.parent))
    url = f'http://127.0.0.1:{httpd.server_address[1]}/{page.name}'
    bad = asyncio.run(check(url, a.shots))
    httpd.shutdown()
    for x in bad:
        print('  ✗', x)
    print('PASS' if not bad else f'FAIL：{len(bad)} 个问题')
    sys.exit(1 if bad else 0)


if __name__ == '__main__':
    main()
