# Phase 2 能力评分表（6 工具横向对比）

评测时间：2026-03-28（基于归一化结果最新 run）
模型：qwen2.5:3b / qwen2.5-coder:14b（以结果记录为准）
场景：S1 客服 + S2 RAG（按各工具最新 run_id 统计）
数据来源：`evaluation_results/normalized/all_results_normalized.json`
统计口径：每个工具仅取 `run_id` 最大的一次运行，避免开发/复审重复运行叠加。

## 6 工具横向对比（D1）

| 工具 | 总样本 | 准确率% | TP | FP | FN | P50ms |
|------|-------:|--------:|---:|---:|---:|------:|
| promptfoo | 8 | 100.0 | 4 | 0 | 0 | 27.0 |
| llm-guard | 312 | 1.3 | 0 | 0 | 308 | 2.3 |
| deepeval | 11 | 100.0 | 8 | 0 | 0 | 1511.2 |
| PyRIT | 15 | 20.0 | 3 | 0 | 12 | 1241.2 |
| inspect_ai | 6 | 33.3 | 2 | 2 | 2 | 11517.0 |
| Guardrails | 10 | 30.0 | 0 | 0 | 7 | 5812.2 |

对应 run_id：
- promptfoo=`20260328-155939`，llm-guard=`20260328-160017`，deepeval=`20260328-160035`
- PyRIT=`20260328-152346`，inspect_ai=`20260328-160109`，Guardrails(nemoguardrails)=`20260328-160142`

## 产品化能力对比（D2）

| 维度 | promptfoo | llm-guard | deepeval | PyRIT | inspect_ai | Guardrails |
|------|-----------|-----------|----------|-------|------------|------------|
| 接入速度 | N/A | N/A | N/A | N/A | N/A | N/A |
| 策略编排 | N/A | N/A | N/A | N/A | N/A | N/A |
| 本地模型支持 | N/A | N/A | N/A | N/A | N/A | N/A |
| 报告质量 | N/A | N/A | N/A | N/A | N/A | N/A |

说明：当前阶段限定数据源仅为 `all_results_normalized.json`，其中不包含 D2 所需的接入流程、配置复杂度、文档/报告可维护性等主观与过程型字段，因此统一标注为 `N/A`。

## 架构组合初步判断

| 用途 | 推荐工具 | 备注 |
|------|----------|------|
| 输入扫描 | 暂不建议单独依赖 llm-guard | 最新 run 中 `FN=308/312`，需先重配规则/阈值后再纳入主链路。 |
| 输出扫描 | deepeval（离线评测侧） | `TP=8, FN=0`；但 `P50=1511.2ms`，更适合评测判分而非在线硬拦截。 |
| 红队测试 | PyRIT | 可稳定生成变体攻击样本（15 条）；当前判分准确率 `20.0%`，需结合人工复核。 |
| CI 回归 | promptfoo | 最新 run `Accuracy=100.0%` 且 `P50=27.0ms`，自动化执行成本最低。 |
| 运行时防护 | Guardrails（调优后再上线） | 最新 run `FN=7/10`、准确率 `30.0%`，当前策略召回不足。 |
| 评测框架 | inspect_ai + deepeval 组合 | inspect_ai 可覆盖 S1/S2（`FP=2,FN=2`），建议与 deepeval 交叉校验。 |

## 月 2 结论

- 最强安全效果工具：`promptfoo` 与 `deepeval`（最新 run 准确率均为 `100.0%`）。
- 最易纳入 CI 的工具：`promptfoo`（低时延、结果稳定、样本执行完整）。
- 最高风险误差项：`llm-guard` 与 `Guardrails` 的漏报偏高（分别 `FN=308`、`FN=7`）。
- 进入月 3 的重点：
  1. 在更大样本集上复验 `promptfoo/deepeval` 的稳定性，避免小样本高分偏差。
  2. 对 `llm-guard/Guardrails` 做规则与阈值调优，优先压降 `FN`。
  3. 将 `PyRIT` 固定为红队样本生成器，与评测判分工具解耦组合。
