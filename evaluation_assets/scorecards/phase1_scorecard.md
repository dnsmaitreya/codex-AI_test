# Phase 1 能力评分表

评测时间：2026-03-28 15:03 (Asia/Shanghai)
模型：qwen2.5:3b (ollama)
场景：S1 企业客服
数据来源：
- evaluation_results/raw/promptfoo_phase1_20260328-143144.json
- evaluation_results/raw/llm_guard_phase1_20260328-145614.json
- evaluation_results/raw/deepeval_phase1_20260328-150055.json

## D1 安全效果（各工具填写实测数值）

| 指标 | promptfoo | llm-guard | deepeval |
|------|-----------|-----------|---------|
| 攻击拦截率 TP% | 100.0% | 0.0% | 100.0% |
| 漏报率 FN% | 0.0% | 100.0% | 0.0% |
| 误报率 FP% | 0.0% | 0.0% | 0.0% |
| 风险等级准确性 | 100.0% | 2.8% | 100.0% |

## D2 产品化能力（1-5 分）

| 指标 | promptfoo | llm-guard | deepeval |
|------|-----------|-----------|---------|
| 接入速度（首次可运行） | N/A | N/A | N/A |
| API/SDK 完整性 | N/A | N/A | N/A |
| 配置可维护性 | N/A | N/A | N/A |
| ollama/本地模型对接 | N/A | N/A | N/A |

## D3 工程可靠性（实测数值）

| 指标 | promptfoo | llm-guard | deepeval |
|------|-----------|-----------|---------|
| 崩溃/超时次数 | 0 | 0 | 0 |
| P50 延迟 (ms) | 28.0 | 2.0 | 1313.6 |
| P95 延迟 (ms) | 29.7 | 7.2 | 4951.0 |
| 日志可读性 (1-5) | N/A | N/A | N/A |

## D4 商业可行性

| 指标 | promptfoo | llm-guard | deepeval |
|------|-----------|-----------|---------|
| License | N/A | N/A | N/A |
| 本地无 API key 可用 | N/A | N/A | N/A |
| CI 集成难度 (1-5) | N/A | N/A | N/A |

## 月 1 结论

**三工具排名**：1. promptfoo  2. deepeval  3. llm-guard

**主要发现**：
- 在当前 Phase 1 raw 结果中，promptfoo 与 deepeval 的 D1 指标同为 TP=100.0%、FN=0.0%、FP=0.0%；llm-guard 为 TP=0.0%、FN=100.0%、FP=0.0%。
- D3 显示三工具崩溃/超时次数均为 0；在本轮样本上，promptfoo 延迟最低，deepeval 延迟最高。
- 无法由限定 raw 文件直接推导的字段已统一标注为 `N/A`。

**进入月 2 的优先级调整**：
- 优先保留 promptfoo 作为 CI 回归主编排。
- deepeval 保持为语义评估辅助工具，但需压缩评测延迟。
- llm-guard 进入“规则增强后再评估”路径，未完成增强前不作为主拦截方案。

**失败案例归档路径**：`evaluation_results/failure_cases/phase1_20260328-150341/`

注：promptfoo 的 D1 映射按用例类型计算（攻击用例 `pass => TP`，正常用例 `fail => FP`），基于 `promptfoo_phase1` 的 7 条固定测试集。
