# AI 安全产品市场调研：子项目能力测评方案

## 1. 文档目标

本方案用于评估当前仓库内子项目在“AI 安全产品”方向上的真实能力边界，强调两条并行路径：

- 手动测试：感受真实产品体验、调试难度与能力边界
- 自动测试：形成可重复、可对比、可回归的客观证据

本次评估对象不是“大模型本身”，而是子项目作为安全产品组件的能力与可产品化程度。

---

## 2. 评估范围（当前仓库）

核心子项目：

- `Guardrails`
- `PyRIT`
- `llm-guard`
- `promptfoo`
- `eval_frameworks/deepeval`
- `eval_frameworks/inspect_ai`
- `eval_frameworks/helm`
- `eval_frameworks/mlcommons-modelbench`
- `eval_frameworks/mlcommons-ailuminate`

说明：

- `mlcommons-ailuminate` 是安全提示数据集，不是执行引擎；应作为测试语料资产参与评估。
- `HELM / Modelbench` 更偏标准基准与研究型评估，落地成本需单独计入。

---

## 3. 需求分解（执行导向）

### 3.1 总体目标

需要回答以下核心问题：

1. 子项目是否能稳定跑通真实 AI 安全场景？
2. 子项目宣称能力与实际效果是否一致？
3. 作为产品组件时，集成成本、运维成本、误报漏报表现如何？
4. 最终应采用何种组合做产品架构（Build / Integrate / Replace）？

### 3.2 双轨评测模式

#### A. 手动测试轨（体验与边界探索）

目标：看真实体验与“非理想条件下”的能力边界。

任务拆解：

1. 为每个子项目完成一次从 0 到 1 的接入。
2. 在 3 类真实场景中进行人工攻击/对抗。
3. 记录接入耗时、调试成本、配置复杂度、错误可定位性。
4. 记录“误报/漏报”典型案例。

建议场景：

- 场景 S1：企业客服（单轮/多轮）
- 场景 S2：RAG 问答（知识库 + 幻觉风险）
- 场景 S3：Agent 工具调用（工具滥用、越权调用）

手动攻击样例类别：

- 提示注入（Prompt Injection）
- 越狱（Jailbreak）
- 系统提示泄露
- 敏感信息泄露（PII/密钥）
- 有害内容诱导
- 工具调用越权/参数投毒

#### B. 自动测试轨（量化与可回归）

目标：产出可比较、可复现、可持续回归的评测结果。

任务拆解：

1. 统一输入资产：测试集、场景配置、模型参数。
2. 对每个子项目执行同构评测任务。
3. 统一指标口径并输出结构化结果。
4. 将结果纳入回归基线，支持版本对比。

自动评测最低样本建议：

- 每场景至少 100 条（MVP）
- 生产前建议每场景 300~1000 条

### 3.3 评估维度与判定标准

#### 维度 D1：安全效果

- 攻击拦截率（TP）
- 漏报率（FN）
- 误报率（FP）
- 风险等级识别准确性

#### 维度 D2：产品化能力

- 接入速度（首次可运行时间）
- API/SDK 完整性
- 配置可维护性
- 策略编排能力

#### 维度 D3：工程可靠性

- 稳定性（崩溃率、超时率）
- 性能（P50/P95 延迟、吞吐）
- 可观测性（日志、追踪、可解释性）

#### 维度 D4：运营与商业可行性

- CI/CD 友好度
- 报告可读性与审计能力
- 社区活跃度与维护风险
- License 与商业使用风险

### 3.4 预期交付物

1. 子项目能力评分表（统一模板）
2. 场景化测试报告（手动 + 自动）
3. 失败样本库与复盘记录
4. 架构选型结论（推荐组合 + 替代方案）

---

## 4. 当前还缺哪些基建（真实测评开发必需）

以下为当前仓库开展“真正测评工程”仍需补齐的基建。

### 4.1 统一运行基线（必需）

缺口：

- 缺统一模型基线配置（同一模型、同一参数、同一 endpoint）
- 缺统一环境锁定（Python/Node 版本、依赖锁）

