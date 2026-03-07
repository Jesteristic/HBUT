import atexit
import threading
from threading import Lock, Event
from typing import Dict, Any, Optional
from loguru import logger
import blackboxprotobuf
from configs import SearchConfig
from curl_cffi import requests


class WangFangBase:
    def __init__(
            self,
            config: Optional[SearchConfig] = None,
            cookies: Optional[Dict] = None
    ):
        """
        初始化搜索器

        Args:
            config: 搜索配置
            cookies: Cookie字典
        """
        self.config = config or SearchConfig()
        self._cookies = cookies or {}
        self._shutdown_event = Event()  # 添加关闭事件

        # 模板十六进制字符串
        self.TEMPLATE_HEX_STRING = ''

        # 基本配置
        self.BASE_URL = "https://s.wanfangdata.com.cn"

        # 存储所有线程的 session
        self._sessions = {}  # 存储所有session
        self._sessions_lock = Lock()  # 保护 sessions 的锁
        self._cleanup_lock = Lock()  # 清理锁

        # 消息类型缓存
        self._message_type = None
        self._message_type_lock = Lock()

        # 注册清理函数
        atexit.register(self.close)

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

    def _get_thread_session(self) -> requests.Session:
        """获取当前线程的会话（线程安全）"""
        thread_id = threading.get_ident()

        # 如果搜索器正在关闭，不再创建新session
        if self._shutdown_event.is_set():
            raise RuntimeError("搜索器正在关闭，无法创建新会话")

        with self._sessions_lock:
            if thread_id not in self._sessions:
                session = requests.Session()
                self._sessions[thread_id] = session
                return session
            return self._sessions[thread_id]

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

    def close(self):
        """关闭搜索器，清理资源"""
        if self._shutdown_event.is_set():
            return

        with self._cleanup_lock:
            if not self._shutdown_event.is_set():
                self._shutdown_event.set()
                logger.info("开始关闭线程...")

                # 清理所有 session
                with self._sessions_lock:
                    closed_count = 0
                    for thread_id, session in self._sessions.items():
                        try:
                            session.close()
                            closed_count += 1
                        except Exception as e:
                            logger.warning(f"关闭线程 {thread_id} 的 session 时出错: {e}")
                    self._sessions.clear()
                    logger.info(f"已关闭 {closed_count} 个 session")

                # 注销 atexit 注册
                atexit.unregister(self.close)
                logger.info("线程已完全关闭")

    def _make_request(self, *args, **kwargs):
        pass

    def __enter__(self):
        """上下文管理器入口"""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """上下文管理器退出"""
        self.close()
