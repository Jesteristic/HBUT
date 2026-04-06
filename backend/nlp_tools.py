"""
NLP工具模块 - 专利文本分析
"""
import base64
import logging
import os
import re
from io import BytesIO
from typing import List, Dict, Any

import jieba
import matplotlib.pyplot as plt
import networkx as nx
from sklearn.cluster import KMeans
from sklearn.feature_extraction.text import TfidfVectorizer

# 设置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class PatentNLPAnalyzer:
    def __init__(self):
        # 使用jieba进行中文分词
        try:
            dict_path = os.path.join(os.path.dirname(__file__), 'nlp_tools', 'dict.txt')
            jieba.load_userdict(dict_path)
        except FileNotFoundError:
            logger.warning("自定义词典文件dict.txt未找到，使用默认分词")

    def extract_technical_elements(self, text: str) -> Dict[str, List[str]]:
        """
        提取技术要素
        使用规则方法
        """
        elements = {
            'technologies': [],
            'problems': [],
            'solutions': [],
            'advantages': []
        }

        # 技术关键词
        tech_keywords = ['算法', '方法', '系统', '装置', '设备', '模型', '网络', '学习', '智能', '自动', '优化']
        for keyword in tech_keywords:
            if keyword in text:
                elements['technologies'].append(keyword)

        # 问题识别
        problem_patterns = [r'问题在于', r'存在.*问题', r'难以.*', r'无法.*']
        for pattern in problem_patterns:
            matches = re.findall(pattern, text)
            elements['problems'].extend(matches)

        # 解决方案
        solution_patterns = [r'通过.*实现', r'采用.*方式', r'利用.*技术']
        for pattern in solution_patterns:
            matches = re.findall(pattern, text)
            elements['solutions'].extend(matches)

        # 优势
        advantage_patterns = [r'提高.*', r'增强.*', r'改善.*', r'提升.*']
        for pattern in advantage_patterns:
            matches = re.findall(pattern, text)
            elements['advantages'].extend(matches)

        # 去重
        for key in elements:
            elements[key] = list(set(elements[key]))

        return elements

    def analyze_hotspots(self, patents: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        技术热点分析
        """
        if not patents:
            return {}

        texts = []
        for patent in patents:
            text = patent.get('title', '') + ' ' + (patent.get('abstract') or '')
            # 使用jieba分词
            segmented = ' '.join(jieba.cut(text))
            texts.append(segmented)

        try:
            # TF-IDF向量化
            vectorizer = TfidfVectorizer(max_features=50, stop_words=None)
            tfidf_matrix = vectorizer.fit_transform(texts)

            # K-means聚类
            n_clusters = min(3, len(texts))
            kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
            clusters = kmeans.fit_predict(tfidf_matrix.toarray())

            # 提取关键词
            feature_names = vectorizer.get_feature_names_out()
            hotspots = {}
            for i in range(n_clusters):
                cluster_indices = [j for j, c in enumerate(clusters) if c == i]
                if cluster_indices:
                    cluster_tfidf = tfidf_matrix[cluster_indices].mean(axis=0).A1
                    top_keywords = [feature_names[j] for j in cluster_tfidf.argsort()[-5:]]
                    hotspots[f'cluster_{i}'] = {
                        'keywords': top_keywords,
                        'patent_count': len(cluster_indices)
                    }

            return hotspots
        except Exception as e:
            logger.error(f"热点分析失败: {e}")
            return {}

    def create_patent_map(self, patents: List[Dict[str, Any]]) -> str:
        """
        生成专利地图 (简化版)
        返回base64编码的图像
        """
        if not patents:
            return ""

        try:
            # 构建技术关联图
            G = nx.Graph()

            for patent in patents:
                title = patent.get('title', '')[:20]  # 简化标题
                G.add_node(title, type='patent')

                # 提取关键词作为节点
                elements = self.extract_technical_elements(patent.get('abstract', ''))
                for tech in elements['technologies'][:3]:  # 取前3个技术
                    G.add_node(tech, type='technology')
                    G.add_edge(title, tech)

            # 绘制图
            plt.figure(figsize=(10, 6))
            pos = nx.spring_layout(G, seed=42)

            # 节点颜色
            node_colors = ['lightblue' if G.nodes[n]['type'] == 'patent' else 'lightgreen' for n in G.nodes]

            nx.draw(G, pos, with_labels=True, node_color=node_colors,
                    node_size=300, font_size=8)

            # 保存为base64
            buffer = BytesIO()
            plt.savefig(buffer, format='png', dpi=100, bbox_inches='tight')
            buffer.seek(0)
            image_base64 = base64.b64encode(buffer.read()).decode('utf-8')
            plt.close()

            return image_base64
        except Exception as e:
            logger.error(f"生成专利地图失败: {e}")
            return ""

    def analyze_opportunities(self, patents: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        技术机会识别与评价
        """
        if not patents:
            return []

        opportunities = []

        try:
            # 简单机会识别：低频技术可能有发展潜力
            tech_freq = {}
            for patent in patents:
                elements = self.extract_technical_elements(patent.get('abstract', ''))
                for tech in elements['technologies']:
                    tech_freq[tech] = tech_freq.get(tech, 0) + 1

            # 识别机会
            for tech, freq in tech_freq.items():
                if freq <= 2:  # 低频技术
                    opportunities.append({
                        'technology': tech,
                        'opportunity_score': 10 - freq,  # 简单评分
                        'reason': '低频技术领域，可能存在发展机会'
                    })

            return opportunities
        except Exception as e:
            logger.error(f"机会分析失败: {e}")
            return []


# 全局实例
analyzer = PatentNLPAnalyzer()


def extract_technical_elements(text: str) -> Dict[str, List[str]]:
    return analyzer.extract_technical_elements(text)


def analyze_technology_hotspots(patents: List[Dict[str, Any]]) -> Dict[str, Any]:
    return analyzer.analyze_hotspots(patents)


def create_patent_map_image(patents: List[Dict[str, Any]]) -> str:
    return analyzer.create_patent_map(patents)


def analyze_technology_opportunities(patents: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    return analyzer.analyze_opportunities(patents)
