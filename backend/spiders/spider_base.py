import threading
from threading import Lock
from typing import Dict, Optional
from loguru import logger
import blackboxprotobuf
from ..configs import CrawlerConfig, MysqlConfig
from ..sql.sql_tools import RedisUtils, MysqlUtils


class WangFangBase(threading.Thread):
    def __init__(self, config: Optional[CrawlerConfig] = None):
        """
        初始化搜索器

        Args:
            config: 搜索配置
        """
        super().__init__()
        self.config = config or CrawlerConfig()

        # 用于外部停止线程的事件
        self._stop_event = threading.Event()

        # 基本配置
        # 消息类型缓存
        self._message_type = None
        self._message_type_lock = Lock()
        self.redis = None
        # Redis实例
        for _ in range(config.max_retries):
            try:
                self.redis = RedisUtils()
                break
            except Exception as e:
                logger.warning(f"Redis 第{config.max_retries + 1}次初始化失败: {e}")
        self.REDIS_TASK_LIST_KEY = "wanfang:task_queue"
        # 管理后台推送生产者搜索任务的 Redis 列表
        self.REDIS_PRODUCER_TASK_KEY = "wanfang:producer_tasks"

        # 如果 Mysql 连接已建立，则注册日志写入 MySQL 的 sink
        if hasattr(self, 'mysql') and self.mysql:
            self._init_mysql_logging(self.mysql)

        # Mysql实例
        self.mysql = None
        for _ in range(config.max_retries):
            try:
                self.mysql = MysqlUtils(host=MysqlConfig.host, port=MysqlConfig.port, user=MysqlConfig.user,
                                        password=MysqlConfig.password, database=MysqlConfig.database,
                                        charset=MysqlConfig.charset)
                break
            except Exception as e:
                logger.warning(f"Mysql 第{config.max_retries + 1}次初始化失败: {e}")

    @property
    def headers(self) -> Dict[str, str]:
        """获取请求头"""
        headers = {
            "accept": "*/*",
            "accept-language": "zh-CN,zh;q=0.9,zh-TW;q=0.8",
            "content-type": "application/grpc-web+proto",
            "cookies": "CASTGC=;CASTGCSpecial=;",
            "httphost": "s.wanfangdata.com.cn",
            "httpreferer": "https://s.wanfangdata.com.cn/patent?q=%E5%88%86%E7%B1%BB%E5%8F%B7%3AA01%20%20%E6%A4%8D%E7%89%A9",
            "origin": "https://s.wanfangdata.com.cn",
            "priority": "u=1, i",
            "referer": "https://s.wanfangdata.com.cn/patent?q=%E5%88%86%E7%B1%BB%E5%8F%B7%3AA01%20%20%E6%A4%8D%E7%89%A9&p=5",
            "sec-ch-ua": "\"Not:A-Brand\";v=\"99\", \"Microsoft Edge\";v=\"145\", \"Chromium\";v=\"145\"",
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": "\"Windows\"",
            "sec-fetch-dest": "empty",
            "sec-fetch-mode": "cors",
            "sec-fetch-site": "same-origin",
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/145.0.0.0 Safari/537.36 Edg/145.0.0.0",
            "x-grpc-web": "1",
            "x-user-agent": "grpc-web-javascript/0.1"
        }
        return headers

    def _get_message_type(self) -> Dict:
        """获取消息类型（线程安全缓存）"""
        with self._message_type_lock:
            if self._message_type is None:
                try:
                    byte_string = bytes.fromhex(self.TEMPLATE_HEX_STRING.replace(" ", ""))
                    _, self._message_type = blackboxprotobuf.protobuf_to_json(byte_string)
                    logger.info("消息类型解析完成并缓存")
                except Exception as e:
                    logger.error(f"解析消息类型失败: {e}")
                    raise
        return self._message_type

    def construct_protobuf(self, *args, **kwargs) -> bytes:
        '''
        构造搜索请求的 protobuf 数据

        Args:
            ...

        Returns:
            protobuf 字节数据
        '''
        pass

    def _make_request(self, *args, **kwargs):
        pass

    def __enter__(self):
        """上下文管理器入口"""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """上下文管理器退出"""
        self.close()

    def stop(self):
        """通知线程停止运行"""
        self._stop_event.set()

    @classmethod
    def _init_mysql_logging(cls, mysql_util):
        """为 loguru 增加一个 sink，把每条日志写入 spider_logs 表。

        该方法只会执行一次。"""
        if getattr(cls, "_mysql_logging_initialized", False):
            return
        from datetime import datetime

        def _mysql_sink(message):
            record = message.record
            extra = record.get("extra", {})
            data = {
                "spider_name": record.get("name", ""),
                "action": extra.get("action"),
                "keyword": extra.get("keyword"),
                "page": extra.get("page"),
                "task_id": extra.get("task_id"),
                "status": record.get("level").name,
                "error_msg": record.get("exception") and str(record.get("exception")) or None,
                "details": record.get("message"),
                "task_ids": extra.get("task_ids"),
                "patent_id": extra.get("patent_id"),
                "log_time": datetime.fromtimestamp(record.get("time").timestamp()),
                "created_at": datetime.now(),
            }
            try:
                mysql_util.insert("spider_logs", data)
            except Exception:
                pass

        logger.add(_mysql_sink, level="DEBUG", enqueue=True)
        cls._mysql_logging_initialized = True
