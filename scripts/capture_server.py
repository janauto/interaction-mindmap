#!/usr/bin/env python3
"""本地静态服务 + 截图接收：把原型目录当网站跑起来，页面里用 fetch('/save') 把 canvas 画面存成文件。

用法：
  python3 capture_server.py <网站根目录> <截图输出目录> [端口，默认 8791]

页面里（浏览器控制台或自动化脚本）：
  const cv = document.querySelector('canvas');
  await fetch('/save', {method: 'POST', body: JSON.stringify({name: 'home.png', data: cv.toDataURL('image/png')})});
适合用 canvas 绘制的原型（固件模拟器、游戏画面）：直接改它的状态变量、调用它的 render()，逐个状态存图。
"""
import base64, functools, http.server, json, os, sys


def main():
    if len(sys.argv) < 3:
        sys.exit(__doc__)
    root, out = sys.argv[1], sys.argv[2]
    port = int(sys.argv[3]) if len(sys.argv) > 3 else 8791
    os.makedirs(out, exist_ok=True)

    class Handler(http.server.SimpleHTTPRequestHandler):
        def do_POST(self):
            n = int(self.headers['Content-Length'])
            d = json.loads(self.rfile.read(n))
            name = os.path.basename(d['name'])
            with open(os.path.join(out, name), 'wb') as f:
                f.write(base64.b64decode(d['data'].split(',', 1)[1]))
            self.send_response(200); self.end_headers(); self.wfile.write(b'ok')

        def log_message(self, *args):
            pass

    print(f'serving {root} on http://127.0.0.1:{port}  ·  POST /save → {out}')
    http.server.ThreadingHTTPServer(('127.0.0.1', port), functools.partial(Handler, directory=root)).serve_forever()


if __name__ == '__main__':
    main()
