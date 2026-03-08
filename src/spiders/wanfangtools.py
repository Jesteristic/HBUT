import blackboxprotobuf
from loguru import logger
from typing import Dict, Any, Optional
import time
from configs import CrawlerConfig
from spiders.spider_base import WangFangBase
from parse_tools import extract_task_ids
from curl_cffi import requests


class WanfangPatentProducer(WangFangBase):
    """万方专利搜索器（单线程版本）"""

    def __init__(self, config: Optional[CrawlerConfig], producerID: int):
        """
        初始化搜索器

        Args:
            config: 搜索配置
        """
        super().__init__(config)
        self.BASE_URL = "https://s.wanfangdata.com.cn/"
        # 模板十六进制字符串
        self.TEMPLATE_HEX_STRING = (
            "0A 25 0A 06 70 61 74 65 6E 74 12 06 E6 A4 8D E7 89 A9 28 01 30 14 "
            "42 01 00 48 01 62 02 70 63 6A 06 73 65 61 72 63 68 10 01 22 07 41 "
            "49 5F 52 45 41 44 22 0A 41 49 5F 45 58 54 52 41 43 54"
        )

        # 基本配置
        self.producerID = producerID
        self.SEARCH_URL = f"{self.BASE_URL}/SearchService.SearchService/search"

        logger.info(f"生产者000{self.producerID}初始化完成")

    def construct_protobuf(self, keyword: str, page: int = 1, page_size: int = 20) -> bytes:
        """
        构造搜索请求的 protobuf 数据

        Args:
            keyword: 搜索关键词
            page: 页码，从1开始
            page_size: 每页数量

        Returns:
            protobuf 字节数据
        """
        try:
            message_type = self._get_message_type()

            # 构造请求数据
            request_data = {
                "1": {
                    "1": "patent",
                    "2": keyword,
                    "5": page,
                    "6": page_size,
                    "8": "\u0000",
                    "9": 1,
                    "12": {"14": 99},
                    "13": "search"
                },
                "2": 1,
                "4": ["AI_READ", "AI_EXTRACT"]
            }

            # 编码消息
            form_data = bytes(blackboxprotobuf.encode_message(request_data, message_type))

            # 添加 GRPC 头部
            protobuf_data = bytes([0, 0, 0, 0, len(form_data)]) + form_data

            return protobuf_data

        except Exception as e:
            logger.error(f"生产者000{self.producerID}:构造 protobuf 数据失败: {e}")
            raise

    def _make_request(self, keyword: str, page: int, page_size: int) -> Optional[Dict[str, Any]]:
        """
        执行单个请求

        Args:
            keyword: 搜索关键词
            page: 页码
            page_size: 每页数量

        Returns:
            搜索结果字典，失败返回 None
        """
        for attempt in range(self.config.max_retries):
            try:
                logger.debug(f"生产者000{self.producerID}:开始搜索--关键词={keyword}, 页码={page}")

                # 构造请求数据
                post_data = self.construct_protobuf(keyword, page, page_size)

                # 发送请求
                start_time = time.time()
                response = requests.post(
                    self.SEARCH_URL,
                    headers=self.headers,
                    data=post_data,
                    timeout=self.config.timeout
                )
                elapsed_time = time.time() - start_time

                # 检查响应状态
                response.raise_for_status()
                logger.debug(
                    f"生产者000{self.producerID}:请求成功--状态码={response.status_code}, 耗时={elapsed_time:.2f}s")

                # 反序列化响应结果
                if len(response.content) > 5:
                    response_data, _ = blackboxprotobuf.protobuf_to_json(response.content[5:])
                    logger.debug(f"生产者000{self.producerID}:解析成功--页码={page}, 数据长度={len(response.content)}")

                    # 解析并实时推送 taskId 到 Redis
                    try:
                        task_ids = extract_task_ids(response_data)
                        if task_ids:
                            if self.redis:
                                try:
                                    # 批量推送到列表
                                    self.redis.rpush(self.REDIS_TASK_LIST_KEY, *task_ids)
                                    logger.info(
                                        f"生产者000{self.producerID}:已将 {len(task_ids)} 个 taskId 推入 Redis 列表 {self.REDIS_TASK_LIST_KEY}")
                                except Exception as e:
                                    logger.warning(f"生产者000{self.producerID}:推送 taskId 到 Redis 失败: {e}")
                            else:
                                logger.warning("生产者000{self.producerID}:Redis 未初始化，无法推送 taskId")
                    except Exception as e:
                        logger.error(f"生产者000{self.producerID}:提取 taskId 并推送到 Redis 时出错: {e}")
                else:
                    logger.warning(
                        f"生产者000{self.producerID}:响应数据过短: 页码--{page}, 长度={len(response.content)}")

            except Exception as e:
                logger.warning(
                    f"生产者000{self.producerID}:请求失败 (尝试 {attempt + 1}/{self.config.max_retries}): {e}")

                if attempt < self.config.max_retries - 1:
                    # 等待后重试
                    time.sleep(1 * (attempt + 1))
                else:
                    logger.error(f"生产者000{self.producerID}--页码 {page} 请求失败，已达到最大重试次数")
                    return None

            # 请求间延迟
            # time.sleep(self.config.delay_between_requests)

    def run(self):
        self._make_request('植物', 1, 50)


