from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional


@dataclass
class PatentItem:
    """专利数据条目，用于存储清洗和解析后的结构化数据。"""
    # 专利核心元数据
    patent_internal_id: str  # 万方内部专利唯一标识符，用于去重和追溯
    application_number: str  # 专利申请号，唯一标识，格式如CN202511610595.7
    publication_number: Optional[str]  # 专利公开/公告号，如CN121241842A
    title: str  # 专利标题，已移除HTML标签的纯文本
    inventors: List[str]  # 发明人列表，已处理为空列表或实际发明人姓名
    applicant: Optional[str]  # 申请人/专利权人名称
    abstract_text: str  # 专利摘要全文，已合并段落并清除HTML标签
    patent_type: Optional[str]  # 专利类型：发明专利/实用新型/外观设计
    application_date: Optional[datetime.date]  # 专利申请日，已转换为Python date对象
    publication_date: Optional[datetime.date]  # 专利公开/公告日，已转换为Python date对象
    country_code: Optional[str]  # 专利国别代码，如CN(中国)、US(美国)
    language: Optional[str]  # 专利文本语言代码，如chi(中文)、eng(英文)
    pdf_link: Optional[str]  # 专利PDF全文下载链接

    # 系统元数据
    source_db: str = 'WF'  # 数据来源标识，固定为"WF"表示万方数据库
    crawl_time: datetime = field(default_factory=datetime.now)  # 数据解析入库时间戳，自动记录当前时间