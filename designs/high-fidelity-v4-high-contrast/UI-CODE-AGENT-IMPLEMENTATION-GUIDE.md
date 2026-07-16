# 答案之外｜高对比高保真 UI 代码生成指引

> 用途：本文件是交给 Code Agent 直接执行 UI 开发的实施合同，不是泛化设计说明。
>
> 目标平台：抖音小程序，默认采用原生 `TTML + TTSS + JavaScript + JSON`。
>
> 规范核对日期：2026-07-16。抖音开放平台规则会更新，首次提审前须重新核对本文末尾的官方链接。

## 0. Code Agent 开始执行

Code Agent 收到本文件后，按以下顺序工作：

1. 先完整阅读：
   - 本文件。
   - `../../docs/产品理念与MVP设计准则.md`。
   - `../../docs/答案之外-品牌文案规范.md`。
   - `index.html`，以其页面状态、文案和视觉层级为高保真来源。
   - `flow-overview.png` 与 `previews/` 下 9 张页面图。
2. 检查仓库是否已经存在抖音小程序源码、构建方式和状态管理方案。
3. 若已有小程序工程：保持现有框架、目录、命名、请求层和构建链，只实现本指引范围内的 UI。
4. 若不存在小程序工程：在仓库根目录创建 `miniprogram/` 原生抖音小程序工程，使用下文给定的目录结构。
5. 先完成静态页面与本地 mock 状态，再接入现有接口；不得为完成 UI 擅自设计后端接口或伪造线上数据。
6. 使用抖音开发者工具检查，随后至少在一台 iOS 和一台 Android 真机验证。
7. 交付前逐条执行第 14 节验收清单，并报告真实测试结果。

严禁：

- 不得把高保真 PNG 整张铺成背景图。
- 不得用 WebView/H5 套壳代替原生小程序组件。
- 不得重新实现抖音 App 顶部 Tab、搜索、关闭胶囊或底部“首页/朋友/消息/我”导航。
- 不得新增分享、关注、匹配、私信、用户主页、历史理由、撤回等 MVP 外能力。
- 不得把示例比例、人数和理由硬编码成真实线上数据。
- 不得为了适配短屏而整体缩放页面或把正文缩到不可读。

## 1. 实现范围

### 1.1 必须实现的 9 个视觉状态

| 编号 | 页面/状态 | 高保真参考 | 实现位置 |
| --- | --- | --- | --- |
| 01 | 今日一问 | `previews/01-today-question.png` | `pages/index` 的 `question` 状态 |
| 02 | 选择结果＋理由 | `previews/02-result-and-reason.png` | `pages/index` 的 `result` 状态 |
| 02B | 理由反馈完成 | `previews/02b-reason-reacted.png` | `pages/index` 的 `result-reacted` 状态 |
| 03A | 理由输入空态 | `previews/03a-posting-empty.png` | `pages/posting` 的 `empty` 状态 |
| 03B | 理由可提交态 | `previews/03b-posting-ready.png` | `pages/posting` 的 `editing` 状态 |
| 04 | 理由发送成功 | `previews/04-posting-success.png` | `pages/posting` 的 `success` 状态 |
| 05A | 样本不足 | `previews/05a-sample-insufficient.png` | `pages/index` 的 `sample-insufficient` 状态 |
| 05B | 理由不足 | `previews/05b-reason-insufficient.png` | `pages/index` 的 `reason-insufficient` 状态 |
| 05C | 加载失败 | `previews/05c-load-failed.png` | `pages/index` 的 `load-failed` 状态 |

### 1.2 不实现的内容

- 高保真图里的系统状态栏。
- 抖音宿主顶部“同城/关注/商城/推荐”、搜索和关闭图标。
- 抖音宿主底部导航。
- 设计浏览器的 gallery 页面。
- 外部分享、保存图片、社交关系和个人内容记录。

这些元素只用于说明页面在真实抖音环境中的最终观感。

## 2. 推荐工程结构

若仓库中没有既有实现，创建：

