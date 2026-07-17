# 答案之外｜动效与音效 Code Agent 实施规范

> 用途：本文件交给已经完成静态 UI 开发的 Coding Agent，作为动效和音效实现合同。
>
> 目标平台：抖音小程序；默认技术栈为原生 `TTML + TTSS + JavaScript + JSON`。
>
> 核对日期：2026-07-17。首次提审前仍须重新核对抖音基础库和真机表现。

## 0. Coding Agent 执行边界

开始编码前，完整阅读：

1. 本文件。
2. `UI-CODE-AGENT-IMPLEMENTATION-GUIDE.md`。
3. `../../docs/产品理念与MVP设计准则.md`。
4. `../../docs/答案之外-品牌文案规范.md`。
5. `../sounds/音效触发规范.md`。
6. `index.html`，以其中已经实现的交互节奏作为可运行参考。

本任务假设 UI、组件、接口和页面状态机已经存在。Coding Agent 必须：

- 保持现有框架、目录、组件边界、请求层、状态管理和构建方式。
- 将本文状态映射到现有组件，不重写静态 UI，不调整文案，不顺手重构。
- 动画只增强反馈；接口、导航、错误恢复不能依赖动画成功执行。
- 音频加载或播放失败时静默降级，不阻断任何业务操作。
- 先完成基础兼容实现，再做 `blur` 等渐进增强。

严禁：

- 背景音乐、循环音景或自动播放声音。
- 粒子、彩屑、爱心飞出、数字滚动、持续发光、呼吸、漂浮和弹跳。
- 使用 `transition: all`、从 `scale(0)` 入场或使用 `ease-in`。
- 用动画掩盖接口等待、延迟真实成功状态或制造“匹配成功”暗示。
- 为 A/B 使用不同的声音、时长、动效幅度或视觉权重。
- 因动画新增分享、关注、匹配、私信、记录或撤回等 MVP 外能力。

## 1. 体验目标

整套反馈的情绪顺序是：

```text
触碰 → 看见结果 → 被一句话接住 → 让一句话飘出去
```

用户应感觉页面有手感、状态清楚、变化自然，但不应产生“这是一套动画演示”的感受。

动效只有四个核心目的：

1. 确认界面收到用户操作。
2. 避免结果和状态突然出现。
3. 解释按钮或内容已经发生状态变化。
4. 在低频投稿成功节点完成情绪收束。

## 2. 全局 Motion Token

在现有全局 Token 文件中增加等价变量；若已有命名体系，沿用现有命名，不重复创建。

```css
page {
  --motion-ease-out: cubic-bezier(.23, 1, .32, 1);
  --motion-ease-in-out: cubic-bezier(.77, 0, .175, 1);

  --motion-press: 110ms;
  --motion-control: 160ms;
  --motion-feedback: 180ms;
  --motion-enter: 210ms;
  --motion-success: 360ms;

  --motion-enter-y: 10px;
  --motion-success-y: 14px;
  --motion-press-scale: .975;
  --motion-selected-scale: .98;
  --motion-enter-scale: .975;
}
```

如果 TTSS 不接受自定义 `cubic-bezier()`，降级为 `ease-out`。不得改成 `ease-in`。

属性使用规则：

| 属性 | 使用 | 说明 |
| --- | --- | --- |
| `transform` | 必须优先 | 位移和缩放不触发布局重排 |
| `opacity` | 必须优先 | 用于入场、内容替换和反馈出现 |
| `color/background-color/border-color` | 可以 | 仅用于短状态过渡 |
| `filter: blur()` | 仅渐进增强 | Android 或低端机不稳定时移除，只保留透明度 |
| `width/height/top/left/margin` | 不用于核心动画 | 避免重排和掉帧 |

## 3. 动效总表

