import threading
from threading import Lock, Thread
from typing import Dict, Optional
from loguru import logger
import blackboxprotobuf
from configs import CrawlerConfig
from sql.sql_tools import RedisUtils


class WangFangBase(threading.Thread):
    def __init__(self, config: Optional[CrawlerConfig] = None):
        """
        初始化搜索器

        Args:
            config: 搜索配置
        """
        super().__init__()
        self.config = config or CrawlerConfig()

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
