"""
系统配置文件
配置模块 - 集中管理项目配置参数
"""
from dataclasses import dataclass
from typing import Optional


@dataclass
class SearchConfig:
    """搜索配置类"""
    timeout: int = 30
    max_retries: int = 3
    max_workers: int = 5  # 最大线程数
    delay_between_requests: float = 0.2  # 请求间延迟(秒)
    use_proxy: bool = False
    proxy: Optional[str] = None


@dataclass
class MysqlConfig:
    """Mysql数据库连接配置类"""
    host: str = "localhost"
    user: str = "root"
    password: str = "lfq1314520"
    database: str = "patent"
    port: int = 3306
    charset: str = "utf8"
    use_unicode: bool = False
