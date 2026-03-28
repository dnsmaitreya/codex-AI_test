#!/usr/bin/env bash

set -euo pipefail

RUN_ID="$(date +%Y%m%d-%H%M%S)"
echo "=== AILuminate Full Run run_id=${RUN_ID} ==="

export AILUMINATE_CSV="eval_frameworks/mlcommons-ailuminate/airr_official_1.0_demo_en_us_prompt_set_release.csv"
export EVAL_RUN_ID="${RUN_ID}"

echo "[1/4] llm-guard (aisec-guard)"
/Users/oyf/miniforge3/condabin/conda run -n aisec-guard python evaluation_runner/run_llmguard.py

echo "[2/4] deepeval (aisec-eval)"
/Users/oyf/miniforge3/condabin/conda run -n aisec-eval python evaluation_runner/run_deepeval.py

echo "[3/4] guardrails (aisec-eval)"
/Users/oyf/miniforge3/condabin/conda run -n aisec-eval python evaluation_runner/run_guardrails.py

echo "[4/4] normalize (aisec-eval)"
/Users/oyf/miniforge3/condabin/conda run -n aisec-eval python evaluation_runner/normalize_results.py

echo "=== Full run complete ==="