| ID | 交互节点 | 频率 | 时长 | 位移/缩放 | 声音 | 业务成功前播放 |
| --- | --- | --- | --- | --- | --- | --- |
| M01 | 按下 A/B | 高频 | `110ms` | `.975 → .98` | `choice-tap.wav` | 可以；它只确认点击被接收 |
| M02 | 结果页进入 | 高频 | `210ms` | `translateY(10px → 0)` | 无 | 不适用 |
| M03 | 理由反馈完成 | 中频 | `160–180ms` | 人数 `translateY(4px → 0)` | `resonance-glow.wav` | 不可以；接口成功后播放 |
| M04 | 更换理由 | 中频 | `160ms + 160ms` | 无位移 | 无 | 新理由准备好后再开始 |
| M05 | 提交按钮启用 | 中频 | `160ms` | 无位移 | 无 | 不适用 |
| M06 | 投稿成功 | 低频 | `360ms` | `translateY(14px → 0)`、`.975 → 1` | `reason-float-away.wav` | 不可以；接口成功后播放 |

页面返回、“再看一道题”、进入投稿页、加载失败、样本不足、理由不足和普通导航不增加声音。

## 4. M01｜选择答案

### 4.1 触发条件

仅当以下条件同时满足时接收点击：

- 当前页面状态为 `question`。
- 选项未锁定。
- 当前题目存在有效 `questionId`。
- 用户点击 A 或 B 的有效触控区域。

首次有效点击后立即锁定 A、B 两项。后续点击、双击和多指触控全部忽略。

### 4.2 时间线

| 时间 | 视觉 | 声音 | 业务 |
| --- | --- | --- | --- |
| `t=0` | 被按选项缩放到 `.975` | 播放 `choice-tap.wav` | 记录选项、生成 `requestId`、锁定两项并立即发起请求 |
| `t=110ms` | 被按选项停在 `.98`，亮度可降至 `.90–.94` | 音效已结束 | 若请求已成功，进入结果状态；否则保持锁定等待 |
| 请求成功 | 不做第二次弹跳 | 不再播放声音 | 进入 `result-entering` |
| 请求失败 | 恢复 `scale(1)` 和原色 | 不播放错误音 | 解锁两项，显示现有非阻断错误提示 |

接口很快时，也要保留最短 `110ms` 的触碰反馈；接口较慢时，不重复或循环按压动画。

### 4.3 TTSS 基线

```css
.choice-button {
  transform: scale(1);
  transition: transform 110ms cubic-bezier(.23, 1, .32, 1),
              filter 160ms ease-out;
}

.choice-button.is-pressed {
  transform: scale(.975);
}

.choice-button.is-selected {
  transform: scale(.98);
  filter: brightness(.92);
}
```

如果 `filter` 真机兼容性不足，删除 `filter`，不得通过更大缩放补偿。

### 4.4 状态要求

```text
question.idle
  └─ tap A/B → choice.submitting
       ├─ success → result.entering
       └─ failure → question.idle + error
```

- A/B 使用完全相同的缩放、时长、缓动和音效。
- 选项提交结果只能由服务端或现有可信状态确认。
- 不播放“正确”“错误”“开奖”或第二次结果音。
- 由键盘或辅助技术触发时，允许直接进入提交状态，不强制等待按压动画。

## 5. M02｜结果页进入

### 5.1 进入顺序

结果页只做两层入场：

1. `result-summary` 先出现。
2. `reason-card` 延迟 `50ms` 出现。

比例直接展示最终值，不从 `0` 滚动到结果值。

### 5.2 参数

| 元素 | 初始状态 | 最终状态 | 时长 | 延迟 |
| --- | --- | --- | --- | --- |
| 结果卡 | `opacity: 0; translateY(10px)` | `opacity: 1; translateY(0)` | `210ms` | `0` |
| 理由卡 | `opacity: 0; translateY(10px)` | `opacity: 1; translateY(0)` | `210ms` | `50ms` |
| 比例数字 | 跟随结果卡 | 静态最终值 | 无独立动画 | 无 |
| 底部操作 | 原位展示或随页面内容出现 | 原位 | 不单独错峰 | 无 |

### 5.3 实现方式

优先使用状态类：

