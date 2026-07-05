#!/bin/bash
# ============================================================
#  招聘岗位需求分析系统 - Shutdown Script
#  Author : 陈坚卓 @ 广东梅州职业技术学院
#  GitHub : https://github.com/cjz-6
#  Version: 1.0.0  |  2026.05
# ============================================================

echo ""
echo "  [CJZ-BigData] 招聘岗位需求分析系统"
echo "  Stopping at $(date '+%Y-%m-%d %H:%M:%S')"
echo "  ----------------------------------------"

cd "$(dirname "$0")/.."
docker compose \
    -f docker-compose.base.yml \
    -f docker-compose.hadoop.yml \
    -f docker-compose.services.yml \
    down
echo "All services stopped."
