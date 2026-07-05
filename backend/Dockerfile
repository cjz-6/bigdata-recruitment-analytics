FROM python:3.11-slim

LABEL maintainer="陈坚卓"
LABEL org.opencontainers.image.authors="陈坚卓"
LABEL org.opencontainers.image.version="1.0.0"
LABEL org.opencontainers.image.vendor="MZVTC-2023"

WORKDIR /app

# 安装系统依赖
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc default-libmysqlclient-dev pkg-config curl \
    && rm -rf /var/lib/apt/lists/*

# 安装 Python 依赖
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple

# 复制应用代码
COPY . .

# 暴露端口
EXPOSE 5000

# 启动 Flask 应用
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "4", "--timeout", "120", "app.main:app"]
