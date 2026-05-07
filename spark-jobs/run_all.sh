#!/bin/bash
# 运行所有 PySpark 分析任务
set -e

SPARK_MASTER="spark://spark-master:7077"
JOBS_DIR="/opt/spark-jobs/analysis"

echo "=== Starting PySpark Analysis Jobs ==="
echo "Time: $(date)"

for script in city_demand_analysis skill_freq_analysis salary_dist_analysis edu_salary_analysis; do
    echo ""
    echo "--- Running: ${script} ---"
    spark-submit \
        --master "${SPARK_MASTER}" \
        "${JOBS_DIR}/${script}.py"
    echo "--- Completed: ${script} ---"
done

echo ""
echo "=== All analysis jobs completed ==="
