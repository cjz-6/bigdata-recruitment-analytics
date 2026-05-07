"""
PySpark 分析任务3：薪资分布统计
将薪资划分为多个区间，统计每个区间的岗位数量，
结果写入 stat_salary_dist 表
"""
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, count, when, current_date, lit, round as spark_round, monotonically_increasing_id
from pyspark.sql.types import LongType
import os

MYSQL_URL = f"jdbc:mysql://{os.getenv('MYSQL_HOST', 'mysql')}:3306/{os.getenv('MYSQL_DATABASE', 'job_analysis')}"
MYSQL_PROPS = {
    'user': os.getenv('MYSQL_USER', 'bigdata'),
    'password': os.getenv('MYSQL_PASSWORD', '请替换为你的MySQL密码'),
    'driver': 'com.mysql.cj.jdbc.Driver',
}

SALARY_RANGES = [
    ('3K以下', 0, 3000),
    ('3K-5K', 3000, 5000),
    ('5K-10K', 5000, 10000),
    ('10K-15K', 10000, 15000),
    ('15K-20K', 15000, 20000),
    ('20K-30K', 20000, 30000),
    ('30K-50K', 30000, 50000),
    ('50K以上', 50000, 999999),
]

spark = SparkSession.builder \
    .appName('SalaryDistAnalysis') \
    .getOrCreate()

df = spark.read.jdbc(MYSQL_URL, 'jobs_raw', properties=MYSQL_PROPS) \
    .filter(col('salary_min').isNotNull() & col('salary_max').isNotNull())

df = df.withColumn('avg_salary', (col('salary_min') + col('salary_max')) / 2)

total = df.count()
case_expr = None
for label, low, high in SALARY_RANGES:
    condition = when((col('avg_salary') >= low) & (col('avg_salary') < high), lit(label))
    case_expr = condition if case_expr is None else case_expr.otherwise(condition)

df = df.withColumn('salary_range', case_expr)

result = df.groupBy('salary_range').agg(count('*').alias('job_count')) \
    .withColumn('percentage', spark_round(col('job_count') / lit(total) * 100, 2))

# 添加区间上下限
range_map = spark.createDataFrame(SALARY_RANGES, ['salary_range', 'range_min', 'range_max'])
result = result.join(range_map, 'salary_range', 'left') \
    .withColumn('id', monotonically_increasing_id().cast(LongType())) \
    .withColumn('stat_date', current_date()) \
    .select('id', 'salary_range', 'range_min', 'range_max', 'job_count', 'percentage', 'stat_date')

result.write.jdbc(MYSQL_URL, 'stat_salary_dist', mode='overwrite', properties=MYSQL_PROPS)

print(f'[SalaryDist] Wrote {result.count()} rows')
spark.stop()
