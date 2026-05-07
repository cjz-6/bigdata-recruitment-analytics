#!/bin/bash

# 解决时区问题
ln -sf /usr/share/zoneinfo/Asia/Shanghai /etc/localtime
echo "Asia/Shanghai" > /etc/timezone

# 生成 SSH 主机密钥并启动 SSH（Hadoop 内部通信需要）
ssh-keygen -A 2>/dev/null || true
/usr/sbin/sshd

# 根据容器角色启动不同服务
if [ "$HADOOP_ROLE" = "namenode" ]; then
    # 首次启动格式化NameNode
    if [ ! -d "/usr/local/hadoop3.4.2/dfs/name/current" ]; then
        hdfs namenode -format -force
    fi
    # 启动NameNode
    hdfs --daemon start namenode
elif [ "$HADOOP_ROLE" = "secondarynamenode" ]; then
    # 启动SecondaryNameNode
    hdfs --daemon start secondarynamenode
elif [ "$HADOOP_ROLE" = "datanode" ]; then
    # 启动DataNode
    hdfs --daemon start datanode
elif [ "$HADOOP_ROLE" = "resourcemanager" ]; then
    # 启动ResourceManager
    yarn --daemon start resourcemanager
elif [ "$HADOOP_ROLE" = "nodemanager" ]; then
    # 启动NodeManager
    yarn --daemon start nodemanager
fi

# 保持容器运行
tail -f /dev/null
