#!/bin/bash
# 清理 3 个月前的旧数据 — MySQL + HDFS
# 建议每月执行一次：0 3 1 * * /root/bigdata/scripts/cleanup_old_data.sh

set -e
cd "$(dirname "$0")/.."

THREE_MONTHS_AGO=$(date -d '3 months ago' +%Y-%m-%d)
echo "[$(date)] 清理 ${THREE_MONTHS_AGO} 之前的旧数据..."

# ─── MySQL: 删除 3 个月前的岗位数据 ───
echo "[MySQL] 清理 jobs_raw..."
# 注意：请先在 .env 文件中配置 MYSQL_PASSWORD，或直接替换下行中的占位符
MYSQL_CMD="docker exec cjz-mysql mysql -u bigdata -p${MYSQL_PASSWORD:-请替换为你的MySQL密码} -D job_analysis"

BEFORE_COUNT=$($MYSQL_CMD -N -e "SELECT COUNT(*) FROM jobs_raw WHERE crawl_time < '${THREE_MONTHS_AGO}'" 2>/dev/null)
echo "  待删除: ${BEFORE_COUNT} 条"

$MYSQL_CMD -e "DELETE FROM jobs_raw WHERE crawl_time < '${THREE_MONTHS_AGO}'" 2>/dev/null
echo "  已删除 ${BEFORE_COUNT} 条旧记录"

AFTER_COUNT=$($MYSQL_CMD -N -e "SELECT COUNT(*) FROM jobs_raw" 2>/dev/null)
echo "  当前总记录: ${AFTER_COUNT} 条"

# ─── HDFS: 删除 3 个月前的 Spark 输出 ───
echo "[HDFS] 清理旧数据..."
if docker exec cjz-namenode hdfs dfs -test -d /user/spark/output 2>/dev/null; then
    docker exec cjz-namenode hdfs dfs -ls /user/spark/output/ 2>/dev/null | while read perm reps owner group size month day time path; do
        if [[ "$path" =~ [0-9]{4}-[0-9]{2}-[0-9]{2} ]]; then
            DIR_DATE=$(echo "$path" | grep -oP '\d{4}-\d{2}-\d{2}')
            if [[ "$DIR_DATE" < "$THREE_MONTHS_AGO" ]]; then
                echo "  删除 HDFS: $path"
                docker exec cjz-namenode hdfs dfs -rm -r -skipTrash "$path" 2>/dev/null
            fi
        fi
    done
fi

echo "[$(date)] 清理完成。"
