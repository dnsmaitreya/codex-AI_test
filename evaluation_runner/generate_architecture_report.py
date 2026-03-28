#!/usr/bin/env python3
"""
Generate architecture decision report from normalized evaluation results.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path


INPUT_PATH = Path("evaluation_results/normalized/all_results_normalized.json")
OUTPUT_PATH = Path("evaluation_results/reports/architecture_decision.md")

PROJECT_ORDER = [
    "promptfoo",
    "llm-guard",
    "deepeval",
    "pyrit",
    "inspect_ai",
    "nemoguardrails",
]

PROJECT_LABEL = {
    "promptfoo": "promptfoo",
    "llm-guard": "llm-guard",
    "deepeval": "deepeval",
    "pyrit": "PyRIT",
    "inspect_ai": "inspect_ai",
    "nemoguardrails": "Guardrails",
}


def _median(values: list[float]) -> float:
    if not values:
        return 0.0
    ordered = sorted(values)
    return float(ordered[len(ordered) // 2])


def _rate(numerator: int, denominator: int) -> float:
    if denominator <= 0:
        return 0.0
    return (numerator / denominator) * 100.0


def _fmt_rate(value: float) -> str:
    return f"{value:.1f}%"


def _fmt_ms(value: float) -> str:
    return f"{value:.1f}ms"


def _decision_for_tool(metric: dict) -> str:
    accuracy = metric["accuracy_pct"]
    fp_rate = metric["fp_rate_pct"]
    fn_rate = metric["fn_rate_pct"]
    if accuracy >= 85.0 and fp_rate <= 10.0 and fn_rate <= 20.0:
        return "Integrate"
    if accuracy < 40.0 or fn_rate > 50.0:
        return "Replace"
    return "Build"


def aggregate_stats(results: list[dict]) -> dict:
    latest_run_by_project: dict[str, str] = {}
    for row in results:
        project = str(row.get("project", "")).strip()
        run_id = str(row.get("run_id", "")).strip()
        if not project or not run_id:
            continue
        if project not in latest_run_by_project or run_id > latest_run_by_project[project]:
            latest_run_by_project[project] = run_id

    filtered = [
        row
        for row in results
        if str(row.get("project", "")).strip() in latest_run_by_project
        and str(row.get("run_id", "")).strip()
        == latest_run_by_project[str(row.get("project", "")).strip()]
    ]

    metrics: dict[str, dict] = {}
    for row in filtered:
        project = str(row.get("project", "")).strip()
        if not project:
            continue
        metric = metrics.setdefault(
            project,
            {
                "run_id": latest_run_by_project.get(project, ""),
                "total": 0,
                "correct": 0,
                "tp": 0,
                "tn": 0,
                "fp": 0,
                "fn": 0,
                "latencies": [],
            },
        )

        blocked = bool(row.get("blocked", False))
        expected = bool(row.get("expected", False))
        correct = bool(row.get("correct", False))
        error_type = row.get("error_type")
        latency_ms = row.get("latency_ms")

        metric["total"] += 1
        if correct:
            metric["correct"] += 1
        if error_type == "FP":
            metric["fp"] += 1
        elif error_type == "FN":
            metric["fn"] += 1
        elif blocked and expected:
            metric["tp"] += 1
        elif (not blocked) and (not expected):
            metric["tn"] += 1

        if isinstance(latency_ms, (int, float)):
            metric["latencies"].append(float(latency_ms))

    for metric in metrics.values():
        total = metric["total"]
        metric["accuracy_pct"] = _rate(metric["correct"], total)
        metric["fp_rate_pct"] = _rate(metric["fp"], total)
        metric["fn_rate_pct"] = _rate(metric["fn"], total)
        metric["p50_ms"] = _median(metric["latencies"])

    return {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "input_path": str(INPUT_PATH),
        "total_records": len(results),
        "latest_run_by_project": latest_run_by_project,
        "metrics": metrics,
    }


def render_report(stats: dict) -> str:
    metrics = stats.get("metrics", {})
    lines: list[str] = []
    lines.append("# 架构选型决策报告")
    lines.append("")
    lines.append(f"- 生成时间（UTC）：{stats.get('generated_at', '')}")
    lines.append(f"- 输入文件：`{stats.get('input_path', '')}`")
    lines.append(f"- 原始记录数：{stats.get('total_records', 0)}")
    lines.append("- 统计口径：每个工具仅统计最新 `run_id` 的结果")
    lines.append("")

    lines.append("## 工具指标表")
    lines.append("")
    lines.append("| 工具 | run_id | 总样本 | 准确率 | TP | TN | FP | FN | P50延迟 |")
    lines.append("|---|---|---:|---:|---:|---:|---:|---:|---:|")

    for project in PROJECT_ORDER:
        metric = metrics.get(project)
        if not metric:
            continue
        lines.append(
            "| "
            + " | ".join(
                [
                    PROJECT_LABEL.get(project, project),
                    metric["run_id"],
                    str(metric["total"]),
                    _fmt_rate(metric["accuracy_pct"]),
                    str(metric["tp"]),
                    str(metric["tn"]),
                    str(metric["fp"]),
                    str(metric["fn"]),
                    _fmt_ms(metric["p50_ms"]),
                ]
            )
            + " |"
        )

    lines.append("")
    lines.append("## Build / Integrate / Replace 决策表")
    lines.append("")
    lines.append("| 能力域 | 决策 | 候选工具 | 依据 |")
    lines.append("|---|---|---|---|")

    llm_guard_metric = metrics.get("llm-guard", {})
    pyrit_metric = metrics.get("pyrit", {})
    guardrails_metric = metrics.get("nemoguardrails", {})
    promptfoo_metric = metrics.get("promptfoo", {})
    deepeval_metric = metrics.get("deepeval", {})
    inspect_metric = metrics.get("inspect_ai", {})

    lines.append(
        "| 输入安全扫描 | "
        f"{_decision_for_tool(llm_guard_metric) if llm_guard_metric else 'Build'}"
        " | llm-guard | "
        f"Acc={_fmt_rate(llm_guard_metric.get('accuracy_pct', 0.0))}, "
        f"FN={llm_guard_metric.get('fn', 0)}，当前漏报偏高，优先做替换或重构。 |"
    )
    lines.append(
        "| 红队测试 | "
        f"{_decision_for_tool(pyrit_metric) if pyrit_metric else 'Integrate'}"
        " | PyRIT + promptfoo | "
        f"PyRIT Acc={_fmt_rate(pyrit_metric.get('accuracy_pct', 0.0))}，"
        "更适合攻击生成与覆盖扩展，建议与 promptfoo 联合。 |"
    )
    lines.append(
        "| 运行时策略护栏 | "
        f"{_decision_for_tool(guardrails_metric) if guardrails_metric else 'Build'}"
        " | Guardrails | "
        f"Acc={_fmt_rate(guardrails_metric.get('accuracy_pct', 0.0))}, "
        f"P50={_fmt_ms(guardrails_metric.get('p50_ms', 0.0))}，策略命中率需提升。 |"
    )
    lines.append(
        "| 自动化回归评测 | "
        f"{_decision_for_tool(promptfoo_metric) if promptfoo_metric else 'Integrate'}"
        " | promptfoo | "
        f"Acc={_fmt_rate(promptfoo_metric.get('accuracy_pct', 0.0))}, "
        f"P50={_fmt_ms(promptfoo_metric.get('p50_ms', 0.0))}，适合 CI 门禁。 |"
    )
    lines.append(
        "| 离线评估分析 | "
        f"{_decision_for_tool(deepeval_metric) if deepeval_metric else 'Integrate'}"
        " | deepeval | "
        f"Acc={_fmt_rate(deepeval_metric.get('accuracy_pct', 0.0))}，质量稳定。 |"
    )
    lines.append(
        "| 实验编排框架 | "
        f"{_decision_for_tool(inspect_metric) if inspect_metric else 'Build'}"
        " | inspect_ai | "
        f"Acc={_fmt_rate(inspect_metric.get('accuracy_pct', 0.0))}, "
        "可保留用于实验编排，但当前安全判定能力需补强。 |"
    )

    lines.append("")
    lines.append("## 结论")
    lines.append("")
    lines.append("- `Integrate`：promptfoo、deepeval（作为默认评测流水线）。")
    lines.append("- `Build/Replace`：llm-guard、Guardrails、inspect_ai、PyRIT 对应能力按漏报和稳定性继续改造。")
    lines.append("- 建议在下一阶段以 S1/S2 分场景阈值重新校准，再更新最终架构决策。")
    lines.append("")

    return "\n".join(lines)


def main() -> None:
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    if not INPUT_PATH.exists():
        raise FileNotFoundError(f"Input file not found: {INPUT_PATH}")

    payload = json.loads(INPUT_PATH.read_text(encoding="utf-8"))
    if not isinstance(payload, list):
        raise ValueError("all_results_normalized.json must be a list of records")

    stats = aggregate_stats(payload)
    report = render_report(stats)
    OUTPUT_PATH.write_text(report, encoding="utf-8")
    print(f"Architecture report saved: {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
