# designs — 设计素材

## 目录结构

```
designs/
├── icons/                       ← 小程序 / App 图标候选（1024×1024）
│   ├── answer-beyond/           ← “答案之外”图标方向（512×512）
│   ├── icon-01-minimal-flat.png
│   ├── icon-02-signature-neon.png
│   ├── icon-03-soft-gradient.png
│   ├── icon-04-sound-ripple.png
│   └── icon-05-geometric-badge.png
├── wireframes/                  ← 线框图
│   ├── all-pages.png
│   └── index.html               ← 线框图浏览页
├── high-fidelity/               ← 当前高保真设计稿（安静夜间霓虹）
│   ├── index.html               ← 高保真浏览页
│   ├── flow-overview.png        ← 6 个页面流程总览
│   ├── render-previews.py       ← 手机预览导出脚本
│   └── previews/                ← 1170×2532 手机预览图
├── source/                      ← 历史高保真生成脚本，不代表当前实现
│   ├── render-previews.py
│   ├── render-previews.sh
│   └── index.html               ← 预览浏览页
├── neon-night-assumption-review.md  ← 霓虹夜色设计假设评审
└── README.md                    ← 本文件
```

## 说明

- `icons/answer-beyond/` 中为本轮“答案之外”品牌图标，均为 512×512 PNG
- `icons/` 根目录中的其他待选品牌图标为 1024×1024 PNG；确认最终方向前不作为正式发布图标
- 旧高保真预览已经与实际产品定位和页面流程不一致，相关导出图已移除
- 当前页面结构以 `wireframes/` 为准；当前高保真实现位于 `high-fidelity/`，采用“安静夜间霓虹”方向
- 各页面交互状态详见 PRD 第 7.2 节
