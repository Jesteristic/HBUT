import blackboxprotobuf
from loguru import logger
import json
from typing import Dict, Any, Optional
import time
from configs import SearchConfig
from spiders.spider_base import WangFangBase
from parse_tools import extract_task_ids
from sql.sql_tools import RedisUtils


class WanfangPatentSearcher(WangFangBase):
    """万方专利搜索器（单线程版本）"""

    def __init__(self, config: Optional[SearchConfig] = None, cookies: Optional[Dict] = None):
        """
        初始化搜索器

        Args:
            config: 搜索配置
            cookies: Cookie字典
        """
        super().__init__(config, cookies)
        # 模板十六进制字符串
        self.TEMPLATE_HEX_STRING = (
            "0A 25 0A 06 70 61 74 65 6E 74 12 06 E6 A4 8D E7 89 A9 28 01 30 14 "
            "42 01 00 48 01 62 02 70 63 6A 06 73 65 61 72 63 68 10 01 22 07 41 "
            "49 5F 52 45 41 44 22 0A 41 49 5F 45 58 54 52 41 43 54"
        )

        # 基本配置
        self.SEARCH_URL = f"{self.BASE_URL}/SearchService.SearchService/search"

        # Redis producer
        try:
            self.redis = RedisUtils()
        except Exception as e:
            logger.warning(f"Redis 初始化失败: {e}")
            self.redis = None
        self.REDIS_TASK_LIST_KEY = "wanfang:task_queue"

        logger.info("万方专利搜索器初始化完成")

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
            logger.error(f"构造 protobuf 数据失败: {e}")
            raise

    def _make_request(
            self,
            keyword: str,
            page: int,
            page_size: int
    ) -> Optional[Dict[str, Any]]:
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
                logger.debug(f"开始搜索: 关键词={keyword}, 页码={page}")

                # 构造请求数据
                post_data = self.construct_protobuf(keyword, page, page_size)

                # 发送请求
                start_time = time.time()
                response = self.session.post(
                    self.SEARCH_URL,
                    headers=self.headers,
                    data=post_data,
                    timeout=self.config.timeout
                )
                elapsed_time = time.time() - start_time

                # 检查响应状态
                response.raise_for_status()
                logger.debug(f"请求成功: 状态码={response.status_code}, 耗时={elapsed_time:.2f}s")

                # 反序列化响应结果
                if len(response.content) > 5:
                    response_data, _ = blackboxprotobuf.protobuf_to_json(response.content[5:])
                    logger.debug(f"解析成功: 页码={page}, 数据长度={len(response.content)}")

                    # 解析并实时推送 taskId 到 Redis
                    try:
                        task_ids = extract_task_ids({page: response_data})
                        if task_ids:
                            if self.redis:
                                try:
                                    # 批量推送到列表
                                    self.redis.rpush(self.REDIS_TASK_LIST_KEY, *task_ids)
                                    logger.info(f"已将 {len(task_ids)} 个 taskId 推入 Redis 列表 {self.REDIS_TASK_LIST_KEY}")
                                except Exception as e:
                                    logger.warning(f"推送 taskId 到 Redis 失败: {e}")
                            else:
                                logger.warning("Redis 未初始化，无法推送 taskId")
                    except Exception as e:
                        logger.error(f"解析 taskId 并推送到 Redis 时出错: {e}")

                    # 返回解析后的数据
                    if isinstance(response_data, str):
                        return json.loads(response_data)
                    return response_data
                else:
                    logger.warning(f"响应数据过短: 页码={page}, 长度={len(response.content)}")

            except Exception as e:
                logger.warning(f"请求失败 (尝试 {attempt + 1}/{self.config.max_retries}): {e}")

                if attempt < self.config.max_retries - 1:
                    # 等待后重试
                    time.sleep(1 * (attempt + 1))
                else:
                    logger.error(f"页码 {page} 请求失败，已达到最大重试次数")
                    return None

            # 请求间延迟
            time.sleep(self.config.delay_between_requests)

        return None

    def search_multiple_pages(
            self,
            keyword: str,
            start_page: int = 1,
            end_page: int = 5,
            page_size: int = 50
    ) -> Dict[int, Optional[Dict[str, Any]]]:
        """
        单线程搜索多页数据

        Args:
            keyword: 搜索关键词
            start_page: 起始页码
            end_page: 结束页码
            page_size: 每页数量

        Returns:
            页码到搜索结果的映射字典
        """
        if start_page < 1:
            start_page = 1
        if end_page < start_page:
            end_page = start_page

        total_pages = end_page - start_page + 1
        logger.info(f"开始搜索: 关键词={keyword}, 页码范围={start_page}-{end_page}, 总页数={total_pages}")

        results = {}
        failed_pages = []

        # 请求
        for page in range(start_page, end_page + 1):
            try:
                result = self._make_request(keyword, page, page_size)
                if result:
                    results[page] = result
                    logger.info(f"页码 {page} 搜索完成")
                else:
                    failed_pages.append(page)
                    logger.warning(f"页码 {page} 搜索失败")

            except Exception as e:
                failed_pages.append(page)
                logger.error(f"页码 {page} 处理异常: {e}")
                continue

        # 统计结果
        success_count = len(results)
        logger.info(f"搜索完成: 成功 {success_count}/{total_pages} 页")
        if failed_pages:
            logger.warning(f"失败的页码: {failed_pages}")

        return results