```text
miniprogram/
├── app.js
├── app.json
├── app.ttss
├── pages/
│   ├── index/
│   │   ├── index.ttml
│   │   ├── index.ttss
│   │   ├── index.js
│   │   └── index.json
│   └── posting/
│       ├── posting.ttml
│       ├── posting.ttss
│       ├── posting.js
│       └── posting.json
├── components/
│   ├── brand-header/
│   ├── question-poster/
│   ├── choice-button/
│   ├── result-summary/
│   ├── reason-card/
│   ├── action-button/
│   └── state-poster/
├── services/
│   └── answer-beyond.js
├── styles/
│   ├── tokens.ttss
│   └── utilities.ttss
└── utils/
    └── layout.js
```

约束：

- 不为只有一次使用的小块强行拆组件。
- `question-poster`、`choice-button`、`reason-card`、`action-button` 必须组件化，因为它们有独立状态或重复使用。
- 业务请求统一从 `services/answer-beyond.js` 暴露，不在组件内直接调用 `tt.request`。
- 页面负责状态编排，组件只接收数据并发出事件。

## 3. 抖音小程序容器规范

### 3.1 默认使用标准导航栏

首版优先使用平台标准导航栏：

```json
{
  "navigationBarBackgroundColor": "#06070B",
  "navigationBarTextStyle": "white",
  "navigationBarTitleText": "答案之外",
  "navigationStyle": "default"
}
```

原因：`navigationStyle: custom` 不是纯代码开关，需要先在抖音开放平台申请自定义页面结构能力。未确认权限前不得设置为 `custom`，否则可能阻碍代码包上传或提审。

### 3.2 获得自定义页面结构权限后的处理

仅当控制台已确认能力通过，才允许：

```json
{
  "navigationStyle": "custom"
}
```

随后在页面 `onReady` 或更晚时读取：

```js
const systemInfo = tt.getSystemInfoSync(false);
const customButtonRect = tt.getCustomButtonBoundingClientRect();

this.setData({
  layout: {
    windowWidth: systemInfo.windowWidth,
    windowHeight: systemInfo.windowHeight,
    statusBarHeight: systemInfo.statusBarHeight,
    safeArea: systemInfo.safeArea,
    leftIcon: customButtonRect.leftIcon,
    capsule: customButtonRect.capsule,
    customNavigation: customButtonRect.customNavigation,
  },
});
```

实现要求：

- 左侧小程序 logo/返回按钮和右侧平台胶囊由平台统一下发，不得重画。
- 业务标题必须位于 `customNavigation` 可绘制范围内。
- 标题与平台胶囊中线对齐，并保留安全间距。
- 平台胶囊层级始终最高，业务内容不得遮挡。
- 首页由平台展示 logo；子页由平台展示返回按钮。
- 投稿页若作为独立路由，删除高保真图中业务区的重复返回箭头，只保留标题“写下答案之外”。
- 如果产品坚持保留业务区返回箭头，则投稿必须继续作为首页内部状态，不得同时出现平台返回按钮。

### 3.3 页面方向和宿主差异

- 小程序只按竖屏实现，不为横屏做版式。
- 使用 `tt.getSystemInfoSync(false)` 获取实际 `windowWidth`、`windowHeight`、`safeArea`、`pixelRatio`、`SDKVersion` 和 `platform`。
- 不用 UA、机型名称或 iPhone 型号判断布局。
- iOS/Android 只允许做兼容差异，不允许做两套视觉风格。
- 对需要新基础库能力的 API 做 `SDKVersion` 检查和降级，不能假设开发者工具可用就代表真机可用。

## 4. 尺寸适配策略

### 4.1 设计基准

- 高保真逻辑尺寸：`390 × 844 px`。
- 导出图尺寸：`1170 × 2532 px`，即 3 倍图，仅供视觉核对。
- 实现时以逻辑尺寸和比例为准，不使用导出图物理像素。
- 水平尺寸优先使用 `rpx` 或百分比；字体、1px 细线和平台安全区计算使用逻辑 `px`。

### 4.2 主流测试尺寸

