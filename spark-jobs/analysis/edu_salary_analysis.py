"""
PySpark 分析任务4：学历与薪资关系统计
按学历分组，统计平均薪资、最低薪资、最高薪资和岗位数量，
结果写入 stat_edu_salary 表
"""
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, count, avg, min, max, current_date, monotonically_increasing_id
from pyspark.sql.types import LongType
import os

MYSQL_URL = f"jdbc:mysql://{os.getenv('MYSQL_HOST', 'mysql')}:3306/{os.getenv('MYSQL_DATABASE', 'job_analysis')}"
MYSQL_PROPS = {
    'user': os.getenv('MYSQL_USER', 'bigdata'),
    'password': os.getenv('MYSQL_PASSWORD', '请替换为你的MySQL密码'),
    'driver': 'com.mysql.cj.jdbc.Driver',
}

spark = SparkSession.builder \
    .appName('EduSalaryAnalysis') \
    .getOrCreate()

df = spark.read.jdbc(MYSQL_URL, 'jobs_raw', properties=MYSQL_PROPS) \
    .filter(col('education').isNotNull() & (col('education') != '')) \
    .filter(col('salary_min').isNotNull() & col('salary_max').isNotNull())

df = df.withColumn('avg_salary', (col('salary_min') + col('salary_max')) / 2)

result = df.groupBy('education').agg(
    count('*').alias('job_count'),
    avg('avg_salary').alias('avg_salary'),
    min('salary_min').alias('min_salary'),
    max('salary_max').alias('max_salary'),
).withColumn('id', monotonically_increasing_id().cast(LongType())) \
 .withColumn('stat_date', current_date()) \
 .select('id', 'education', 'avg_salary', 'min_salary', 'max_salary', 'job_count', 'stat_date') \
 .orderBy(col('avg_salary').desc())

result.write.jdbc(MYSQL_URL, 'stat_edu_salary', mode='overwrite', properties=MYSQL_PROPS)

print(f'[EduSalary] Wrote {result.count()} rows')
spark.stop()