class WanfangPatentComsumer(WangFangBase):
    def __init__(self, config: CrawlerConfig, comsumerID: int):
        super().__init__(config)
        # 模板十六进制字符串
        self.TEMPLATE_HEX_STRING = '0A 06 50 61 74 65 6E 74 12 70 43 68 31 51 59 58 52 6C 62 6E 52 4F 5A 58 64 54 62 32 78 79 4F 56 4D 79 4D 44 49 32 4D 44 45 79 4E 7A 45 31 4E 54 45 7A 4F 52 49 70 57 6B 78 66 51 30 34 79 4D 44 49 31 4D 54 45 34 4D 54 55 79 4E 54 45 75 57 46 39 44 54 6A 45 79 4D 54 49 30 4D 54 6B 78 4E 6B 46 66 4D 6A 41 79 4E 6A 41 78 4D 44 49 61 43 47 31 31 59 6E 6B 35 63 48 63 79 3A 07 41 49 5F 52 45 41 44 3A 0A 41 49 5F 45 58 54 52 41 43 54'

        # 基本配置
        self.BASE_URL = 'https://d.wanfangdata.com.cn/'
        self.DETAIL_URL = f"{self.BASE_URL}/Detail.DetailService/getDetailInFormation"

        self.comsumerID = comsumerID

        logger.info(f"000消费者{self.comsumerID}初始化完成")

    def construct_protobuf(self, taskId: str) -> bytes:
        """
        构造搜索请求的 protobuf 数据

        Args:
            keyword: 搜索关键词
            page: 页码，从1开始
            page_size: 每页数量

        Returns:
            protobuf 字节数据
        """
        try:
            message_type = self._get_message_type()

            # 构造请求数据
            request_data = {
                "1": "Patent",
                "2": taskId,
                "7": [
                    "AI_READ",
                    "AI_EXTRACT"
                ]
            }

            # 编码消息
            form_data = bytes(blackboxprotobuf.encode_message(request_data, message_type))

            # 添加 GRPC 头部
            protobuf_data = bytes([0, 0, 0, 0, len(form_data)]) + form_data

            return protobuf_data

        except Exception as e:
            logger.error(f"消费者000{self.comsumerID}--构造 protobuf 数据失败: {e}")
            raise

    def _make_request(self, taskId) -> Optional[Dict[str, Any]]:
        """
        执行单个请求

        Returns:
            搜索结果字典，失败返回 None
        """
        for attempt in range(self.config.max_retries):
            try:
                # 构造请求数据
                post_data = self.construct_protobuf(taskId)

                # 发送请求
                start_time = time.time()
                response = requests.post(
                    self.DETAIL_URL,
                    headers=self.headers,
                    data=post_data,
                    timeout=self.config.timeout
                )
                elapsed_time = time.time() - start_time

                # 检查响应状态
                response.raise_for_status()
                logger.debug(
                    f"消费者000{self.comsumerID}:请求成功--状态码={response.status_code}, 耗时={elapsed_time:.2f}s")

                # 反序列化响应结果
                response_data = {}
                if len(response.content) > 5:
                    response_data, _ = blackboxprotobuf.protobuf_to_json(response.content[5:])
                logger.debug(f"消费者000{self.comsumerID}:解析成功--taskId={taskId}, 数据长度={len(response.content)}")
                return response_data

            except Exception as e:
                logger.warning(
                    f"消费者000{self.comsumerID}:请求失败 (尝试 {attempt + 1}/{self.config.max_retries}): {e}")

                if attempt < self.config.max_retries - 1:
                    # 等待后重试
                    time.sleep(1 * (attempt + 1))
                else:
                    logger.error(f"消费者000{self.comsumerID}--{taskId} 请求失败，已达到最大重试次数")
                    return None

            # 请求间延迟
            # time.sleep(self.config.delay_between_requests)

    def run(self):
        taskId = self.redis.lindex(self.REDIS_TASK_LIST_KEY, 0).decode().replace("%3D", "=")
        logger.debug(f"消费者000{self.comsumerID}:拉取任务{taskId}")
        resp_data = self._make_request(taskId)
        print(resp_data)


if __name__ == "__main__":
    from configs import CrawlerConfig

    """万方专利爬虫主程序"""
    config = CrawlerConfig()
    p1 = WanfangPatentProducer(config, producerID=1)
    # p2=WanfangPatentProducer(config,producerID=2)
    c1 = WanfangPatentComsumer(config, comsumerID=1)
    # c2=WanfangPatentComsumer(config,comsumerID=2)
    p1.start()
    c1.start()

    p1.join()
    c1.join()
    print('All threads finished!')