| 优先级 | 逻辑视口 | 代表场景 | 要求 |
| --- | --- | --- | --- |
| P0 | `375 × 812` | 主流 iPhone 刘海屏 | 全流程无裁切，无非预期滚动 |
| P0 | `390 × 844/852` | 当前设计基准、主流 iPhone | 与高保真最接近 |
| P0 | `360 × 800` | 主流 Android | 题目、选项、主按钮完整可见 |
| P1 | `393 × 873` | 主流 Android/大屏 iPhone | 内容不被无意义拉散 |
| P1 | `412 × 915` | 主流 Android 大屏 | 业务内容居中，宽度不无限放大 |
| P1 | `430 × 932` | 大屏 iPhone | 保持卡片最大宽度和阅读行长 |
| P2 | `320 × 568` | 旧款/小众短屏 | 允许纵向滚动，功能必须可完成 |

不需要专门为折叠屏展开态、横屏、平板和极小安卓机做精细视觉还原；这些尺寸只要求不崩溃、可阅读、可完成主流程。

### 4.3 响应式规则

1. 页面根节点使用纵向 Flex：头部、内容、底部操作区。
2. 业务内容宽度默认 `100%`，左右安全边距：
   - 视口 `<= 360px`：`16px`。
   - `361–399px`：`18px`。
   - `>= 400px`：`20px`，内容最大宽度 `390px` 并水平居中。
3. 高度适配不使用整页 `transform: scale()`。
4. 可用高度 `>= 760px`：保持高保真布局，主操作区贴近业务区底部。
5. 可用高度 `700–759px`：压缩非必要垂直间距 10%–20%，品牌副标题可以隐藏。
6. 可用高度 `< 700px`：页面改为自然纵向滚动，主按钮跟随内容；不得用固定定位盖住理由或输入框。
7. 题目、理由和错误文案均按真实长度撑高，不写死文本容器高度。
8. 卡片视觉宽度不得超过 `390px`，避免在大屏设备上产生过长行宽。
9. 底部安全留白按 `Math.max(0, windowHeight - safeArea.bottom)` 计算；若 TTSS 环境已验证支持，也可使用 `env(safe-area-inset-bottom)`。不得把 `safeArea.bottom` 坐标直接当作留白值，也不得写死 Home Indicator 高度。

### 4.4 建议尺寸换算

以 `390px` 设计基准换算时，可使用：

```text
rpx ≈ 设计 px × 750 / 390
```

常用值：

| 设计值 | 建议实现值 |
| --- | --- |
| `10px` | `20rpx` |
| `12px` | `24rpx` |
| `16px` | `31rpx` |
| `18px` | `35rpx` |
| `20px` | `38rpx` |
| `22px` | `42rpx` |
| `48px` | `92rpx` |
| `68px` | `131rpx` |

这是实现起点，不是逐像素强制表。文字建议优先使用逻辑 `px`，并用真机视觉校准；1px 边框必须保持 `1px`。

## 5. 设计 Token

### 5.1 色彩

```text
page.background        #06070B
page.backgroundBlack   #000000
surface.paper          #F4EFE7
surface.dark           rgba(255,255,255,0.07)
text.onDark.primary    #FFFDF8
text.onDark.secondary  #A5A7AF
text.onLight.primary   #101116
text.onLight.secondary #69665F
accent.pink            #FF5F91
accent.cyan            #52E1D2
accent.yellow          #FFE36E
border.onDark          rgba(255,255,255,0.16)
disabled.background    #24252B
disabled.text          #777880
```

规则：

- 黄色只用于单页最主要动作和栏目标签，不同时出现两个黄色主按钮。
- 粉色与青色分别承担 A/B 等权选择，不用颜色表达“正确/错误”。
- 米白色纸张用于问题、结果和状态总结；匿名理由卡使用深色，不把所有内容都塞进白卡。
- 正文对比度按项目标准至少达到 WCAG AA：普通文字 `4.5:1`，大号文字 `3:1`。
- 不使用持续闪烁、呼吸光、放大循环等诱导点击效果。

### 5.2 字体

- 使用系统中文字体栈，不打包自定义中文字体：`PingFang SC` / 系统默认 sans-serif。
- 字重只使用 Regular、Semibold/Bold、Heavy 三层。
- 最小可见字号 `10px`；正文和说明优先不低于 `12px`。
- 主问题标题：基准 `34px / 1.22 / Heavy`；`360px` 宽度下降为 `30px`，不得小于 `28px`。
- 页面标题：`21–24px / 1.35 / Heavy`。
- 选项正文：`17px / 1.35 / Bold`。
- 理由正文：`16px / 1.52 / Semibold`。
- 按钮文字：`14–16px / Bold`。
- 辅助说明：`10–12px / 1.5 / Regular`。
- 数字比例：`64–66px / 0.9 / Heavy`，百分号 `22px`。

