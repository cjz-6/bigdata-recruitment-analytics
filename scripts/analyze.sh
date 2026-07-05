#!/bin/bash
# 运行 PySpark 分析任务
cd "$(dirname "$0")/.."

echo "Triggering PySpark analysis via Spark..."
docker compose -f docker-compose.base.yml -f docker-compose.services.yml \
    exec spark-master /opt/spark-jobs/run_all.sh
echo "Analysis complete."
