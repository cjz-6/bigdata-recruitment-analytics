#!/bin/bash
set -e

# 设置时区
ln -sf /usr/share/zoneinfo/Asia/Shanghai /etc/localtime
echo "Asia/Shanghai" > /etc/timezone

case "${SPARK_MODE}" in
  master)
    echo "Starting Spark Master..."
    exec /opt/spark/bin/spark-class org.apache.spark.deploy.master.Master \
      --host "${SPARK_MASTER_HOST:-spark-master}" \
      --port "${SPARK_MASTER_PORT:-7077}"
    ;;
  worker)
    echo "Starting Spark Worker connecting to ${SPARK_MASTER_URL}..."
    exec /opt/spark/bin/spark-class org.apache.spark.deploy.worker.Worker \
      "${SPARK_MASTER_URL:-spark://spark-master:7077}"
    ;;
  *)
    echo "SPARK_MODE must be 'master' or 'worker'"
    exit 1
    ;;
esac
