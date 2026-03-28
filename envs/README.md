# Conda 环境说明

所有环境均基于 Python 3.11，通过 miniforge3 管理。

## 环境划分

| 环境 | 覆盖工具 | 隔离原因 |
|------|----------|---------|
| `aisec-guard` | llm-guard | `transformers==4.51.3` 版本锁死，必须独立 |
| `aisec-red` | PyRIT | `torch>=2.7.0` + azure 全家桶，与 llm-guard 冲突 |
| `aisec-eval` | deepeval · inspect_ai · Guardrails | 无 torch 强依赖，兼容性好，合并节省空间 |
| 系统 Node.js | promptfoo | Node.js 工具，无需 conda |

## 创建所有环境

> **注意**：`aisec-eval` 包含 Guardrails，其依赖 `annoy` 在 ARM macOS 上无预编译包，
> 需要先设置正确的 SDK 头文件路径再编译。必须按以下顺序执行。

```bash
cd /Users/oyf/Code/codex/AI_test

# 1. aisec-guard（无特殊编译依赖，直接创建）
conda env create -f envs/aisec-guard.yml

# 2. aisec-red（无特殊编译依赖，直接创建）
conda env create -f envs/aisec-red.yml

# 3. aisec-eval（分两步：先建环境，再手动编译安装 annoy，然后装其余包）
conda env create -f envs/aisec-eval.yml   # 只创建 Python 空环境

SDK=$(xcrun --show-sdk-path)
CPLUS_INCLUDE_PATH="$SDK/usr/include/c++/v1:$SDK/usr/include" \
MACOSX_DEPLOYMENT_TARGET=12.0 \
  conda run -n aisec-eval pip install annoy   # 编译 annoy

conda run -n aisec-eval pip install \
  -e eval_frameworks/deepeval \
  -e eval_frameworks/inspect_ai \
  -e Guardrails \
  pyyaml requests litellm jsonschema
```

## 验证

```bash
# aisec-guard — 验证 llm-guard
conda run -n aisec-guard python -c "from llm_guard.input_scanners import PromptInjection; print('llm-guard OK')"

# aisec-red — 验证 PyRIT
conda run -n aisec-red python -c "import pyrit; print('PyRIT OK')"

# aisec-eval — 验证三个工具
conda run -n aisec-eval python -c "import deepeval; print('deepeval OK')"
conda run -n aisec-eval python -c "import inspect_ai; print('inspect_ai OK')"
conda run -n aisec-eval python -c "import nemoguardrails; print('nemoguardrails OK')"
# 注意：Guardrails 目录是 NVIDIA NeMo Guardrails，import 名为 nemoguardrails，非 guardrails

# promptfoo（Node.js，无需激活环境）
cd promptfoo && npx promptfoo --version
```

## 日常使用

```bash
# 激活特定环境
conda activate aisec-guard   # 运行 llm-guard 相关脚本
conda activate aisec-red     # 运行 PyRIT 红队脚本
conda activate aisec-eval    # 运行 deepeval / inspect_ai / Guardrails 脚本

# 或者不激活，直接用 conda run（适合脚本调用）
conda run -n aisec-guard python evaluation_runner/run_llmguard.py
conda run -n aisec-red   python evaluation_runner/run_pyrit.py
conda run -n aisec-eval  python evaluation_runner/run_deepeval.py
```

## 更新环境

```bash
# 如果 yml 文件有修改
conda env update -f envs/aisec-guard.yml --prune
conda env update -f envs/aisec-red.yml --prune
conda env update -f envs/aisec-eval.yml --prune
```

## 删除重建（遇到无法解决的依赖冲突时）

```bash
conda env remove -n aisec-guard
conda env create -f envs/aisec-guard.yml
```
