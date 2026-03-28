# AI 子项目中文总览

本仓库当前包含 9 个主要子项目（4 个通用安全/评测项目 + 5 个评测框架项目）。

## 中文 README 索引

- [Guardrails 中文](./Guardrails/README.zh-CN.md)
- [PyRIT 中文](./PyRIT/README.zh-CN.md)
- [llm-guard 中文](./llm-guard/README.zh-CN.md)
- [promptfoo 中文](./promptfoo/README.zh-CN.md)
- [DeepEval 中文](./eval_frameworks/deepeval/README.zh-CN.md)
- [HELM 中文](./eval_frameworks/helm/README.zh-CN.md)
- [Inspect AI 中文](./eval_frameworks/inspect_ai/README.zh-CN.md)
- [MLCommons AILuminate 中文](./eval_frameworks/mlcommons-ailuminate/README.zh-CN.md)
- [MLCommons Modelbench 中文](./eval_frameworks/mlcommons-modelbench/README.zh-CN.md)

## 子项目优缺点对比

| 子项目 | 优势 | 局限 | 推荐用途 |
|---|---|---|---|
| Guardrails | 护栏编排强<br>流程可控 | 配置偏复杂<br>学习成本高 | 生产客服<br>合规问答 |
| PyRIT | 红队导向清晰<br>研究属性强 | 上手资料分散<br>需读官网 | 安全评估<br>攻防研究 |
| llm-guard | 接入轻量<br>扫描器丰富 | 偏扫描层<br>端到端评测弱 | API 网关防护<br>上线前过滤 |
| promptfoo | 上手快<br>CI/CD 友好 | 深度学术指标<br>不算最强 | 日常回归测试<br>模型横评 |
| DeepEval | 指标覆盖广<br>适合 Python 研发 | 指标多<br>选择门槛高 | RAG/Agent 评测<br>持续验收 |
| HELM | 标准化强<br>可复现好 | 运行成本高<br>上手偏慢 | 学术基准<br>公开对比 |
| Inspect AI | 预置 eval 多<br>扩展性好 | 文档偏框架化<br>改造需经验 | 结构化实验<br>安全评测 |
| AILuminate | 风险分类清晰<br>数据规范 | 仅数据集<br>非执行框架 | 安全语料构建<br>覆盖抽样 |
| Modelbench | 报告链路完整<br>对齐 MLCommons | 全量跑得慢<br>依赖外部密钥 | 官方体系测评<br>风险聚合报告 |

## 选型建议（简版）

- 快速工程落地：`promptfoo + llm-guard`
- 生产对话护栏：`Guardrails`
- 深度 Python 评测：`DeepEval`
- 学术/公开基准：`HELM`
- MLCommons 安全标准对齐：`Modelbench + AILuminate`
