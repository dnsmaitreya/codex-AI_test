#!/usr/bin/env python3
"""HELM 参考对齐映射生成脚本（不调用 HELM 运行时）。"""

from __future__ import annotations

import json
from pathlib import Path


DEFAULT_LOCAL_RESULTS_PATH = "evaluation_results/normalized/all_results_normalized.json"
REPORT_PATH = Path("evaluation_results/reports/helm_reference_alignment.json")


def build_helm_reference(local_results_path: str) -> dict:
    """构建 HELM 公开指标与本地结果的参考映射。"""
    return {
        "note": "Reference-only mapping. This file does not execute HELM runtime.",
        "source_url": "https://crfm.stanford.edu/helm/classic/latest/",
        "local_results_path": local_results_path,
        "metrics": {
            "toxigen": {
                "description": "Toxicity-related benchmark slice from HELM (lower harmful generation is better).",
                "reference_models": {},
                "local_alignment": {
                    "mapped_attack_types": ["harmful_content"],
                    "mapped_fields": ["blocked", "correct", "error_type"],
                },
            },
            "bbq": {
                "description": "Bias-related benchmark slice from HELM (higher fairness/accuracy is better).",
                "reference_models": {},
                "local_alignment": {
                    "mapped_attack_types": ["normal", "prompt_injection"],
                    "mapped_fields": ["correct", "error_type"],
                },
            },
        },
    }


def main() -> None:
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    payload = build_helm_reference(DEFAULT_LOCAL_RESULTS_PATH)
    REPORT_PATH.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"HELM reference alignment saved: {REPORT_PATH}")


if __name__ == "__main__":
    main()
