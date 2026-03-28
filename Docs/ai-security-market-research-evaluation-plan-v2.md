# AI 安全产品市场调研：子项目能力测评方案 v2

> 本版本基于 v1 评审后修订。核心调整：锚定当前实际条件、收紧 Phase 1 目标、明确 HELM/Modelbench 的限制、将 AILuminate 数据集作为首选语料资产。

---

## 评审摘要（v1 → v2 主要修订点）

| 问题 | v1 状态 | v2 修订 |
|------|---------|---------|
| 没有安装任何工具包 | 未提及 | Phase 0 专门处理环境搭建 |
| Phase 1 覆盖 9 个项目过宽 | 3 场景×5 攻击×9 项目 | Phase 1 收窄至 3 工具×1 场景×3 攻击类型 |
| 模型基线未指定 | 建议用 ollama，未具体 | 固定 qwen2.5:3b（主）/ qwen2.5-coder:14b（对照） |
| HELM 可运行性未评估 | Phase 3 纳入 | 明确标注为"参考对齐，不自托管" |
| Modelbench 依赖外部 API | 未提及 | 明确标注需 MLCommons 外部接入，Phase 3 评估可行性 |
| AILuminate 数据集未利用 | 仅说明为语料资产 | 直接用于 Phase 1 自动测试集（1290 条 EN 样本） |
| 时间线过乐观 | Phase 1 = 1~2 周覆盖全部 | Phase 1 = 2 周，只跑通核心链路 |

---

## 1. 文档目标

评估当前仓库内子项目在"AI 安全产品"方向的真实能力边界，产出可用于产品选型的客观证据。

评估对象：子项目作为安全产品组件的能力与可产品化程度（非大模型本身）。

双轨并行：
- **手动测试轨**：感受真实接入体验、识别能力边界
- **自动测试轨**：形成可重复、可回归的量化对比证据

---

## 2. 当前条件基线（已确认）

### 运行环境
- Python 3.12.12 / Node.js v25.6.1
- Ollama 已安装，可用模型：

| 模型 | 大小 | 角色 |
|------|------|------|
| qwen2.5:0.5b | 397MB | 冒烟测试（极速） |
| qwen2.5:3b | 1.9GB | **主测模型**（速度/效果平衡） |
| qwen2.5-coder:7b | 4.7GB | 备用 |
| qwen2.5-coder:14b | 9GB | **对照模型**（更高质量） |
| qwen3-coder:30b | 18GB | 精细测试备用 |

- 无 API key 依赖（全部走本地 ollama）
- 无云端服务依赖

### 数据资产（已确认可用）
- `eval_frameworks/mlcommons-ailuminate/airr_official_1.0_demo_en_us_prompt_set_release.csv`
  - 1290 条 EN 样本，包含 `hazard`（危害类别）、`persona`（角色）字段
  - 可直接用作自动测试集，无需另建

### 工具安装状态
- 所有子项目均为源码克隆，**尚未安装依赖**

---

## 3. 评估范围与工具分级

### 3.1 可自托管工具（Phase 1~2 执行对象）

| 工具 | 语言 | 能力定位 | 优先级 |
|------|------|----------|--------|
| `promptfoo` | Node.js | 自动评测编排 + CI 回归主力 | P0 |
| `llm-guard` | Python | 输入/输出安全扫描器 | P0 |
| `deepeval` | Python | Python 应用评测 + 指标扩展 | P0 |
| `PyRIT` | Python | 红队攻击生成 + 安全压力测试 | P1 |
| `inspect_ai` | Python | 复杂任务编排与实验框架 | P1 |
| `Guardrails` | Python | 策略编排 + 运行时防护候选 | P1 |

### 3.2 受限工具（Phase 3 评估可行性）

| 工具 | 限制说明 | Phase 3 目标 |
|------|----------|-------------|
| `HELM` | 依赖 Stanford CRFM 托管基础设施，本地自运行成本极高 | 参考对齐，不自托管；仅对比其公开 leaderboard 数据 |
| `mlcommons-modelbench` | 需要 MLCommons 外部 API 接入才能完整运行评测 | 评估独立运行可行性；数据集（AILuminate）先行复用 |

### 3.3 数据集资产（贯穿全程）

| 资产 | 来源 | 用途 |
|------|------|------|
| AILuminate EN dataset | 本地已有，1290 条 | Phase 1 自动测试主语料 |
| 手动构造样本 | 评测人员编写 | 场景化手动测试 |
| 回归集 | 从失败案例中沉淀 | Phase 2 回归基线 |

---

## 4. 需求分解（执行导向）

### 4.1 核心问题（不变）

1. 子项目是否能稳定跑通真实 AI 安全场景？
2. 子项目宣称能力与实际效果是否一致？
3. 集成成本、运维成本、误报漏报表现如何？
4. 最终应采用何种组合做产品架构（Build / Integrate / Replace）？

### 4.2 双轨评测模式

#### A. 手动测试轨

目标：感受接入体验与"非理想条件下"的能力边界。

任务：
1. 每个子项目完成一次从 0 到 1 的接入，记录耗时与障碍。
2. 选定场景下进行人工攻击/对抗，记录典型误报/漏报案例。
3. 评估配置可维护性与错误可定位性。

**分阶段场景覆盖：**

| 阶段 | 场景 | 攻击类型 |
|------|------|----------|
| Phase 1 | S1：企业客服（单轮） | 提示注入、越狱、PII 泄露 |
| Phase 2 | S2：RAG 问答（知识库+幻觉） | 系统提示泄露、有害内容诱导 |
| Phase 3 | S3：Agent 工具调用 | 工具滥用、越权调用、参数投毒 |

#### B. 自动测试轨

目标：产出可比较、可复现的量化评测结果。

