import json
from dataclasses import dataclass, field
from typing import Dict, Any, Optional, List
from datetime import datetime, date
from urllib.parse import urljoin
import hashlib


@dataclass
class PatentItem:
    """专利数据条目，用于存储清洗和解析后的结构化数据。"""
    # 专利核心元数据
    patent_internal_id: str  # 万方内部专利唯一标识符
    application_number: str  # 专利申请号
    publication_number: Optional[str]  # 专利公开/公告号
    title: str  # 专利标题
    inventors: List[str]  # 发明人列表
    applicant: Optional[str]  # 申请人/专利权人名称
    applicant_address: Optional[str]  # 申请人地址
    agency: Optional[str]  # 代理机构
    agent: Optional[str]  # 代理人
    abstract_text: str  # 专利摘要全文
    claims_text: str  # 权利要求全文
    description_text: Optional[str]  # 说明书全文
    patent_type: Optional[str]  # 专利类型
    ipc_classes: List[str]  # IPC分类号列表
    main_ipc: Optional[str]  # 主IPC分类号
    application_date: Optional[date]  # 专利申请日
    publication_date: Optional[date]  # 专利公开/公告日
    country_code: Optional[str]  # 专利国别代码
    language: Optional[str]  # 专利文本语言
    legal_status: Optional[str]  # 法律状态
    patent_link: Optional[str]  # 专利详情链接

    # 技术分类信息
    main_class_codes: Optional[str]  # 主分类号路径

    # 系统元数据
    source_db: str = 'WF'  # 数据来源标识
    crawl_time: datetime = field(default_factory=datetime.now)  # 解析入库时间戳
    raw_data_hash: Optional[str] = None  # 原始数据哈希，用于去重校验