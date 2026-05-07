"""
PySpark 分析任务1：城市岗位需求统计
读取 MySQL 中的 jobs_raw 表，按城市聚合岗位数量和平均薪资，
结果写入 stat_city_demand 表
"""
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, count, avg, current_date, monotonically_increasing_id, round as spark_round
from pyspark.sql.types import LongType
import os

MYSQL_URL = f"jdbc:mysql://{os.getenv('MYSQL_HOST', 'mysql')}:3306/{os.getenv('MYSQL_DATABASE', 'job_analysis')}"
MYSQL_PROPS = {
    'user': os.getenv('MYSQL_USER', 'bigdata'),
    'password': os.getenv('MYSQL_PASSWORD', '请替换为你的MySQL密码'),
    'driver': 'com.mysql.cj.jdbc.Driver',
}

spark = SparkSession.builder \
    .appName('CityDemandAnalysis') \
    .getOrCreate()

# 读取原始数据
df = spark.read.jdbc(MYSQL_URL, 'jobs_raw', properties=MYSQL_PROPS)

# 按城市聚合，输出字段与 SQLAlchemy 模型一致（id, city, job_count, avg_salary, stat_date）
result = df.groupBy('city').agg(
    count('*').alias('job_count'),
    spark_round(avg((col('salary_min') + col('salary_max')) / 2), 2).alias('avg_salary')
).withColumn('id', monotonically_increasing_id().cast(LongType())) \
 .withColumn('stat_date', current_date()) \
 .select('id', 'city', 'job_count', 'avg_salary', 'stat_date')

result.write.jdbc(MYSQL_URL, 'stat_city_demand', mode='overwrite', properties=MYSQL_PROPS)

print(f'[CityDemand] Wrote {result.count()} rows')
spark.stop()
