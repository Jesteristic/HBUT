from typing import List, Optional
from datetime import datetime
import re
from dateutil.parser import parse as date_parse
from loguru import logger
from src.spiders.wanfangtools import WanfangPatentSearcher
from configs import SearchConfig
from Item_models import PatentItem
from parse_tools import extract_task_ids

class WangFangTaskIdProducer:
    def __init__(self, search_config: SearchConfig = SearchConfig(
        timeout=30,
        max_retries=3,
        max_workers=5,
        delay_between_requests=0.2
    )):
        self.searchConfig = search_config
        self.searcher = WanfangPatentSearcher(self.searchConfig)

    def produce(self, keyword: str,
                            start_page: int = 1,
                            end_page: int = 10,
                            page_size: int = 20) -> List[PatentItem]:
        '''
        抓取多页专利数据
        :return: 成功解析的PatentItem对象列表。
        '''
        result = []
        pages_patent_data = self.searcher.search_multiple_pages(keyword, start_page, end_page, page_size)
        result = extract_task_ids(pages_patent_data)
        # 提交redis任务队列
        return result
