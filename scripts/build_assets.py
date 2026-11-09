#!/usr/bin/env python3
"""按一份清单把原始截图批量压成页面素材：WebP、并排拼图、帧序列 GIF、裁局部、原样拷贝。

用法：
  python3 build_assets.py recipe.json --src raw/ local/ shots/ --out site/assets/

recipe.json 是一个数组，每项一个操作（src 只写文件名，按 --src 目录顺序查找；同名时可写 "目录名:文件名"）：
  {"key": "home",   "op": "webp",  "src": "home.png", "max_h": 720, "max_w": 900}
  {"key": "screen", "op": "crop",  "src": "home.png", "box": [0, 0, 480, 200]}      # 像素框，裁完再压
  {"key": "four",   "op": "strip", "src": ["a.png", "b.png", "c.png"], "h": 560}  # 并排拼成一张
  {"key": "flow",   "op": "gif",   "src": ["s1.png", "s2.png", "s3.png"], "ms": 900, "h": 480}
  {"key": "demo",   "op": "copy",  "src": "demo.gif"}                              # 已有 GIF 原样保留
输出文件名 = key + 扩展名（webp / gif / 原扩展名）。
"""
import argparse, glob, json, os, shutil, sys
from PIL import Image


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('recipe')
    ap.add_argument('--src', nargs='+', required=True, help='原始图片所在目录，按顺序查找')
    ap.add_argument('--out', required=True)
    ap.add_argument('--quality', type=int, default=80)
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)

    pool = {}
    for d in a.src:
        tag = os.path.basename(os.path.normpath(d))
        for f in glob.glob(os.path.join(d, '*')):
            b = os.path.basename(f).split('__')[-1]
            pool.setdefault(f'{tag}:{b}', f)
            pool.setdefault(b, f)

    def P(n):
        if n in pool:
            return pool[n]
        sys.exit(f'找不到原图：{n}（查找目录 {a.src}）')

    def fit(im, mh=720, mw=900):
        im = im.convert('RGB')
        r = min(mh / im.height, mw / im.width, 1)
        return im.resize((round(im.width * r), round(im.height * r)), Image.LANCZOS) if r < 1 else im

    def save_webp(im, key):
        p = os.path.join(a.out, key + '.webp')
        im.save(p, 'WEBP', quality=a.quality, method=6)
        return p

    with open(a.recipe, encoding='utf-8') as f:
        ops = json.load(f)
    total = 0
    for o in ops:
        key, op = o['key'], o.get('op', 'webp')
        if op == 'webp':
            p = save_webp(fit(Image.open(P(o['src'])), o.get('max_h', 720), o.get('max_w', 900)), key)
        elif op == 'crop':
            im = Image.open(P(o['src'])).convert('RGB').crop(tuple(o['box']))
            p = save_webp(fit(im, o.get('max_h', 720), o.get('max_w', 900)), key)
        elif op == 'strip':
            h, gap = o.get('h', 560), o.get('gap', 16)
            ims = [fit(Image.open(P(s)), h, 10000) for s in o['src']]
            W = sum(i.width for i in ims) + gap * (len(ims) + 1)
            canvas = Image.new('RGB', (W, h + 2 * gap), tuple(o.get('bg', [236, 239, 241])))
            x = gap
            for i in ims:
                canvas.paste(i, (x, gap)); x += i.width + gap
            p = save_webp(fit(canvas, 720, o.get('max_w', 1600)), key)
        elif op == 'gif':
            frames = [fit(Image.open(P(s)), o.get('h', 480), 10000).convert('P', palette=Image.ADAPTIVE, colors=128) for s in o['src']]
            p = os.path.join(a.out, key + '.gif')
            frames[0].save(p, save_all=True, append_images=frames[1:], duration=o.get('ms', 800), loop=0, optimize=True)
        elif op == 'copy':
            src = P(o['src'])
            p = os.path.join(a.out, key + os.path.splitext(src)[1].lower())
            shutil.copy(src, p)
        else:
            sys.exit(f'未知操作 {op!r}')
        total += os.path.getsize(p)
        print(f'{key:24s} {op:6s} {os.path.getsize(p) // 1024:5d} KB')
    print(f'共 {len(ops)} 张，{total / 1024 / 1024:.1f} MB → {a.out}')


if __name__ == '__main__':
    main()