动态字体增大场景：允许文本容器增高和页面滚动，不截断核心题目、答案、理由和按钮文案。

### 5.3 圆角、间距与阴影

- 页面栅格基数：`4px`。
- 页面水平边距：`16/18/20px`。
- 大纸张卡片圆角：`22px`。
- 选项圆角：`17px`。
- 主按钮圆角：`15px`。
- 小胶囊圆角：`999px`。
- 同组间距：`8–12px`；模块间距：`16–24px`。
- 阴影只用于米白纸张和主要选择块，不给每个元素加阴影。
- Android 阴影若表现不一致，优先保留边界、层级和色差，允许降低阴影精度。

## 6. 组件合同

### 6.1 `brand-header`

输入：

```js
{
  title: "答案之外",
  badge: "匿名",
  subtitle: "选择之后，听见真实的想法"
}
```

要求：短屏可以隐藏 `subtitle`，不得隐藏产品名和匿名标识。高保真中的“AI生成”若由宿主平台提供则不实现；若产品合规明确要求业务自行展示，才通过配置开启。

### 6.2 `question-poster`

输入：

```js
{
  questionId,
  label: "今日一问",
  guide: "如果是你，会怎么选？",
  questionText,
  emphasisText,
  empathyText
}
```

要求：

- `emphasisText` 只加粉色划线，不改变语义。
- 找不到精确子串时不渲染划线，不拆坏中文文本。
- 问题最多建议 3–4 行；超长时允许卡片增高，不使用省略号。
- 作答前严禁显示人数、比例或他人选择。

### 6.3 `choice-button`

属性：`option=A|B`、`label`、`disabled`、`loading`。

事件：`bindselect`，返回 `{ option, questionId }`。

状态必须完整：

- 普通：A 粉色、B 青色。
- 按下：`transform: scale(0.975)`，持续 `120–160ms`。
- 提交中：两项锁定，只在已点选项显示轻量加载反馈。
- 禁用：不得只通过透明度区分，文字和背景同时降级。
- 失败回滚：恢复可点击，并显示非阻断错误提示。

触摸区域不小于项目标准 `44 × 44px`；当前选项高度目标 `68px`。

### 6.4 `result-summary`

输入：`selectedOption`、`selectedLabel`、`ratio`、`sampleCount`、`sampleState`。

规则：

- 比例必须来自服务端结果。
- `sampleState !== "ready"` 时不得显示模拟百分比，直接进入样本不足状态。
- `sampleCount` 仅在数据口径满足展示条件时显示。
- 文案保持“你选择了…… / 有 xx% 的作答者，和你选了一样 / 基于 xx 次作答”。

### 6.5 `reason-card`

输入：`reason`、`reacted`、`reactionCount`、`switching`。

事件：`bindreact`、`bindnext`。

规则：

- 理由卡顶部只显示来源标签“一个同样选择的人，留了这句话”，正文下方不得再次显示来源说明。
- 来源标签与理由正文间距目标 `14px`；理由正文与操作区间距目标 `20px`；反馈人数与操作区间距目标 `9px`。
- 默认不显示共鸣人数。
- 用户点击“这句话说中了我”后，按钮变为“原来你也这样想”，再显示人数。
- 已反馈按钮使用低饱和青色背景和青色文字表达完成状态，不使用整块高饱和填充，不得与页面主按钮争夺层级。
- 反馈不可取消。
- “再看一种想法”只替换理由卡，不刷新结果比例、不改变已选答案。
- 切换时基线动画只做 `opacity` 过渡；`filter: blur()` 仅作为确认兼容后的渐进增强。
- 连续点击期间锁定请求，避免理由乱序。
- 理由不足进入专用状态，不用 AI 或模板文案填充真人理由。

### 6.6 `action-button`

类型：`primary`、`secondary`。

必须包含：普通、按下、加载、禁用四种状态。一个页面只能有一个 `primary`。

按钮默认不得依赖 hover；只实现触摸反馈。不要使用 `transition: all`。

### 6.7 `state-poster`

