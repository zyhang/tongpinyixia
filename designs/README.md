# designs — 设计素材

## 目录结构

```
designs/
├── previews/                    ← 各视觉方向的 7 页面预览
│   ├── warm-handwritten/        ← "温暖手写"（MVP 默认评审基线）
│   ├── quiet-editorial/         ← "安静编辑部"
│   ├── light-lab/               ← "轻实验装置"
│   ├── soft-digital/            ← "柔和数字原生"
│   ├── neon-night/              ← "霓虹夜色" v1
│   └── neon-night-v2/           ← "霓虹夜色" v2
├── wireframes/                  ← 线框图
│   ├── all-pages.png
│   └── index.html               ← 线框图浏览页
├── source/                      ← 设计源脚本
│   ├── render-previews.py
│   ├── render-previews.sh
│   └── index.html               ← 预览浏览页
├── style-directions.png         ← 四套视觉方向总览
├── echo-flow-neon.png           ← 用户流程图（霓虹风格）
├── neon-night-v2-flow.png       ← 用户流程图 v2
├── neon-night-assumption-review.md  ← 霓虹夜色设计假设评审
└── README.md                    ← 本文件
```

## 说明

- 每套方向下 7 张预览对应 7 个核心页面：01(问题) → 02(结果) → 03(理由) → 04(空白回声) → 05(编辑回声) → 06(生成回声) → 07(分享卡)
- 各页面交互状态详见 PRD 第 7.2 节
- 当前 MVP 以 `warm-handwritten` 方向为默认评审基线