```css
.result-summary,
.reason-card {
  opacity: 0;
  transform: translateY(10px);
  transition: opacity 210ms cubic-bezier(.23, 1, .32, 1),
              transform 210ms cubic-bezier(.23, 1, .32, 1);
}

.reason-card {
  transition-delay: 50ms;
}

.result-page.is-entered .result-summary,
.result-page.is-entered .reason-card {
  opacity: 1;
  transform: translateY(0);
}
```

先渲染初始状态，再在下一渲染周期或约 `20ms` 后设置 `is-entered`。如果平台对状态类过渡不稳定，可用 `tt.createAnimation()` 生成等价的 `opacity + translateY` 动画数据。

业务状态在结果数据准备完成时已经是 `result`，不得等 `210ms` 动画结束后才允许用户操作。

## 6. M03｜“这句话说中了我”

### 6.1 正确顺序

```text
result.ready
  └─ tap react
       → reaction.submitting
       ├─ success → reaction.completed
       └─ failure → result.ready + error
```

点击后立即锁定该按钮并发起请求。只有接口成功后才：

1. 文案变为“原来你也这样想”。
2. 按钮进入低饱和青色完成态。
3. 共鸣人数出现。
4. 播放 `resonance-glow.wav`。

接口失败时恢复原按钮，不显示人数、不播放音效。

### 6.2 动画参数

| 元素 | 变化 | 时长 | 缓动 |
| --- | --- | --- | --- |
| 按钮边框 | 默认 → 青色低透明边框 | `160ms` | `ease-out` |
| 按钮背景 | 默认 → 青色低透明背景 | `160ms` | `ease-out` |
| 按钮文字 | 默认 → 青色完成文字 | `160ms` | `ease-out` |
| 共鸣人数 | `opacity 0 → 1` | `180ms` | 强 `ease-out` |
| 共鸣人数 | `translateY(4px → 0)` | `180ms` | 强 `ease-out` |

按钮文案变化必须发生在同一按钮容器中，避免销毁再创建导致宽度闪动。若文案宽度不同，按钮宽度保持布局既定值。

反馈不可取消，同一 `reasonId` 成功后永久锁定本次交互；重复回调、重复点击或页面恢复不得再次播放音效。

## 7. M04｜“再看一种想法”

### 7.1 数据先行

点击后先锁定请求，但保持当前理由完整可读。新理由准备完成后才启动替换动画，避免网络慢时卡片长时间空白。

```text
reason.ready
  └─ tap next → reason.loading-next
       ├─ success → reason.switching-out → swap → reason.switching-in → reason.ready
       └─ failure → reason.ready + error
```

### 7.2 时间线

| 阶段 | 正文透明度 | 模糊 | 时长 |
| --- | --- | --- | --- |
| 淡出 | `1 → .3` | `0 → 2px` | `160ms` |
| 中点 | 替换 `reasonId`、正文、反馈状态和人数 | 无动画 | 即时 |
| 淡入 | `.3 → 1` | `2px → 0` | `160ms` |

基线兼容实现只使用 `opacity`。仅在 iOS/Android 真机均稳定时增加 `blur(2px)`。

切换后：

- 已选答案和结果比例不变。
- 新理由的反馈状态按服务端数据决定，不能沿用上一条理由。
- 默认不展示新理由共鸣人数。
- 不播放声音。
- 请求期间重复点击全部忽略，响应乱序时只接受最新有效请求。

## 8. M05｜投稿按钮启用

用户输入从空白变为有效内容时，按钮从禁用态进入可用态：

- `color`、`background-color`、`opacity` 过渡 `160ms ease-out`。
- 不位移、不缩放、不播放声音。
- 输入、删除、字数变化不播放任何音效。
- 键盘弹出和收起不做装饰动画，优先保证按钮可访问。
- 内容再次变空时使用同样的 `160ms` 过渡返回禁用态。

提交中使用现有 loading 状态，不用循环发光表达等待。

## 9. M06｜投稿成功

### 9.1 触发边界

只有 `submitReason` 接口明确成功后才能进入成功状态。以下时机不得触发：

- 点击提交按钮的瞬间。
- 内容安全检查开始时。
- 网络请求发出时。
- 超时、失败、被拒绝或用户重复点击时。