属性：`type`、`title`、`description`、`actionLabel`。

支持：`sample-insufficient`、`reason-insufficient`、`load-failed`、`posting-success`。

状态卡可使用一次性 `opacity + scale(.95 → 1)` 入场，时长 `180–220ms`；不得循环动画。

## 7. 页面状态机

### 7.1 首页

```text
loading-question
  ├─ success → question
  └─ failure → load-failed

question
  └─ choose A/B → submitting-choice

submitting-choice
  ├─ sample ready + reason ready → result
  ├─ sample insufficient → sample-insufficient
  ├─ reason insufficient → reason-insufficient
  └─ failure → question + non-blocking error

result
  ├─ react reason → reacting → result-reacted
  ├─ next reason → switching-reason → result
  ├─ next question → loading-question
  └─ write reason → pages/posting
```

### 7.2 投稿页

```text
empty
  └─ input → editing

editing
  ├─ clear → empty
  └─ submit → checking-content

checking-content
  ├─ accepted → success
  ├─ rejected → editing + 友好提示
  └─ failure → editing + 可重试提示

success
  ├─ next question → 返回首页并加载下一题
  └─ finish → 调用 tt.exitMiniProgram 退出当前小程序到后台
```

用户可输入文字必须接入现有内容安全检测链路。UI 不展示“审核/授权/风控”等平台术语；被拒绝时使用类似“这句话还不能飘出去，换一种说法试试。”的低负担提示。不得在客户端放置内容安全密钥。

## 8. 数据与服务层合同

若现有服务层命名不同，适配现有命名，但必须提供等价能力：

```js
export async function fetchQuestion() {}
export async function submitChoice({ questionId, option, requestId }) {}
export async function fetchNextReason({ questionId, option, excludeReasonIds }) {}
export async function reactToReason({ reasonId, requestId }) {}
export async function submitReason({ questionId, option, content, requestId }) {}
```

要求：

- 每次写操作都携带客户端 `requestId`，服务端应支持幂等。
- 选项提交、理由反馈、理由投稿均防重复点击。
- 页面卸载后不得继续 `setData`。
- 接口失败不能清空用户已输入的理由。
- 页面只展示接口明确返回的数据口径；不知道是否真实时不展示人数和百分比。
- mock 数据只能存在开发环境，并明显标注 `mock`；生产构建不得默认回退 mock。

## 9. 原生组件注意事项

### 9.1 `textarea`

- 使用原生 `<textarea maxlength="60">`。
- `textarea` 是半受控组件，不根据页面 data 推断真实焦点和选区状态。
- 提交建议使用 `<form bindsubmit>`，避免 `textarea` 的 `blur` 晚于按钮 `tap` 导致读取旧值。
- 少部分 Android 机型出现 fixed 异常时，根据官方建议为组件增加 `fixed` 属性；不要默认把输入框放在 fixed 容器。
- 键盘弹出时主按钮必须仍可访问；必要时让页面滚动，不把按钮覆盖在输入框上。
- 字数计数使用 `e.detail.value.length`，并以服务端最终校验为准。

### 9.2 `scroll-view`

- 仅在确实需要独立滚动区域时使用；普通短页面优先页面自然滚动。
- 竖向 `scroll-view` 必须设置明确高度。
- 不使用 `vh/vw` 设置包含原生组件的 `scroll-view` 宽高，避免部分 Android 同层渲染异常。
- 如需动态追加子项，为所有子元素增加一层 `<view>` 包裹，规避旧 iOS 滚动位置回顶问题。

### 9.3 层级

- 原生 `textarea`、`input` 可能涉及同层渲染差异。
- 不在输入框上方叠放装饰性按钮、Toast 或不可关闭浮层。
- 所有弹层必须有明确关闭方式；本 MVP 原则上不需要业务弹窗。

## 10. 动效与反馈

- 高频点击只使用 `120–160ms` 按下缩放反馈。
- 状态卡首次出现可以使用 `180–220ms` 的 `opacity + scale(.95)`。
- 理由切换使用 `160ms` 淡出，再替换文本并淡入。
- UI 动画只操作 `transform` 与 `opacity`；颜色变化使用短 transition。
- 不从 `scale(0)` 入场。
- 不使用 `ease-in`；默认使用强 ease-out：`cubic-bezier(.23, 1, .32, 1)`。
- 不使用 `transition: all`。
- 不阻塞交互等待装饰动画完成。
- 系统或基础库无法支持动效时，直接无动画切换，不影响功能。

