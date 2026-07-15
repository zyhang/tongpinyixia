# designs — 设计素材

## 目录结构

```
designs/
├── icons/
│   └── answer-beyond/           ← “答案之外”小程序图标方向（512×512）
├── wireframes/                  ← 当前 MVP 线框图
│   ├── all-pages.png
│   └── index.html               ← 线框图浏览页
├── source/                      ← 历史高保真生成脚本，不代表当前实现
│   ├── render-previews.py
│   ├── render-previews.sh
│   └── index.html               ← 历史预览浏览页
├── neon-night-assumption-review.md  ← 历史设计假设评审
└── README.md                    ← 本文件
```

## 说明

- `icons/answer-beyond/` 中为本轮“答案之外”品牌图标，均为 512×512 PNG
- 旧高保真预览已经与实际产品定位和页面流程不一致，相关导出图已移除
- 当前页面结构以 `wireframes/` 为准；新的高保真设计应在实际实现约束确认后重新制作
- 各页面交互状态详见 PRD 第 7.2 节
