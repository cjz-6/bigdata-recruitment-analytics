#!/usr/bin/env python3
"""
PySpark 岗位数据分析脚本
从 MySQL jobs_raw 读取数据，分析后写入 4 张统计表
表结构与 SQLAlchemy 模型一致
"""
from pyspark.sql import SparkSession
import builtins
from pyspark.sql.functions import (
    col, count, avg, min, max as spark_max, round as spark_round,
    explode, split, when, lit, current_date, monotonically_increasing_id
)
from pyspark.sql.types import DecimalType
import json

MYSQL_URL = "jdbc:mysql://cjz-mysql:3306/job_analysis"
MYSQL_PROPS = {
    "user": "root",
    "password": "请替换为你的MySQL密码",
    "driver": "com.mysql.cj.jdbc.Driver",
}

def main():
    spark = SparkSession.builder \
        .appName("JobAnalysis") \
        .getOrCreate()

    df = spark.read.jdbc(MYSQL_URL, "jobs_raw", properties=MYSQL_PROPS)
    df = df.filter(col("source") == "51job")
    df.cache()
    total = df.count()
    print(f"[Analysis] Total records: {total}")

    if total == 0:
        print("[Analysis] No data, skipping.")
        spark.stop()
        return

    today = current_date()

    # ─── 1. 城市需求统计 ───
    city_df = df.filter(col("city").isNotNull() & (col("city") != "")) \
        .withColumn("city_short",
            when(col("city").contains("·"), split(col("city"), "·").getItem(0))
            .otherwise(col("city"))) \
        .groupBy("city_short") \
        .agg(
            count("*").alias("job_count"),
            spark_round(avg("salary_max"), 2).alias("avg_salary"),
        ) \
        .withColumnRenamed("city_short", "city") \
        .withColumn("id", monotonically_increasing_id()) \
        .withColumn("stat_date", today) \
        .select("id", "city", "job_count", "avg_salary", "stat_date") \
        .orderBy(col("job_count").desc())

    city_df.write.mode("overwrite").jdbc(MYSQL_URL, "stat_city_demand", properties=MYSQL_PROPS)
    print(f"[Analysis] stat_city_demand: {city_df.count()} rows")

    # ─── 2. 技能频率统计 ───
    from pyspark.sql.functions import udf
    from pyspark.sql.types import ArrayType, StringType

    def parse_skills(skills_str):
        if not skills_str or skills_str == "[]":
            return []
        try:
            return json.loads(skills_str)
        except:
            return []

    parse_skills_udf = udf(parse_skills, ArrayType(StringType()))

    total_with_skills = df.filter(col("skills").isNotNull() & (col("skills") != "[]")).count()

    skills_df = df.filter(col("skills").isNotNull() & (col("skills") != "[]")) \
        .withColumn("skill", explode(parse_skills_udf(col("skills")))) \
        .groupBy("skill") \
        .agg(count("*").alias("frequency")) \
        .withColumn("percentage", spark_round(col("frequency") / lit(total_with_skills) * 100, 2)) \
        .withColumn("id", monotonically_increasing_id()) \
        .withColumn("stat_date", today) \
        .select("id", "skill", "frequency", "percentage", "stat_date") \
        .orderBy(col("frequency").desc())

    skills_df.write.mode("overwrite").jdbc(MYSQL_URL, "stat_skill_freq", properties=MYSQL_PROPS)
    print(f"[Analysis] stat_skill_freq: {skills_df.count()} rows")

    # ─── 3. 薪资分布统计 ───
    ranges = [
        ("0-5K", 0, 5000), ("5K-10K", 5000, 10000),
        ("10K-15K", 10000, 15000), ("15K-20K", 15000, 20000),
        ("20K-30K", 20000, 30000), ("30K+", 30000, 999999),
    ]

    salary_rows = []
    for label, rmin, rmax in ranges:
        cnt = df.filter(
            (col("salary_min") >= rmin) & (col("salary_max") <= rmax)
        ).count()
        salary_rows.append((label, float(rmin), float(rmax), cnt))

    sal_df = spark.createDataFrame(salary_rows, ["salary_range", "range_min", "range_max", "job_count"])
    total_salary = builtins.max(sum(r[3] for r in salary_rows), 1)
    sal_df = sal_df.withColumn("percentage",
        spark_round(col("job_count") / lit(total_salary) * 100, 2)) \
        .withColumn("id", monotonically_increasing_id()) \
        .withColumn("stat_date", today) \
        .select("id", "salary_range", "range_min", "range_max", "job_count", "percentage", "stat_date")

    sal_df.write.mode("overwrite").jdbc(MYSQL_URL, "stat_salary_dist", properties=MYSQL_PROPS)
    print(f"[Analysis] stat_salary_dist: {sal_df.count()} rows")

    # ─── 4. 学历薪资统计 ───
    edu_df = df.filter(
        col("education").isNotNull() & (col("education") != "") &
        col("salary_min").isNotNull()
    ) \
        .groupBy("education") \
        .agg(
            count("*").alias("job_count"),
            spark_round(avg("salary_max"), 2).alias("avg_salary"),
            spark_round(min("salary_min"), 2).alias("min_salary"),
            spark_round(spark_max("salary_max"), 2).alias("max_salary"),
        ) \
        .withColumn("id", monotonically_increasing_id()) \
        .withColumn("stat_date", today) \
        .select("id", "education", "avg_salary", "min_salary", "max_salary", "job_count", "stat_date") \
        .orderBy(col("avg_salary").desc())

    edu_df.write.mode("overwrite").jdbc(MYSQL_URL, "stat_edu_salary", properties=MYSQL_PROPS)
    print(f"[Analysis] stat_edu_salary: {edu_df.count()} rows")

    df.unpersist()
    spark.stop()
    print("[Analysis] Done!")

if __name__ == "__main__":
    main()
