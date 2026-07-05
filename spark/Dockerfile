FROM apache/spark:3.5.3

LABEL maintainer="陈坚卓"
LABEL org.opencontainers.image.authors="陈坚卓"
LABEL org.opencontainers.image.version="1.0.0"
LABEL org.opencontainers.image.vendor="MZVTC-2023"

USER root

# 安装 Python3 和 pip
RUN apt-get update && apt-get install -y --no-install-recommends \
    python3 python3-pip python3-dev curl \
    && ln -s /usr/bin/python3 /usr/bin/python \
    && rm -rf /var/lib/apt/lists/*

# 安装 PySpark 和依赖
RUN pip3 install --no-cache-dir pyspark==3.5.3 pymysql==1.1.1 pandas==2.0.3 \
    -i https://pypi.tuna.tsinghua.edu.cn/simple

# 下载 MySQL JDBC 驱动
RUN curl -L -o /opt/spark/jars/mysql-connector-j-8.3.0.jar \
    https://repo1.maven.org/maven2/com/mysql/mysql-connector-j/8.3.0/mysql-connector-j-8.3.0.jar

# 创建 Hadoop 配置目录
RUN mkdir -p /opt/spark/conf/hadoop

COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

ENV SPARK_HOME=/opt/spark
ENV PATH=$PATH:$SPARK_HOME/bin:$SPARK_HOME/sbin

ENTRYPOINT ["/entrypoint.sh"]
