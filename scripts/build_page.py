#!/usr/bin/env python3
"""把 data.json 填进页面模板，生成单个 HTML，并校验每个节点都挂了存在的图片。

用法：
  python3 build_page.py data.json -o out/index.html
  python3 build_page.py data.json -o out/index.html --strict   # 有缺图时返回非 0

data.json 结构见 references/data-schema.md。图片路径 = 输出 HTML 所在目录 / meta.base / asset.f。
"""
import argparse, html, json, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
TEMPLATE = os.path.join(HERE, '..', 'assets', 'template.html')
STATUS_CODES = {'ok', 'pv', 'cs', 'br', 'td', 'sm'}


def walk(node, depth=0, path=()):
    yield node, depth, path
    for k in node.get('c', []) or []:
        yield from walk(k, depth + 1, path + (node.get('t', ''),))


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('data')
    ap.add_argument('-o', '--out', required=True)
    ap.add_argument('--template', default=TEMPLATE)
    ap.add_argument('--strict', action='store_true', help='缺图或引用错误时以非 0 退出')
    a = ap.parse_args()

    with open(a.data, encoding='utf-8') as f:
        data = json.load(f)
    meta, assets, tree = data.get('meta', {}), data.get('assets', {}), data.get('tree')
    if not tree:
        sys.exit('data.json 缺少 tree')

    out_dir = os.path.dirname(os.path.abspath(a.out))
    base = meta.get('base', 'assets/')
    problems, used, nodes = [], set(), 0
    for node, depth, path in walk(tree):
        nodes += 1
        where = ' / '.join(path + (node.get('t', '?'),))
        key = node.get('i')
        if not key:
            problems.append(f'节点没有图片：{where}')
        elif key not in assets:
            problems.append(f'节点引用了不存在的素材 {key!r}：{where}')
        else:
            used.add(key)
        for s in node.get('s', []) or []:
            if s not in STATUS_CODES:
                problems.append(f'未知状态码 {s!r}（可用 {sorted(STATUS_CODES)}）：{where}')
        z = node.get('z')
        if z is not None and (len(z) != 4 or not all(0 <= v <= 1 for v in z)):
            problems.append(f'z 细节框应为 4 个 0–1 的数：{where}')
        if depth == 1 and node.get('color') not in (None, 1, 2, 3, 4, 5, 6):
            problems.append(f'一级分支 color 只能是 1–6：{where}')
    for key, asset in assets.items():
        p = os.path.join(out_dir, base, asset.get('f', ''))
        if not asset.get('f') or not os.path.isfile(p):
            problems.append(f'素材文件不存在：{key} → {p}')
        if not asset.get('c'):
            problems.append(f'素材缺少说明 c（来源与日期）：{key}')
        fb = asset.get('focus')
        if fb is not None and (len(fb) != 4 or not all(0 <= v <= 1 for v in fb)):
            problems.append(f'素材 focus 细节框应为 4 个 0–1 的数：{key}')
    unused = sorted(set(assets) - used)

    with open(a.template, encoding='utf-8') as f:
        tpl = f.read()
    payload = json.dumps(data, ensure_ascii=False).replace('</', '<\\/')
    page = tpl.replace('/*__MINDMAP_DATA__*/null', payload).replace('__TITLE__', html.escape(meta.get('title', '功能交互脑图')))
    os.makedirs(out_dir, exist_ok=True)
    with open(a.out, 'w', encoding='utf-8') as f:
        f.write(page)

    for p in problems:
        print('  ✗', p)
    if unused:
        print('  · 未被引用的素材：', ', '.join(unused))
    status = 'OK' if not problems else 'WARN'
    print(f'{status}: {nodes} 个节点，{len(assets)} 张素材，{len(problems)} 个问题 → {a.out}')
    if problems and a.strict:
        sys.exit(1)


if __name__ == '__main__':
    main()
