export JAVA_HOME=/usr/local/jdk11
export HADOOP_HOME=/usr/local/hadoop3.4.2
export HADOOP_CONF_DIR=$HADOOP_HOME/etc/hadoop

# 时区配置
export TZ=Asia/Shanghai

# 解决root用户启动问题
export HDFS_NAMENODE_USER=root
export HDFS_DATANODE_USER=root
export HDFS_SECONDARYNAMENODE_USER=root
export YARN_RESOURCEMANAGER_USER=root
export YARN_NODEMANAGER_USER=root

# 内存配置优化
export HADOOP_HEAPSIZE=1024
export HADOOP_NAMENODE_INIT_HEAPSIZE=1024

# 日志目录
export HADOOP_LOG_DIR=${HADOOP_HOME}/logs
export YARN_LOG_DIR=${HADOOP_HOME}/logs
