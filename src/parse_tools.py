from loguru import logger
from typing import Dict, List, Any


def extract_task_ids(pages_patent_data: Dict[str, Any]) -> List[str]:
    """
    从{页数:API响应JSON,...}中提取所有taskId。

    Args:
        pages_patent_data (dict): {页数:API响应JSON,...}

    Returns:
        list: 包含所有taskId的列表
    """
    task_ids = []

    try:
        for page_key, page_data in pages_patent_data.items():
            try:
                # 获取专利列表
                patent_list = page_data.get('4', [])

                if not isinstance(patent_list, list):
                    logger.error(f"页面 {page_key} 的专利数据格式异常")
                    continue

                # 遍历专利条目提取taskId
                for idx, patent_item in enumerate(patent_list):
                    try:
                        if isinstance(patent_item, dict) and '3' in patent_item:
                            task_id = patent_item['3']
                            if isinstance(task_id, str) and task_id.strip():
                                task_ids.append(task_id.strip())
                    except Exception as e:
                        logger.error(f"处理页面 {page_key} 第 {idx} 个专利条目时出错: {e}")
                        continue

            except Exception as e:
                logger.error(f"处理页面 {page_key} 时出错: {e}")
                continue

    except Exception as e:
        logger.error(f"解析API响应结构时出错: {e}")

    return task_ids