## 11. 可访问性与易用性

- 可点击区域项目下限 `44 × 44px`。
- 只靠颜色无法判断状态：A/B 同时保留字母和文本；反馈完成同时显示图标与文案。
- 所有可交互组件提供清晰的可访问文本。
- 正文不小于 `12px`；只有极低层级辅助信息可用 `10px`。
- 题目、理由和错误信息不允许截断。
- 提交中必须有可感知状态，并防止重复操作。
- 网络失败后提供明确重试，不让用户猜测选择是否成功。
- 动态字体导致内容增高时允许页面滚动。
- 不使用自动播放声音、振动或闪烁提示。

## 12. 文案与产品边界

实现时必须原样遵守品牌文案规范，尤其是：

- 产品名：“答案之外”。
- 副标题：“选择之后，听见真实的想法”。
- 首页标签：“今日一问”。
- 作答提示：“没有标准答案，只选此刻更像你的那个。”
- 理由来源标签：“一个同样选择的人，留了这句话”。理由正文下方不重复来源文案。
- 理由反馈：“这句话说中了我” → “原来你也这样想”。
- 下一条理由：“再看一种想法”。
- 投稿按钮：“让这句话飘进答案之外”。
- 成功标题：“好啦，这句话飘出去了”。
- 主操作：“再看一道题”。

禁止出现：

- “匹配成功”“正在寻找同频的人”“有人正在等你”。
- “关注他”“认识一下”“私信”“好友”。
- “我的理由”“历史记录”“撤回”。
- 作答前人数和比例。
- 把预设理由冒充真人理由的说明。
- 用户界面的“审核、授权、提交工单”等平台术语。

## 13. 实现步骤与提交边界

Code Agent 应按以下批次实现，每批都可独立验证：

### 批次 A：壳层与 Token

- 工程配置、标准导航栏、页面背景、安全区。
- Token、公共按钮、品牌头部。
- 主流尺寸空页面截图验证。

### 批次 B：首页主循环

- 今日一问、A/B 选择、选择提交锁。
- 结果总结、理由卡、下一题。
- 样本不足、理由不足、加载失败。

### 批次 C：理由交互

- “这句话说中了我”的一次性反馈。
- “再看一种想法”的局部切换和并发保护。

### 批次 D：理由投稿

- 独立投稿页、60 字输入、禁用/可提交状态。
- 内容安全检查状态、错误保留输入、成功页。

### 批次 E：真机适配

- P0/P1 尺寸矩阵。
- iOS/Android 键盘、输入框、返回行为。
- 标准导航与自定义导航权限分支。

不要把上述批次压成一次大改；每批完成后先看真实 diff 和运行结果。

## 14. 验收清单

### 14.1 视觉

- [ ] `390 × 844` 与高保真稿主要布局一致。
- [ ] `360 × 800`、`375 × 812`、`412 × 915` 无横向溢出。
- [ ] 大屏卡片宽度受限，不被拉得过宽。
- [ ] 短屏允许滚动，题目、选项、理由和主按钮均可访问。
- [ ] A/B 视觉等权，没有默认选中暗示。
- [ ] 每页只有一个黄色主操作。
- [ ] 所有文字可读，最低字号和对比度达标。

### 14.2 宿主规范

- [ ] 未重复实现抖音顶部导航、胶囊和底部导航。
- [ ] 未获权限时使用 `navigationStyle: default`。
- [ ] 自定义导航权限存在时，使用真实胶囊位置计算布局。
- [ ] 业务内容不遮挡平台 logo/返回和胶囊。
- [ ] 子页面没有双返回按钮。
- [ ] 不模仿系统通知、警告或抖音原生按钮诱导点击。

### 14.3 交互

- [ ] A/B 选择只能成功提交一次。
- [ ] 结果、比例和理由在同一页连续出现。
- [ ] 理由反馈前不展示共鸣人数。
- [ ] 理由反馈完成后不可取消。
- [ ] 换理由不刷新比例、不改变选择。
- [ ] 理由投稿为空时按钮禁用。
- [ ] 投稿失败保留输入内容。
- [ ] 投稿成功后“再看一道题”为主操作。
- [ ] 接口失败存在明确可重试路径。