成功状态必须按 `requestId` 幂等；同一成功响应最多动画一次、播放一次声音。

### 9.2 时间线

| 时间 | 视觉 | 声音 |
| --- | --- | --- |
| `t=0` | 成功卡以 `opacity:0; translateY(14px); scale(.975)` 渲染 | 开始播放 `reason-float-away.wav` |
| `t=20ms` | 设置进入态 | 音效继续 |
| `t=20–380ms` | 卡片过渡到 `opacity:1; translateY(0); scale(1)` | 760ms 音效自然收束 |
| `t≈380ms` | 页面完全静止 | 不追加任何声音或循环效果 |

参数：

- 卡片入场：`360ms`，强 `ease-out`。
- 成功标记：可同步做 `opacity:0 → 1`、`scale(.95 → 1)`，`220ms`。
- 不回弹、不超调、不旋转、不让投稿文字真的飞出屏幕。

成功页面的主按钮“再看一道题”在页面出现后立即可用，不等待动画结束。

## 10. 音效实现合同

### 10.1 素材来源

设计源文件：

```text
designs/sounds/choice-tap.wav
designs/sounds/resonance-glow.wav
designs/sounds/reason-float-away.wav
```

实现时复制到现有小程序静态资源目录，例如：

```text
miniprogram/assets/sounds/
```

生产代码不得跨目录运行时引用 `designs/`，不得使用外部热链。

### 10.2 单播放器原则

使用一个共享 `InnerAudioContext`。不要为三个音效分别创建实例。抖音官方文档说明 Android 当前只支持单个内部音频实例，多实例设置 `src` 时会以最后一次设置为准。

伪代码：

```js
const SOUND_SOURCE = {
  choice: "/assets/sounds/choice-tap.wav",
  resonance: "/assets/sounds/resonance-glow.wav",
  floatAway: "/assets/sounds/reason-float-away.wav",
};

function createUiSoundPlayer() {
  const context = tt.createInnerAudioContext();
  let currentKey = "";

  return {
    play(key) {
      const src = SOUND_SOURCE[key];
      if (!src) return;

      try {
        context.stop();
        currentKey = key;
        context.src = src;
        context.play();
      } catch (error) {
        currentKey = "";
        // 仅记录开发日志；音效失败不显示用户错误。
      }
    },

    stop() {
      try {
        context.stop();
      } catch (error) {}
      currentKey = "";
    },

    destroy() {
      this.stop();
      if (typeof context.destroy === "function") context.destroy();
    },
  };
}
```

官方说明：调用 `stop` 后需要重新播放时，应重新设置 `src` 再调用 `play`；上方伪代码已经遵守此要求。

### 10.3 生命周期

- 页面 `onLoad` 或共享服务初始化时创建一次播放器。
- 页面 `onHide`：停止当前音效，清理未完成的动效计时器。
- 页面 `onUnload`：停止并销毁播放器，清理计时器和异步回调引用。
- 小程序进入后台、页面跳转或音频焦点被其他内容占用时不续播。
- 同一时刻只允许一个 UI 音效；新音效会停止旧音效并重新设置 `src`。
- 音频失败、资源缺失或系统静音时，视觉状态照常完成。

## 11. 状态与并发控制

页面 data 至少需要等价状态；命名可适配现有代码：

```js
{
  pageState: "question" | "result" | "posting" | "success" | "error",
  choiceState: "idle" | "pressed" | "submitting",
  selectedOption: "A" | "B" | "",
  resultEntered: false,
  reactionState: "idle" | "submitting" | "completed",
  reasonState: "ready" | "loading-next" | "switching-out" | "switching-in",
  postingState: "empty" | "editing" | "submitting" | "success",
  motionEnabled: true,
}
```

实现要求：

