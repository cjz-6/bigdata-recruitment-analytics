#!/bin/bash
# ============================================================
#  招聘岗位需求分析系统 - Startup Script
#  Author : 陈坚卓 @ 广东梅州职业技术学院
#  GitHub : https://github.com/cjz-6
#  Version: 1.0.0  |  2026.05
# ============================================================

echo ""
echo "  [CJZ-BigData] 招聘岗位需求分析系统"
echo "  GitHub  : https://github.com/cjz-6"
echo "  Starting at $(date '+%Y-%m-%d %H:%M:%S')"
echo "  ----------------------------------------"

set -e

cd "$(dirname "$0")/.."
COMPOSE_FILES="-f docker-compose.base.yml"

case "${1:-all}" in
    all)
        COMPOSE_FILES="$COMPOSE_FILES -f docker-compose.hadoop.yml -f docker-compose.services.yml"
        ;;
    hadoop)
        COMPOSE_FILES="$COMPOSE_FILES -f docker-compose.hadoop.yml"
        ;;
    services)
        COMPOSE_FILES="$COMPOSE_FILES -f docker-compose.services.yml"
        ;;
    mysql)
        COMPOSE_FILES="$COMPOSE_FILES -f docker-compose.services.yml"
        docker compose $COMPOSE_FILES up -d mysql
        echo "MySQL started. Waiting for healthy..."
        docker compose $COMPOSE_FILES exec mysql mysqladmin ping -h localhost -u root -p请替换为你的MySQL密码 --wait=30
        exit 0
        ;;
    spark)
        COMPOSE_FILES="$COMPOSE_FILES -f docker-compose.services.yml"
        docker compose $COMPOSE_FILES up -d spark-master spark-worker
        exit 0
        ;;
    backend)
        COMPOSE_FILES="$COMPOSE_FILES -f docker-compose.services.yml"
        docker compose $COMPOSE_FILES up -d --build backend
        exit 0
        ;;
    frontend)
        COMPOSE_FILES="$COMPOSE_FILES -f docker-compose.services.yml"
        docker compose $COMPOSE_FILES up -d --build frontend
        exit 0
        ;;
    dify)
        COMPOSE_FILES="$COMPOSE_FILES -f docker-compose.services.yml"
        docker compose $COMPOSE_FILES up -d dify-db dify-redis dify-api dify-worker dify-web
        exit 0
        ;;
    *)
        echo "用法: $0 [all|hadoop|services|mysql|spark|backend|frontend|dify]"
        exit 1
        ;;
esac

echo "Starting services with: $COMPOSE_FILES"
docker compose $COMPOSE_FILES up -d --build

echo ""
echo "=== 服务状态 ==="
docker compose $COMPOSE_FILES ps
echo ""
echo "=== 清理旧镜像 ==="
docker image prune -f
echo ""
echo "=== 访问地址 ==="
echo "  Hadoop HDFS:    http://localhost:9870"
echo "  YARN:           http://localhost:8088"
echo "  Spark Master:   http://localhost:8082"
echo "  Flask API:      http://localhost:5000/api/health"
echo "  Vue 前端:       http://localhost:3000"
echo "  Dify AI:        http://localhost:8080"
echo "  MySQL:          localhost:3306"
