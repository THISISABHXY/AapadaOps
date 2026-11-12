#!/usr/bin/env python3
"""AapadaOps Evaluation Benchmark Runner.

Executes the empirical benchmark evaluation across all 160 disaster incidents,
measuring NLP extraction accuracy, spatial deduplication F1, prioritization alignment,
latency distributions, and OR-Tools MIP solver efficiency.
Outputs results to evaluation/reports/.
"""

import os
import sys
import shutil
import subprocess

def main():
    root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
    backend_dir = os.path.join(root_dir, "backend")
    evaluation_dir = os.path.join(root_dir, "evaluation")
    reports_dir = os.path.join(evaluation_dir, "reports")
    os.makedirs(reports_dir, exist_ok=True)

    print("================================================================================")
    print("                AapadaOps Empirical AI & OR-Tools Benchmark Suite               ")
    print("================================================================================")
    print(f"Working Directory : {root_dir}")
    print(f"Backend Directory : {backend_dir}")
    print(f"Reports Directory : {reports_dir}\n")

    eval_script = os.path.join(backend_dir, "evaluation", "evaluate_ai_engine.py")
    python_bin = sys.executable

    print(f"Executing evaluation suite: {eval_script} ...")
    env = os.environ.copy()
    env["PYTHONPATH"] = backend_dir

    result = subprocess.run([python_bin, eval_script], env=env, cwd=backend_dir)
    if result.returncode != 0:
        print(f"Benchmark execution failed with exit code {result.returncode}")
        sys.exit(result.returncode)

    # Copy output artifacts to evaluation/reports/
    src_bench = os.path.join(backend_dir, "evaluation", "benchmark_results.json")
    dst_bench = os.path.join(reports_dir, "benchmark_results.json")
    if os.path.exists(src_bench):
        shutil.copyfile(src_bench, dst_bench)
        print(f"\n[OK] Copied benchmark metrics to: {dst_bench}")

    src_deploy = os.path.join(backend_dir, "evaluation", "deployment_verification.json")
    dst_deploy = os.path.join(reports_dir, "deployment_verification.json")
    if os.path.exists(src_deploy):
        shutil.copyfile(src_deploy, dst_deploy)
        print(f"[OK] Copied deployment verification to: {dst_deploy}")

    print("\nBenchmark run completed successfully.")

if __name__ == "__main__":
    main()