- 所有写操作使用现有 `requestId` 幂等机制。
- 选择、反馈、换理由和投稿分别有独立锁，不能用一个全局 `loading` 互相阻塞。
- 页面卸载后不得继续 `setData`。
- 所有 `setTimeout` 句柄集中保存，在 `onHide/onUnload` 清理。
- 不用 `animationend` 决定接口成功、写入完成或页面导航；它只可用于移除临时视觉类。
- 接口响应晚于动画时，保持稳定状态，不循环动画。
- 接口响应早于最短触碰反馈时，等待 M01 的 `110ms` 后再进入结果；其他业务不为装饰动画等待。

## 12. 减少动态效果与降级

动效必须可整体关闭，但 MVP 不新增显眼的用户设置入口。

优先级：

1. 若现有运行环境能可靠读取系统“减少动态效果”偏好，则设置 `motionEnabled=false`。
2. 若平台无可靠系统能力，保留内部配置 `motionEnabled`，供兼容性、自动化和真机 QA 使用。
3. 基础库或设备不支持指定动画时直接无动画切换。

`motionEnabled=false` 时：

- 所有位移、缩放、模糊和错峰延迟关闭。
- 颜色或透明度可以保留不超过 `80ms` 的变化，也可以直接切换。
- 选择提交、理由反馈、换理由和投稿成功的功能流程不变。
- 声音开关与减少动态效果是两套独立能力；不得假设关闭动画等于关闭声音。

## 13. 性能与兼容性

- 目标为常见 iOS/Android 真机稳定接近 60fps。
- 首选 TTSS transition；它适合由状态类驱动、可被中断的 UI 变化。
- 只有状态类无法稳定表达时才使用 `tt.createAnimation()`。
- `tt.createAnimation()` 只导出当前需要的动画组，避免重复累计旧 step。
- 不在动效过程中高频 `setData`；每个阶段只做必要状态更新。
- 不为动效引入大型动画库。
- 不在原生 `textarea` 上方覆盖动画元素。
- Android 上若阴影、模糊与动画组合掉帧，优先移除模糊，其次降低阴影，不增加时长。
- 短屏滚动期间不触发装饰动画；页面布局不得因动画产生横向滚动条。

## 14. 不应有动画或声音的场景

以下状态保持安静、直接、可理解：

- 首次打开题目页。
- 输入理由、删除文字和字数变化。
- 返回、关闭、普通导航和进入投稿页。
- “再看一道题”。
- 样本不足、理由不足。
- 网络请求开始、加载失败和“再试一次”。
- 表单空内容、按钮禁用和内容安全拒绝。
- 比例数字和样本数出现。
- 小程序进入前台或页面从缓存恢复。

异常状态不得抖动、闪烁或播放警告音。

## 15. 实现顺序

Coding Agent 按以下顺序修改，每一步可独立验证：

1. 识别现有页面、组件和状态字段，列出本文 M01–M06 的映射。
2. 增加 Motion Token 和基础状态类。
3. 实现 M01，完成双击锁、最短反馈时间和失败回滚。
4. 实现 M02，验证结果页不因动画延迟交互。
5. 实现 M03/M04，验证反馈与理由 ID 严格绑定。
6. 实现 M05/M06，验证投稿失败绝不触发成功动效。
7. 接入一个共享音频播放器和三份本地资源。
8. 增加 `onHide/onUnload` 清理与 `motionEnabled=false` 降级。
9. 跑自动化、开发者工具和 iOS/Android 真机验收。

## 16. 验收用例

### 16.1 功能与幂等

- [ ] 快速双击 A 只提交一次、只播放一次 `choice-tap.wav`。
- [ ] 同时点击 A/B 只接受第一个有效选项。
- [ ] A/B 的声音、缩放、时长和亮度完全一致。
- [ ] 选项接口失败后恢复可点击，不进入结果页。
- [ ] 结果页只有两层入场，比例不滚动计数。
- [ ] 理由反馈接口成功后才显示人数、播放音效。
- [ ] 理由反馈失败不显示完成态、不播放音效。
- [ ] 同一理由反馈成功后不可取消、不可重复播放。
- [ ] 换理由网络慢时旧理由保持可读。
- [ ] 换理由失败时旧理由和反馈状态保持不变。
- [ ] 换理由后比例、选项和题目上下文不变。
- [ ] 投稿失败、超时、拒绝均不出现成功页、不播放成功音效。
- [ ] 投稿成功重复回调只执行一次成功反馈。

