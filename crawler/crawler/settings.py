import os
# 清除代理环境变量，让 Playwright 不走系统代理（保留用户终端代理不受影响）
for _var in ('http_proxy', 'https_proxy', 'HTTP_PROXY', 'HTTPS_PROXY', 'ALL_PROXY', 'all_proxy'):
    os.environ.pop(_var, None)

# 加载 .env 文件，使爬虫在宿主机运行时也能读取 .env 中配置的密码
_env_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), '.env')
if os.path.exists(_env_path):
    with open(_env_path) as _f:
        for _line in _f:
            _line = _line.strip()
            if _line and not _line.startswith('#') and '=' in _line:
                _k, _, _v = _line.partition('=')
                _k, _v = _k.strip(), _v.strip().strip('"').strip("'")
                if _k not in os.environ:
                    os.environ[_k] = _v

BOT_NAME = 'crawler'
SPIDER_MODULES = ['crawler.spiders']
NEWSPIDER_MODULE = 'crawler.spiders'

# ─── Playwright 配置 ───
DOWNLOAD_HANDLERS = {
    "http": "scrapy_playwright.handler.ScrapyPlaywrightDownloadHandler",
    "https": "scrapy_playwright.handler.ScrapyPlaywrightDownloadHandler",
}
TWISTED_REACTOR = "twisted.internet.asyncioreactor.AsyncioSelectorReactor"
PLAYWRIGHT_BROWSER_TYPE = "chromium"
PLAYWRIGHT_LAUNCH_OPTIONS = {
    "headless": True,
    "args": [
        "--disable-blink-features=AutomationControlled",
        "--disable-features=IsolateOrigins,site-per-process",
        "--no-sandbox",
        "--no-proxy-server",
    ],
}
PLAYWRIGHT_CONTEXTS = {
    "default": {
        "viewport": {"width": 1920, "height": 1080},
        "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "locale": "zh-CN",
        "timezone_id": "Asia/Shanghai",
    },
}
PLAYWRIGHT_DEFAULT_NAVIGATION_TIMEOUT = 30000

# ─── 反爬配置 ───
ROBOTSTXT_OBEY = False
CONCURRENT_REQUESTS = 1
DOWNLOAD_DELAY = 10
RANDOMIZE_DOWNLOAD_DELAY = True
RETRY_TIMES = 3
RETRY_HTTP_CODES = [500, 502, 503, 504, 408, 429]

# ─── MySQL 配置 ───
MYSQL_HOST = '127.0.0.1'
MYSQL_PORT = 3306
MYSQL_USER = 'bigdata'
MYSQL_PASSWORD = os.getenv('MYSQL_PASSWORD', '请替换为你的MySQL密码')
MYSQL_DATABASE = 'job_analysis'

# ─── Pipeline ───
ITEM_PIPELINES = {
    'crawler.pipelines.MySQLPipeline': 300,
}

# ─── 日志 ───
LOG_LEVEL = 'INFO'
LOG_FORMAT = '%(asctime)s [%(name)s] %(levelname)s: %(message)s'
LOG_DATEFORMAT = '%Y-%m-%d %H:%M:%S'

FEED_EXPORT_ENCODING = 'utf-8'

# ─── Scrapy 默认配置 ───
REQUEST_FINGERPRINTER_IMPLEMENTATION = "2.7"
