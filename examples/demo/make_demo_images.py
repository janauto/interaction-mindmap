#!/usr/bin/env python3
"""生成示例用的屏幕图（脚本画的示意画面，不是任何真实产品）。只用于演示脑图的结构与交互。"""
import os
from PIL import Image, ImageDraw, ImageFont

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'raw')
os.makedirs(OUT, exist_ok=True)
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


W, H = 480, 800
BG, FG, MUTED, ACC = (18, 22, 26), (236, 240, 242), (140, 150, 158), (76, 192, 183)


def screen(name, title, lines, accent=ACC, big=None, keys=('◀', 'M', '▶', 'SET')):
    im = Image.new('RGB', (W, H), BG)
    d = ImageDraw.Draw(im)
    d.text((24, 18), '09:41', fill=MUTED, font=font(22))
    d.text((W - 24, 18), 'DEMO', fill=accent, font=font(22), anchor='ra')
    d.text((24, 70), title, fill=FG, font=font(40))
    y = 140
    if big:
        d.text((W // 2, 300), big, fill=accent, font=font(120), anchor='mm')
        y = 430
    for ln in lines:
        d.rounded_rectangle((24, y, W - 24, y + 72), 16, fill=(32, 38, 44))
        d.text((44, y + 36), ln, fill=FG, font=font(26), anchor='lm')
        y += 88
    d.rectangle((0, H - 64, W, H), fill=(28, 33, 38))
    for i, k in enumerate(keys):
        d.text((W * (2 * i + 1) // 8, H - 32), k, fill=MUTED, font=font(24), anchor='mm')
    im.save(os.path.join(OUT, name))
    return im


screen('home.png', '首页', ['今日 3 项待办', '天气 22°'], big='10:30')
screen('drawer.png', '应用抽屉', ['计时器', '天气', '笔记', '设置'])
screen('drawer_menu.png', '长按菜单', ['打开', '置顶', '重命名', '卸载'], accent=(238, 149, 98))
screen('settings.png', '设置', ['亮度', '震动', '蓝牙', '关于'])
screen('voice.png', '正在听…', ['松开发送'], big='((·))')
screen('notice.png', '通知', ['快递已到驿站', '会议 14:00', '电量 20%'], accent=(139, 158, 240))
for i, sec in enumerate([5, 4, 3, 2, 1, 0]):
    screen(f'timer_{i}.png', '计时器', ['M 暂停 · SET 返回'], big=f'00:0{sec}')
# 横图：按键位置示意
im = Image.new('RGB', (900, 420), (236, 239, 241))
d = ImageDraw.Draw(im)
d.rounded_rectangle((300, 40, 600, 380), 40, fill=BG)
for i, k in enumerate(['◀', 'M', '▶']):
    d.ellipse((330 + i * 90, 300, 390 + i * 90, 360), fill=(60, 68, 76))
    d.text((360 + i * 90, 330), k, fill=FG, font=font(24), anchor='mm')
d.rounded_rectangle((604, 140, 620, 230), 6, fill=(60, 68, 76))
d.text((640, 185), 'SET 侧键', fill=(26, 31, 35), font=font(26), anchor='lm')
d.text((40, 40), 'DEMO · 按键示意', fill=(91, 101, 109), font=font(26))
im.save(os.path.join(OUT, 'keys.png'))
print('demo images →', OUT)