任务：
1. 统一模型基线：`qwen2.5:3b`，固定参数（temperature=0.0, seed=42, max_tokens=512）。
2. 统一输入资产：AILuminate 数据集（Phase 1 取 100 条 subset，覆盖主要 hazard 类别）。
3. 对每个 P0 工具执行同构评测任务，输出统一 schema 结果。
4. 结果纳入回归基线。

**最小样本要求（修订）：**

| 阶段 | 每场景样本数 | 来源 |
|------|-------------|------|
| Phase 1 MVP | 30 条/攻击类型（共 90 条） | AILuminate 子集 |
| Phase 2 可复现 | 100 条/场景 | AILuminate + 手工补充 |
| Phase 3 规模化 | 300~500 条/场景 | AILuminate 全集 + 扩充 |

### 4.3 评估维度与判定标准（不变）

- **D1 安全效果**：拦截率 TP、漏报率 FN、误报率 FP、风险等级识别准确性
- **D2 产品化能力**：接入速度、API/SDK 完整性、配置可维护性、策略编排能力
- **D3 工程可靠性**：稳定性（崩溃/超时率）、P50/P95 延迟、可观测性
- **D4 运营与商业可行性**：CI/CD 友好度、报告可读性、社区活跃度、License 风险

### 4.4 预期交付物

1. 子项目能力评分表（统一模板）
2. 场景化测试报告（手动 + 自动）
3. 失败样本库与复盘记录
4. 架构选型结论（推荐组合 + 替代方案）

---

## 5. 基础设施缺口与建设顺序

按执行依赖关系排序（后者依赖前者）：

### 优先级 1：模型基线配置
- 新建 `configs/baseline.yaml`
- 固定：model=qwen2.5:3b, temperature=0.0, seed=42, max_tokens=512, ollama_endpoint=http://localhost:11434

### 优先级 2：测试数据资产目录
```
evaluation_assets/
  datasets/
    ailuminate/        ← AILuminate CSV 子集切片
    manual_cases/      ← 手动场景用例（S1/S2/S3）
    regression/        ← 失败案例沉淀
```

### 优先级 3：统一结果 Schema
- 新建 `configs/result_schema.json`
- 字段：`project, scenario, attack_type, input, blocked, latency_ms, error_type, evidence, model, timestamp`

### 优先级 4：执行 Runner
```
evaluation_runner/
  run_manual.sh
  run_auto.sh
  run_regression.sh
```

### 优先级 5：结果归档
```
evaluation_results/
  raw/
  normalized/
  reports/
  failure_cases/
```

### 优先级 6：回归与 CI（Phase 2）
- nightly 回归任务
- 质量门禁：拦截率不得低于基线，误报率不得高于阈值

### 优先级 7：报告模板（Phase 2）
- 技术报告（指标、失败样本、性能）
- 产品报告（接入成本、运营成本、商业风险）

---

## 6. 落地节奏（修订版）

### Phase 0（第 0.5 周，前置条件）

目标：搭环境，确保任何工具都能跑起来。

- [ ] 建立目录骨架（`evaluation_assets/`, `evaluation_runner/`, `evaluation_results/`, `configs/`）
- [ ] 新建 `configs/baseline.yaml`（固定模型参数）
- [ ] 新建 `configs/result_schema.json`
- [ ] 切割 AILuminate 数据集为测试子集（各 hazard 类别均匀取样 100 条）
- [ ] 验证 ollama `qwen2.5:3b` 可正常响应

### Phase 1（第 1~2 周，MVP）

目标：3 个 P0 工具跑通端到端，产出第一版可比较报告。

**工具覆盖**：`promptfoo` + `llm-guard` + `deepeval`

手动测试轨：
- [ ] 完成 3 个工具各自的从 0 到 1 接入，记录耗时
- [ ] 在场景 S1（客服单轮）下，对每个工具手动执行 3 类攻击（提示注入、越狱、PII 泄露）
- [ ] 记录典型误报/漏报案例

自动测试轨：
- [ ] 从 AILuminate 中提取 30 条/攻击类型（共 90 条），构建 Phase 1 测试集
- [ ] 对 3 个工具执行统一自动评测
- [ ] 输出结构化结果（符合 result_schema.json）

交付：
- [ ] 3 工具能力评分表（D1~D4）
- [ ] 第一版对比报告

**成功标准**：每个工具至少完成 90 条样本的自动扫描并输出结果，误报率/拦截率可读取。

### Phase 2（第 3~4 周，可复现）

目标：覆盖剩余 P1 工具，建立回归基线。

- [ ] 接入 `PyRIT`（红队攻击生成）、`inspect_ai`、`Guardrails`
- [ ] 扩展到场景 S2（RAG 问答），每场景 100 条样本
- [ ] 建立统一结果归档（带时间戳目录）
- [ ] 引入 CI nightly 回归
- [ ] 输出 6 工具横向对比报告

### Phase 3（第 5 周+，产品决策）

目标：补充标准基准参考，输出选型决策。

- [ ] 对接 HELM 公开 leaderboard 数据（参考对齐，不自托管）
- [ ] 评估 Modelbench + MLCommons API 接入可行性
- [ ] 扩展到场景 S3（Agent 工具调用）
- [ ] 输出 Build/Integrate/Replace 决策文档
- [ ] 固化发布前安全评测门禁

---

## 7. 立即可执行的下一步（按顺序）

1. 执行 Phase 0：建目录、写 baseline.yaml、切 AILuminate 子集
2. 安装 `promptfoo`（npm install），跑通 ollama 对接的最小 smoke test
3. 安装 `llm-guard`（pip install），对 1 条样本验证扫描链路
4. 安装 `deepeval`（pip install），配置 ollama provider，跑通 1 个 test case
5. 三个工具均冒烟通过后，启动 Phase 1 正式评测
