---
name: interaction-mindmap
description: 把产品原型、App 或竞品整理成「功能交互脑图」网页——每个节点配一张真实截图（设备截屏、原型画面、手机实机截图、评测图），点开看大图，可逐个切换功能场景、放大细节、自动导览，并标注实机 / 预览 / 开发中等可靠程度。适用于：用户要做功能交互脑图、交互全景图、竞品交互对比脑图、产品功能地图，或要求「每个节点配真实图片」「切换到每个功能场景的截图」「细节放大」时，即使没说「脑图」二字（如「把原型和 App 的功能理一张图」「竞品按钮和软件交互可视化」）。Builds a screenshot-backed, interactive feature/interaction mind map (HTML) for a product, prototype, app, or competitors.
---

# interaction-mindmap

产出一个单页 HTML：从左向右展开的功能交互脑图，**每个节点都挂真实截图**；点开大图后能按全树顺序切换场景、在同级场景间跳转、放大细节、自动导览。页面模板、素材压缩、原型截图、生成与自检都有现成脚本，主要工作量在「把结构理对」和「给每个节点找到对的图」。

## 产出物

1. `<目录>/index.html`（或项目里约定的文件名）——由 `assets/template.html` + `data.json` 生成。
2. `<目录>/assets/`——压缩后的 WebP / GIF 素材。
3. `data.json`、`recipe.json`、`shots.json`——结构和素材的来源配置，跟页面一起留档，方便以后重建。
4. （可用时）发布为 Artifact 的链接。

## 基本原则

- **每个节点一张真实的图，图下写来源和日期。** 没有专门画面的节点，用最接近的真实画面并在图说里注明；不画假界面、不用 AI 生成图冒充截图。
- **可靠程度要分清。** 实机验证过的、只在预览里跑过的、开发分支上的、原型模拟的，用状态徽标区分；只在预览里跑过的功能不配实机截图。
- **写「怎么用」，不写功能清单。** 每个面板 / 页面写清怎么打开、怎么关、按键在这里代表什么；同一个键在不同上下文的含义分开写。
- **资料里没有的不写。** 推测放在给用户的说明里，不进脑图。

## 工作流程

按顺序做，用到哪份参考文档时再读。

### 1. 读资料，定结构

先读完要覆盖的全部资料：原型源码与说明、产品说明、App 源码（页面文案比文档准）、调研报告。然后读 `references/tree-design.md`，选骨架（自家产品 / 竞品）、定一级分支和状态徽标。

资料拿不到时（比如文件在受保护目录里读不了），先找同主题的其他来源，并在最后明确告诉用户依据换成了什么。

### 2. 找图

读 `references/image-sourcing.md`，按顺序：盘点仓库各分支和证据目录里的图 → 用 `scripts/capture_server.py`、`scripts/shoot.py` 从原型补截缺的状态 → 竞品从官网、评测、帮助文档找。全部放进草稿目录，用 `scripts/contact_sheet.py` 拼对照表一次看完，按画面内容（不是文件名）给每个节点挑图。

素材多、来源分散时（比如十几个竞品），可以按产品组派几个子 agent 并行找图，每个 agent 把图和来源清单放进各自的空目录。

### 3. 压缩素材

写 `recipe.json`，跑 `scripts/build_assets.py`：截图压成 WebP，多张并排拼图，帧序列拼 GIF，需要突出局部时裁图。整套控制在 10 MB 左右。

### 4. 写 data.json

按 `references/data-schema.md` 填 `meta`、`assets`、`tree`。一张图里只有一小块是重点时，给素材加 `focus` 细节框（或给节点加 `z`），大图会自动放大到那里。

### 5. 生成与自检

```bash
python3 scripts/build_page.py data.json -o site/index.html --strict
python3 scripts/check_page.py site/index.html --shots <草稿目录>
```

看一眼 `check_desktop.png` / `check_phone.png`，修一轮后发布。交互细节和发布方式见 `references/page-and-publish.md`。

### 6. 交付

- 发布 Artifact（素材用 `files` 一起发），或把 `site/` 交给用户。
- 页面、素材和三份配置提交进项目仓库；推送前按项目规则询问。
- 回复用户时说清：覆盖了哪几支、图从哪里来、哪些节点用的是替代图、哪些内容仍未验证。

## 依赖

- Python 3.9+、Pillow（素材与对照表）。
- Playwright（`shoot.py`、`check_page.py`）：优先用系统 Chrome；没有时 `python3 -m playwright install chromium`。
- 缺 Playwright 时：截图改用浏览器面板手动截，自检改为在浏览器里打开页面目测。流程不中断。
