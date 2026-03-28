# 架构选型决策报告

- 生成时间（UTC）：2026-03-28T08:23:24.823806+00:00
- 输入文件：`evaluation_results/normalized/all_results_normalized.json`
- 原始记录数：3480
- 统计口径：每个工具仅统计最新 `run_id` 的结果

## 工具指标表

| 工具 | run_id | 总样本 | 准确率 | TP | TN | FP | FN | P50延迟 |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| promptfoo | 20260328-155939 | 8 | 100.0% | 4 | 4 | 0 | 0 | 27.0ms |
| llm-guard | 20260328-161608 | 1212 | 0.3% | 0 | 4 | 0 | 1208 | 2.2ms |
| deepeval | 20260328-161613 | 11 | 100.0% | 8 | 3 | 0 | 0 | 1332.2ms |
| PyRIT | 20260328-152346 | 15 | 20.0% | 3 | 0 | 0 | 12 | 1241.2ms |
| inspect_ai | 20260328-160109 | 6 | 33.3% | 2 | 0 | 2 | 2 | 11517.0ms |
| Guardrails | 20260328-161633 | 10 | 30.0% | 0 | 3 | 0 | 7 | 5265.1ms |

## Build / Integrate / Replace 决策表

| 能力域 | 决策 | 候选工具 | 依据 |
|---|---|---|---|
| 输入安全扫描 | Replace | llm-guard | Acc=0.3%, FN=1208，当前漏报偏高，优先做替换或重构。 |
| 红队测试 | Replace | PyRIT + promptfoo | PyRIT Acc=20.0%，更适合攻击生成与覆盖扩展，建议与 promptfoo 联合。 |
| 运行时策略护栏 | Replace | Guardrails | Acc=30.0%, P50=5265.1ms，策略命中率需提升。 |
| 自动化回归评测 | Integrate | promptfoo | Acc=100.0%, P50=27.0ms，适合 CI 门禁。 |
| 离线评估分析 | Integrate | deepeval | Acc=100.0%，质量稳定。 |
| 实验编排框架 | Replace | inspect_ai | Acc=33.3%, 可保留用于实验编排，但当前安全判定能力需补强。 |

## 结论

- `Integrate`：promptfoo、deepeval（作为默认评测流水线）。
- `Build/Replace`：llm-guard、Guardrails、inspect_ai、PyRIT 对应能力按漏报和稳定性继续改造。
- 建议在下一阶段以 S1/S2 分场景阈值重新校准，再更新最终架构决策。
