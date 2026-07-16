# designs — 设计素材

## 目录结构

```
designs/
├── icons/                       ← 小程序 / App 正式图标与历史候选
│   ├── answer-beyond-app-icon.png  ← “答案之外”正式图标（1024×1024）
│   └── archive/                 ← 已归档的历史候选
│       ├── legacy-wave/
│       └── answer-beyond-concepts/
├── wireframes/                  ← 线框图
│   ├── all-pages.png
│   └── index.html               ← 线框图浏览页
├── high-fidelity/               ← 当前高保真设计稿（安静夜间霓虹）
│   ├── index.html               ← 高保真浏览页
│   ├── flow-overview.png        ← 6 个页面流程总览
│   ├── render-previews.py       ← 手机预览导出脚本
│   └── previews/                ← 1170×2532 手机预览图
├── high-fidelity-v4-high-contrast/ ← 高对比编辑海报完整候选稿
│   ├── index.html               ← 9 个页面状态的可交互浏览页
│   ├── flow-overview.png        ← 完整页面流程总览
│   ├── UI-CODE-AGENT-IMPLEMENTATION-GUIDE.md ← 可直接交给 Code Agent 的 UI 开发指引
│   ├── render-previews.py       ← 手机预览导出脚本
│   └── previews/                ← 9 张 1170×2532 手机预览图
├── homepage-high-contrast/      ← 高对比首页的前期单页概念稿
├── source/                      ← 历史高保真生成脚本，不代表当前实现
│   ├── render-previews.py
│   ├── render-previews.sh
│   └── index.html               ← 预览浏览页
├── neon-night-assumption-review.md  ← 霓虹夜色设计假设评审
└── README.md                    ← 本文件
```

## 说明

- `icons/answer-beyond-app-icon.png` 为当前唯一正式品牌图标，采用与高保真设计一致的深墨蓝、青色与粉色
- `icons/archive/` 仅保存历史候选，不作为正式发布资源
- 旧高保真预览已经与实际产品定位和页面流程不一致，相关导出图已移除
- 当前页面结构以 `wireframes/` 为准；当前高保真实现位于 `high-fidelity/`，采用“安静夜间霓虹”方向
- `high-fidelity-v4-high-contrast/` 为“高对比编辑海报”完整候选方向，在不改变 MVP 主流程的前提下覆盖正常流程、投稿流程和异常状态
- 各页面交互状态详见 PRD 第 7.2 节