### 14.4 数据与合规

- [ ] 生产环境不回退 mock 比例、人数和理由。
- [ ] 用户输入接入现有内容安全检测链路。
- [ ] 客户端不包含密钥或内容安全服务凭据。
- [ ] 没有新增 MVP 外的分享、社交和个人记录入口。
- [ ] 所有接口状态都有 loading/success/error 处理。

### 14.5 测试证据

交付报告必须附：

- 抖音开发者工具编译结果。
- P0 三个尺寸的首页、结果页、投稿页截图。
- iOS 和 Android 真机验证结果。
- 完整流程：选答案 → 看结果与理由 → 理由反馈 → 换理由 → 写理由 → 成功 → 下一题。
- 异常流程：样本不足、理由不足、加载失败、投稿失败。
- 未完成项和真实阻塞，不得伪造通过结果。

## 15. 高保真与平台规范冲突时的优先级

优先级从高到低：

1. 抖音开放平台强制规范、审核与安全要求。
2. `../../docs/产品理念与MVP设计准则.md`。
3. `../../docs/答案之外-品牌文案规范.md`。
4. 本文件的交互和组件合同。
5. `index.html` 与 `previews/` 的视觉像素还原。

典型冲突处理：

- 高保真画了抖音宿主导航 → 不实现。
- 高保真投稿页画了返回箭头，但平台已下发返回按钮 → 删除业务箭头。
- 短屏无法保持所有元素同屏 → 允许滚动，不缩小核心文字。
- 阴影在 Android 表现不一致 → 保留层级和边界，降低阴影精度。
- 自定义导航尚未获批 → 使用标准导航，不阻塞 UI 主流程。

## 16. 官方规范依据

以下链接是本指引使用的一手依据：

- [自定义导航最佳实践](https://developer.open-douyin.com/docs/resource/zh-CN/mini-app/design/design-specification/visual-specification/custom-nav-practices)
- [自定义页面结构](https://developer.open-douyin.com/docs/resource/zh-CN/mini-app/open-capacity/basic-capacities/custom-page-structure/)
- [小程序配置](https://developer.open-douyin.com/docs/resource/zh-CN/mini-app/develop/framework/general-configuration)
- [tt.getCustomButtonBoundingClientRect](https://developer.open-douyin.com/docs/resource/zh-CN/mini-app/develop/api/interface/menu/tt-get-custom-button-bounding-client-rect)
- [tt.getSystemInfoSync](https://developer.open-douyin.com/docs/resource/zh-CN/mini-app/develop/api/device/system-information/tt-get-system-info-sync/)
- [tt.exitMiniProgram](https://developer.open-douyin.com/docs/resource/zh-CN/mini-app/develop/api/foundation/lifecycle/tt-exit-mini-program)
- [通用控件](https://developer.open-douyin.com/docs/resource/zh-CN/mini-app/design/design-specification/visual-specification/Common-Control)
- [基础规范](https://developer.open-douyin.com/docs/resource/zh-CN/mini-app/design/design-specification/visual-specification/Basic-Specifications)
- [组件概述](https://developer.open-douyin.com/docs/resource/zh-CN/mini-app/develop/component/overview/)
- [scroll-view](https://developer.open-douyin.com/docs/resource/zh-CN/mini-app/develop/component/view-container/scroll-view)
- [textarea](https://developer.open-douyin.com/docs/resource/zh-CN/mini-app/develop/component/list/textarea)
- [小程序运营规范](https://developer.open-douyin.com/docs/resource/zh-CN/mini-app/operation/management/specification/standard)

## 17. Code Agent 最终回报格式

完成后按以下格式回复：

```markdown
实现结果：完成 / 部分完成 / 阻塞

已完成：
- ...

文件：
- ...

验证：
- 开发者工具：...
- iOS：...
- Android：...
- 尺寸矩阵：...
- 主流程：...
- 异常流程：...

与高保真差异：
- 差异：...
- 原因：平台规范 / 兼容性 / 产品约束 / 尚未完成

未完成或阻塞：
- ...
```
