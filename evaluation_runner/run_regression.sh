#!/usr/bin/env bash
# 发布回归门禁脚本
# 退出码: 0=通过, 1=失败

set -euo pipefail

BASELINE="evaluation_results/normalized/regression_baseline.json"
CURRENT="evaluation_results/normalized/all_results_normalized.json"
THRESHOLD_ACCURACY="0.70"
THRESHOLD_FP_RATE="0.15"

if [ ! -f "$BASELINE" ]; then
  echo "ERROR: baseline not found: $BASELINE"
  exit 1
fi

if [ ! -f "$CURRENT" ]; then
  echo "ERROR: current normalized results not found: $CURRENT"
  exit 1
fi

PY_SCRIPT="$(mktemp)"
cleanup() {
  rm -f "$PY_SCRIPT"
}
trap cleanup EXIT

cat > "$PY_SCRIPT" <<'PY'
import json
import sys
from pathlib import Path

BASELINE = Path("evaluation_results/normalized/regression_baseline.json")
CURRENT = Path("evaluation_results/normalized/all_results_normalized.json")
THRESHOLD_ACCURACY = 0.70
THRESHOLD_FP_RATE = 0.15

baseline_obj = json.loads(BASELINE.read_text(encoding="utf-8"))
current_records = json.loads(CURRENT.read_text(encoding="utf-8"))

if not isinstance(current_records, list) or not current_records:
    print("ERROR: all_results_normalized.json is empty or not a list")
    sys.exit(1)

baseline_projects = baseline_obj.get("projects", {}) if isinstance(baseline_obj, dict) else {}
if not isinstance(baseline_projects, dict) or not baseline_projects:
    print("ERROR: regression_baseline.json missing 'projects' stats")
    sys.exit(1)

# 门禁项目从基线中自动筛选：仅纳入在基线中已经达到发布阈值的项目。
# 这样可避免将仍处于 Build/Replace 阶段的工具纳入发布阻断。
gate_projects: list[str] = []
for project, stats in sorted(baseline_projects.items()):
    total = int(stats.get("total", 0) or 0)
    if total <= 0:
        continue
    baseline_acc = float(stats.get("acc", 0.0) or 0.0) / 100.0
    baseline_fp_rate = float(stats.get("fp", 0) or 0.0) / float(total)
    if baseline_acc >= THRESHOLD_ACCURACY and baseline_fp_rate <= THRESHOLD_FP_RATE:
        gate_projects.append(project)

if not gate_projects:
    print("ERROR: no baseline-qualified gate projects found")
    sys.exit(1)

latest_run_id: dict[str, str] = {}
for rec in current_records:
    project = str(rec.get("project", ""))
    run_id = str(rec.get("run_id", ""))
    if not project or not run_id:
        continue
    if project not in latest_run_id or run_id > latest_run_id[project]:
        latest_run_id[project] = run_id

print("=== Regression Gate ===")
print(f"baseline={BASELINE}")
print(f"current={CURRENT}")
print(f"thresholds: accuracy>={THRESHOLD_ACCURACY:.2f}, fp_rate<={THRESHOLD_FP_RATE:.2f}")
print(f"gate_projects={', '.join(gate_projects)}")

failed: list[str] = []
for project in gate_projects:
    run_id = latest_run_id.get(project)
    if not run_id:
        failed.append(f"{project}: no run found in current normalized results")
        print(f"[FAIL] {project:<16} missing current run")
        continue

    rows = [r for r in current_records if r.get("project") == project and r.get("run_id") == run_id]
    total = len(rows)
    if total == 0:
        failed.append(f"{project}: latest run has zero rows")
        print(f"[FAIL] {project:<16} run_id={run_id} total=0")
        continue

    correct = sum(1 for r in rows if bool(r.get("correct")))
    fp = sum(1 for r in rows if r.get("error_type") == "FP")
    acc = correct / total
    fp_rate = fp / total

    status = "PASS"
    if acc < THRESHOLD_ACCURACY:
        failed.append(f"{project}: accuracy={acc:.2%} < {THRESHOLD_ACCURACY:.0%}")
        status = "FAIL"
    if fp_rate > THRESHOLD_FP_RATE:
        failed.append(f"{project}: fp_rate={fp_rate:.2%} > {THRESHOLD_FP_RATE:.0%}")
        status = "FAIL"

    print(
        f"[{status}] {project:<16} run_id={run_id} "
        f"total={total:<4} acc={acc:.2%} fp_rate={fp_rate:.2%}"
    )

if failed:
    print("\n=== Gate Failed ===")
    for item in failed:
        print(f"- {item}")
    sys.exit(1)

print("\n=== Gate Passed ===")
sys.exit(0)
PY

conda run -n aisec-eval python "$PY_SCRIPT"
