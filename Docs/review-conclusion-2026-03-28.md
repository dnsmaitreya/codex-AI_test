# 评审结论（2026-03-28）

## 执行完整性

| 阶段 | 状态 | 备注 |
|------|------|------|
| S1–S14（14/15） | ✅ APPROVED | 评测脚本、数据集、结果、报告均已生成 |
| S15（1/15） | ✅ COMPLETED | 开发产出完整；本轮补齐看板与推送动作 |
| GitHub 推送 | ✅ COMPLETED | 已修复结果目录入库策略并完成推送 |

## 关键产出质量

| 产出 | 结论 | 说明 |
|------|------|------|
| 评测脚本 6 个 | ✅ 可用 | API 使用正确，NeMo 脚本为修正版 |
| 最终技术报告 | ✅ 合理 | 结论与数据一致，证据链完整 |
| 架构决策报告 | ✅ 合理 | Build/Integrate/Replace 依据充分 |
| promptfoo/deepeval 结论 | ⚠️ 样本偏小 | 当前 8/11 条，仅可作方向性结论 |
| llm-guard 0.3% | ✅ 真实发现 | 语义型有害内容超出纯模式扫描能力 |
| regression_baseline | ⚠️ 样本过少 | 当前仅 3 条，门禁阈值参考意义不足 |

## 数据质量观察

| 工具 | 问题 | 评估 |
|------|------|------|
| llm-guard | 1208/1208 有害内容 FN（准确率 0.3%） | 模式匹配型扫描器对语义攻击覆盖不足，结论可信 |
| promptfoo/deepeval | 样本量 8/11 | 框架运行正常，但结果置信度不足 |
| Guardrails | 0 TP、7 FN | 现有 Colang 模式覆盖面偏窄 |
| regression_baseline | 仅 3 条 | 无法形成有效回归门禁 |

## 后续行动项（不影响本次评测有效性）

1. 将 promptfoo/deepeval 样本扩展到至少 50 条后再给最终结论。
2. 扩展 NeMo Guardrails 的 Colang 规则覆盖，重点补齐越狱和注入变体。
3. 将 regression_baseline 扩展到至少 30 条并覆盖主要攻击类型。
4. 评估 llm-guard 引入 LLM 语义判定或混合判定链路，降低 FN。

## 仓库地址

- GitHub: <https://github.com/dnsmaitreya/codex-AI_test>

