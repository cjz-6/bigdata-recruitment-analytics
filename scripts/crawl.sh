#!/bin/bash
# 运行 Scrapy 爬虫
cd "$(dirname "$0")/.."
SPIDER="${1:-jobs}"

echo "Running Scrapy spider: ${SPIDER}"
# 爬虫通过 docker 运行（需要自行构建爬虫镜像或在宿主机运行）
cd crawler && scrapy crawl "${SPIDER}" && cd ..
echo "Crawl complete."