建议：

- 固定本地基线模型（如 `ollama` 指定一个主测模型 + 一个对照模型）
- 固定推理参数：`temperature/top_p/max_tokens/seed`
- 新增 `configs/baseline.yaml` 统一配置

### 4.2 测试数据资产层（必需）

缺口：

- 缺统一测试集目录和版本管理
- 缺“业务集 + 对抗集 + 回归集”分层

建议：

- 新建目录：`evaluation_assets/`
- 子目录建议：
  - `evaluation_assets/datasets/manual_cases/`
  - `evaluation_assets/datasets/auto_cases/`
  - `evaluation_assets/datasets/regression/`
- 为每条样本加 `id/场景/风险类别/期望结果`

### 4.3 执行编排层（必需）

缺口：

- 缺统一 runner（目前只能手工逐项目跑）
- 缺统一错误重试、超时、并发控制

建议：

- 新建 `evaluation_runner/`（脚本或小服务）
- 统一入口命令：
  - `make eval-manual`
  - `make eval-auto`
  - `make eval-regression`

### 4.4 指标与评分层（必需）

缺口：

- 缺统一指标定义与打分规范
- 各工具结果格式不同，无法横向对比

建议：

- 定义统一 schema：`result_schema.json`
- 统一字段：
  - `project`
  - `scenario`
  - `attack_type`
  - `blocked`
  - `latency_ms`
  - `error_type`
  - `evidence`
- 新建 `evaluation_assets/scorecards/scorecard_template.md`

### 4.5 观测与证据层（必需）

缺口：

- 缺统一日志与 trace 汇总
- 缺失败样本自动归档

建议：

- 新建 `evaluation_results/`：
  - `raw/`
  - `normalized/`
  - `reports/`
  - `failure_cases/`
- 每次运行生成时间戳目录并保存命令参数快照

### 4.6 回归与自动化（高优先级）

缺口：

- 缺变更后自动回归机制
- 缺质量门禁（如拦截率跌破阈值）

建议：

- 引入 CI 任务：`nightly` + `PR smoke`
- 设阈值门禁：
  - 安全拦截率不得低于基线
  - 误报率不得高于阈值

### 4.7 报告与决策产物（高优先级）

缺口：

- 缺可汇报的市场调研模板

建议：

- 统一输出两类报告：
  - 技术报告（指标、失败样本、性能）
  - 产品报告（接入成本、运营成本、商业风险）

---

## 5. 子项目在整体评测系统中的角色建议

- `promptfoo`：自动评测编排、报告、CI 回归主力
- `deepeval`：Python 应用评测与指标扩展主力
- `inspect_ai`：复杂任务编排与实验框架
- `PyRIT`：红队攻击生成与安全压力测试
- `llm-guard`：输入/输出扫描器能力组件
- `Guardrails`：策略编排与运行时防护核心候选
- `HELM`：硬基准参考与对外可信度补充
- `Modelbench + AILuminate`：标准安全基准对齐能力

---

## 6. 推荐落地节奏（MVP -> 规模化）

### Phase 1（1~2 周，MVP）

- 完成统一基线配置
- 完成 3 场景 x 5 攻击类型的手动评测
- 跑通 `promptfoo + deepeval + PyRIT` 自动评测最小链路
- 输出第一版对比报告

### Phase 2（2~4 周，可复现）

- 建立统一结果 schema 与归档
- 引入 `inspect_ai` 与 `Guardrails/llm-guard` 对照测试
- 加入 CI nightly 回归

### Phase 3（4 周+，产品决策）

- 纳入 `HELM / Modelbench` 标准基准补充
- 输出 Build/Integrate/Replace 决策文档
- 固化“发布前安全评测门禁”

---

## 7. 立即可执行的下一步

1. 建立目录骨架：`evaluation_assets/`、`evaluation_runner/`、`evaluation_results/`
2. 先选一个主场景（建议客服）做端到端试跑
3. 每个子项目先做 1 个 smoke test + 1 个真实攻击用例
4. 用统一模板记录结果，形成首轮市场调研事实库