### 16.2 生命周期

- [ ] 动画中切后台，音效停止，回前台不自动重播。
- [ ] 页面卸载后无残留计时器、无异步 `setData` 警告。
- [ ] 连续切页时最多存在一个音频实例和一个正在播放的 UI 音效。
- [ ] 音频资源加载失败时主流程仍可完成。

### 16.3 视觉

- [ ] 选择按压不超过 `.975`，没有弹跳和超调。
- [ ] 结果卡位移 `10px`，理由卡仅延迟 `50ms`。
- [ ] 共鸣人数只上移 `4px`，没有放大或数字滚动。
- [ ] 投稿成功卡位移 `14px`、初始缩放 `.975`，不从零出现。
- [ ] 页面静止后无持续动画。
- [ ] 没有背景音乐、彩屑、粒子、呼吸光或循环音景。

### 16.4 减少动态效果

- [ ] `motionEnabled=false` 时没有位移、缩放、错峰和模糊。
- [ ] 关闭动画后所有按钮、状态和异常恢复仍完整可用。
- [ ] 自动化测试可稳定控制 `motionEnabled`，不依赖截图时机猜状态。

### 16.5 真机矩阵

至少记录：

- iOS：一台当前主流机型。
- Android：一台中端或低端机型、一台主流机型。
- 网络：正常、慢网、断网恢复。
- 系统声音：普通音量、静音。
- 连续操作：快速答题、连续换理由、重复提交。

不得用开发者工具预览代替全部真机验证。

## 17. 与高保真原型的映射

可运行参考：`index.html`。

| 本文 | 原型状态/选择器 | 参考行为 |
| --- | --- | --- |
| M01 | `.choice[data-option]`、`.is-selected` | 选项锁定、微缩放、110ms 后切换 |
| M02 | `.result-page.is-entered` | 结果卡与理由卡错峰进入 |
| M03 | `.reaction.active`、`.resonance-count.selected` | 按钮完成态与人数出现 |
| M04 | `.reason-text.is-switching` | 160ms 淡出/模糊后替换 |
| M05 | `.submit-reason:disabled` | 禁用与启用颜色变化 |
| M06 | `.success-page.is-entered` | 成功卡上浮与缩放恢复 |

原型是节奏参考，不是生产架构。Coding Agent 应把这些行为映射到现有小程序组件和真实接口状态，不复制浏览器 DOM 操作方式。

## 18. 官方平台依据

- [tt.createAnimation](https://developer.open-douyin.com/docs/resource/zh-CN/mini-app/develop/api/interface/animation/tt-create-animation)：基础库 1.0.0 起支持，提供 `duration`、`timingFunction`、`delay`、`transformOrigin` 以及透明度、缩放、位移等动画能力。
- [tt.createInnerAudioContext](https://developer.open-douyin.com/docs/resource/zh-CN/mini-app/develop/api/media/audio/tt-create-inner-audio-context/)：基础库 1.0.0 起支持；Android 当前只支持单个内部音频实例；`stop` 后重新播放应重新设置 `src`。
- 抖音小程序 Page 生命周期：页面隐藏触发 `onHide`，页面卸载触发 `onUnload`；用于停止音效、清理计时器和异步引用。

## 19. Coding Agent 最终回报格式

```markdown
实现结果：完成 / 部分完成 / 阻塞

组件映射：
- M01：...
- M02：...
- M03：...
- M04：...
- M05：...
- M06：...

已修改文件：
- ...

验证：
- 自动化：...
- 抖音开发者工具：...
- iOS 真机：...
- Android 真机：...
- 慢网/失败/重复点击：...
- motionEnabled=false：...
- 音频失败降级：...

与本文差异：
- 差异：...
- 原因：平台限制 / 现有架构 / 兼容性 / 尚未完成

未完成或阻塞：
- ...
```

不得只回复“动效已完成”。必须提供真实验证结果；未做真机验证时明确写“未验证”，不得推断成功。
