# 项目协作约束

后续在本项目中进行产品、设计、文案、原型或开发工作前，必须先阅读并遵守：

- [docs/产品理念与MVP设计准则.md](docs/产品理念与MVP设计准则.md)
- [docs/答案之外-品牌文案规范.md](docs/答案之外-品牌文案规范.md)

优先级：若历史设计稿、旧命名、既有实现与上述文档冲突，以这两份文档为准；任何涉及 MVP 范围、匿名边界、真实数据、文案或交互主路径的变更，必须先通过《产品理念与MVP设计准则》的“实施前检查”。

## 项目级 AI Skills

- [题库扩题助手](.agents/skills/generate-questions/SKILL.md)：为「答案之外」生成新题目、选项与匿名理由，自动去重并写入题库 CSV。
  - Cursor 用户可通过 `.cursor/rules/generate-questions.mdc` 触发。
  - 该 skill 已按 GitHub Copilot、Kimi Code、OpenCode 的通用约定放在 `.agents/skills/` 目录下。
