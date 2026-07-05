import json
import pymysql
from datetime import datetime


class MySQLPipeline:
    """将爬取的岗位数据写入 MySQL"""

    def __init__(self, host, port, user, password, database):
        self.host = host
        self.port = port
        self.user = user
        self.password = password
        self.database = database

    @classmethod
    def from_crawler(cls, crawler):
        return cls(
            host=crawler.settings.get('MYSQL_HOST', 'mysql'),
            port=crawler.settings.getint('MYSQL_PORT', 3306),
            user=crawler.settings.get('MYSQL_USER', 'bigdata'),
            password=crawler.settings.get('MYSQL_PASSWORD', '请替换为你的MySQL密码'),
            database=crawler.settings.get('MYSQL_DATABASE', 'job_analysis'),
        )

    def open_spider(self, spider):
        self.conn = pymysql.connect(
            host=self.host, port=self.port,
            user=self.user, password=self.password,
            database=self.database, charset='utf8mb4'
        )
        self.cursor = self.conn.cursor()
        # 加载已有记录用于去重
        self.cursor.execute("SELECT job_title, company, city FROM jobs_raw")
        self.seen = set(self.cursor.fetchall())

    def close_spider(self, spider):
        self.conn.close()

    def process_item(self, item, spider):
        skills = item.get('skills')
        if isinstance(skills, list):
            skills = json.dumps(skills, ensure_ascii=False)

        title = (item.get('job_title', '') or '')[:255]
        company = (item.get('company', '') or '')[:255]
        city = (item.get('city', '') or '')[:100]
        dedup_key = (title, company, city)
        if dedup_key in self.seen:
            return item
        self.seen.add(dedup_key)

        sql = """
            INSERT INTO jobs_raw
            (job_title, company, city, salary_raw, salary_min, salary_max,
             experience, education, skills, source, job_url, crawl_time, enterprise_type)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        self.cursor.execute(sql, (
            title, company, city,
            (item.get('salary_raw') or '')[:100],
            item.get('salary_min'),
            item.get('salary_max'),
            (item.get('experience') or '')[:50],
            (item.get('education') or '')[:50],
            skills,
            (item.get('source') or '')[:50],
            (item.get('job_url') or '')[:500],
            item.get('crawl_time', datetime.now()),
            (item.get('enterprise_type') or '')[:50],
        ))
        self.conn.commit()
        return item
