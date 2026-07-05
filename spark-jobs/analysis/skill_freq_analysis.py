"""
PySpark 分析任务2：技能词频统计
从 jobs_raw 的 skills 字段中提取技能，统计出现频率
"""
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, count, explode, from_json, current_date, lit, round as spark_round
from pyspark.sql.types import ArrayType, StringType
import os

MYSQL_URL = f"jdbc:mysql://{os.getenv('MYSQL_HOST', 'mysql')}:3306/{os.getenv('MYSQL_DATABASE', 'job_analysis')}"
MYSQL_PROPS = {
    'user': os.getenv('MYSQL_USER', 'bigdata'),
    'password': os.getenv('MYSQL_PASSWORD', '请替换为你的MySQL密码'),
    'driver': 'com.mysql.cj.jdbc.Driver',
}

spark = SparkSession.builder \
    .appName('SkillFreqAnalysis') \
    .config('spark.jars', '/opt/spark-jars/mysql-connector-j-8.3.0.jar') \
    .getOrCreate()

df = spark.read.jdbc(MYSQL_URL, 'jobs_raw', properties=MYSQL_PROPS)

# 解析 skills JSON 数组
skills_df = df.withColumn('skill_list', from_json(col('skills'), ArrayType(StringType()))) \
    .select(explode(col('skill_list')).alias('skill')) \
    .filter(col('skill').isNotNull() & (col('skill') != ''))

# 统计频率
total = skills_df.count()
result = skills_df.groupBy('skill').agg(count('*').alias('frequency')) \
    .withColumn('percentage', spark_round(col('frequency') / lit(total) * 100, 2)) \
    .withColumn('stat_date', current_date()) \
    .orderBy(col('frequency').desc())

result.write.jdbc(MYSQL_URL, 'stat_skill_freq', mode='overwrite', properties=MYSQL_PROPS)

print(f'[SkillFreq] Wrote {result.count()} rows')
spark.stop()
