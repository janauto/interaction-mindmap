#!/usr/bin/env python3
"""把一批图片（含 GIF 首帧）拼成带编号和文件名的对照表，方便一次看完再挑图。

用法：
  python3 contact_sheet.py out.png img1.png img2.webp dir/*.gif
  python3 contact_sheet.py out.png --cols 5 --cell 330x560 a.png b.png   # 放大看细节
同时把「编号 文件路径」打印到标准输出。
"""
import argparse, os
from PIL import Image, ImageDraw, ImageFont

FONTS = ['/System/Library/Fonts/STHeiti Medium.ttc', '/System/Library/Fonts/PingFang.ttc',
         '/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc', '/usr/share/fonts/noto-cjk/NotoSansCJK-Regular.ttc',
         'C:/Windows/Fonts/msyh.ttc']


def font(size):
    for p in FONTS:
        if os.path.exists(p):
            try:
                return ImageFont.truetype(p, size)
            except OSError:
                pass
    return ImageFont.load_default()


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('out')
    ap.add_argument('files', nargs='+')
    ap.add_argument('--cols', type=int, default=6)
    ap.add_argument('--cell', default='200x230', help='每格宽x高，默认 200x230')
    a = ap.parse_args()
    W, H = map(int, a.cell.lower().split('x'))
    files = [f for f in a.files if os.path.isfile(f)]
    if not files:
        raise SystemExit('没有可用的图片')
    f11 = font(11)
    rows = (len(files) + a.cols - 1) // a.cols
    sheet = Image.new('RGB', (a.cols * W, rows * H), 'white')
    d = ImageDraw.Draw(sheet)
    for i, fp in enumerate(files):
        x, y = (i % a.cols) * W, (i // a.cols) * H
        try:
            im = Image.open(fp); im.seek(0); size = im.size
            im = im.convert('RGB'); im.thumbnail((W - 8, H - 36))
            sheet.paste(im, (x + 4, y + 4))
        except Exception as e:  # noqa: BLE001
            size = ('ERR', str(e)[:20])
        name = os.path.basename(fp).split('__')[-1]
        d.text((x + 4, y + H - 30), f'{i}:{name[:30]}', fill='black', font=f11)
        d.text((x + 4, y + H - 16), f'{size[0]}x{size[1]}', fill='gray', font=f11)
        print(i, fp)
    sheet.save(a.out)


if __name__ == '__main__':
    main()
