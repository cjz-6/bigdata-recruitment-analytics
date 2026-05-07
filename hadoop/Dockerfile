FROM openeuler/openeuler:24.03

LABEL maintainer="陈坚卓"
LABEL org.opencontainers.image.authors="陈坚卓"
LABEL org.opencontainers.image.version="1.0.0"
LABEL org.opencontainers.image.vendor="MZVTC-2023"

#安装依赖（使用系统包管理器安装 OpenJDK 11，避免失效的外部下载链接）
RUN dnf install -y wget tar openssh tzdata java-11-openjdk && \
    yum clean all && \
    ln -sf /usr/share/zoneinfo/Asia/Shanghai /etc/localtime && \
    echo "Asia/Shanghai" > /etc/timezone && \
    ln -s $(dirname $(dirname $(readlink -f $(which java)))) /usr/local/jdk11

#安装Hadoop
RUN wget https://dlcdn.apache.org/hadoop/common/hadoop-3.4.2/hadoop-3.4.2.tar.gz && \
	tar -xvf hadoop-3.4.2.tar.gz -C /usr/local/ && \
	mv /usr/local/hadoop-3.4.2 /usr/local/hadoop3.4.2 && \
	rm -f hadoop-3.4.2.tar.gz

# 配置环境变量
ENV JAVA_HOME=/usr/local/jdk11
ENV HADOOP_HOME=/usr/local/hadoop3.4.2
ENV PATH=$PATH:$JAVA_HOME/bin:$HADOOP_HOME/bin:$HADOOP_HOME/sbin
ENV HDFS_NAMENODE_USER="root"
ENV HDFS_DATANODE_USER="root"
ENV HDFS_SECONDARYNAMENODE_USER="root"
ENV YARN_RESOURCEMANAGER_USER="root"
ENV YARN_NODEMANAGER_USER="root"
ENV HADOOP_CONF_DIR=$HADOOP_HOME/etc/hadoop

# 创建配置目录
RUN mkdir -p /usr/local/hadoop3.4.2/dfs/name && \
    mkdir -p /usr/local/hadoop3.4.2/dfs/data && \
    mkdir -p /usr/local/hadoop3.4.2/tmp

# 配置SSH免密登录，关闭严格的主机密钥检查，不记录已知主机信息
RUN ssh-keygen -t rsa -f ~/.ssh/id_rsa -P '' && \
    cat ~/.ssh/id_rsa.pub >> ~/.ssh/authorized_keys && \
    chmod 600 ~/.ssh/authorized_keys && \
    echo "StrictHostKeyChecking no" >> /etc/ssh/ssh_config && \
    echo "UserKnownHostsFile /dev/null" >> /etc/ssh/ssh_config

# 暴露HDFS端口
EXPOSE 9870 9820 9000
# 暴露YARN端口
EXPOSE 8088 8032 8030 8031 8033 8040 8042
# 暴露SSH端口
EXPOSE 22

# 复制配置文件和启动脚本
COPY config/* $HADOOP_HOME/etc/hadoop/
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh
# 确保SSH服务启动
CMD ["/usr/sbin/sshd", "-D"]
ENTRYPOINT ["/entrypoint.sh"]
