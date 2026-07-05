import scrapy


class JobItem(scrapy.Item):
    job_title = scrapy.Field()      # 岗位名称
    company = scrapy.Field()        # 公司名称
    city = scrapy.Field()           # 城市
    salary_raw = scrapy.Field()     # 原始薪资字符串
    salary_min = scrapy.Field()     # 最低薪资
    salary_max = scrapy.Field()     # 最高薪资
    experience = scrapy.Field()     # 工作经验
    education = scrapy.Field()      # 学历要求
    skills = scrapy.Field()         # 技能要求
    source = scrapy.Field()         # 数据来源
    job_url = scrapy.Field()        # 岗位链接
    crawl_time = scrapy.Field()     # 爬取时间
    enterprise_type = scrapy.Field() # 企业类型（专精特新/小巨人/高新技术企业）
