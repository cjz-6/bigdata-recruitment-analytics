from app.main import db
from datetime import datetime


class JobsRaw(db.Model):
    __tablename__ = 'jobs_raw'

    id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    job_title = db.Column(db.String(255), nullable=False)
    company = db.Column(db.String(255), nullable=False)
    city = db.Column(db.String(100), nullable=False, index=True)
    salary_raw = db.Column(db.String(100))
    salary_min = db.Column(db.Numeric(12, 2))
    salary_max = db.Column(db.Numeric(12, 2))
    experience = db.Column(db.String(50))
    education = db.Column(db.String(50))
    skills = db.Column(db.Text)
    crawl_time = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    source = db.Column(db.String(50))
    job_url = db.Column(db.String(500))
    enterprise_type = db.Column(db.String(50))


class StatCityDemand(db.Model):
    __tablename__ = 'stat_city_demand'

    id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    city = db.Column(db.String(100), nullable=False)
    job_count = db.Column(db.Integer, default=0)
    avg_salary = db.Column(db.Numeric(12, 2))
    stat_date = db.Column(db.Date, nullable=False)


class StatSkillFreq(db.Model):
    __tablename__ = 'stat_skill_freq'

    id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    skill = db.Column(db.String(100), nullable=False)
    frequency = db.Column(db.Integer, default=0)
    percentage = db.Column(db.Numeric(5, 2))
    stat_date = db.Column(db.Date, nullable=False)


class StatSalaryDist(db.Model):
    __tablename__ = 'stat_salary_dist'

    id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    salary_range = db.Column(db.String(50), nullable=False)
    range_min = db.Column(db.Numeric(12, 2), nullable=False)
    range_max = db.Column(db.Numeric(12, 2), nullable=False)
    job_count = db.Column(db.Integer, default=0)
    percentage = db.Column(db.Numeric(5, 2))
    stat_date = db.Column(db.Date, nullable=False)


class StatEduSalary(db.Model):
    __tablename__ = 'stat_edu_salary'

    id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    education = db.Column(db.String(50), nullable=False)
    avg_salary = db.Column(db.Numeric(12, 2))
    min_salary = db.Column(db.Numeric(12, 2))
    max_salary = db.Column(db.Numeric(12, 2))
    job_count = db.Column(db.Integer, default=0)
    stat_date = db.Column(db.Date, nullable=False)
