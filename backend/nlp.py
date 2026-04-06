import numpy as np
import torch
import torch.nn as nn
from transformers import BertModel, BertTokenizer, BertForTokenClassification
from transformers import pipeline
import jieba
import re


# 技术要素标签
LABELS = ['B-TECH', 'I-TECH', 'B-FUNC', 'I-FUNC', 'B-EFF', 'I-EFF', 'O']


class BERTBiLSTMCRF(nn.Module):
    def __init__(self, bert_model_name='bert-base-chinese', num_labels=7, hidden_size=768, lstm_hidden=256):
        super(BERTBiLSTMCRF, self).__init__()
        self.num_labels = num_labels
        self.bert = BertModel.from_pretrained(bert_model_name)
        self.tokenizer = BertTokenizer.from_pretrained(bert_model_name)
        self.bilstm = nn.LSTM(hidden_size, lstm_hidden // 2, bidirectional=True, batch_first=True)
        self.classifier = nn.Linear(lstm_hidden, num_labels)
        self.dropout = nn.Dropout(0.1)

    def forward(self, input_ids, attention_mask, labels=None):
        outputs = self.bert(input_ids=input_ids, attention_mask=attention_mask)
        sequence_output = outputs.last_hidden_state
        sequence_output = self.dropout(sequence_output)
        lstm_output, _ = self.bilstm(sequence_output)
        logits = self.classifier(lstm_output)

        if labels is not None:
            loss_fct = nn.CrossEntropyLoss()
            loss = loss_fct(logits.view(-1, self.num_labels), labels.view(-1))
            return loss, logits
        return logits


def extract_technical_elements(text, model_path='models/bert_bilstm_crf.pth'):
    """
    提取专利文本中的技术要素
    """
    # 加载预训练模型（如果存在），否则使用规则-based方法
    try:
        model = BERTBiLSTMCRF()
        model.load_state_dict(torch.load(model_path))
        model.eval()
        tokenizer = BertTokenizer.from_pretrained('bert-base-chinese')

        inputs = tokenizer(text, return_tensors='pt', truncation=True, max_length=512)
        with torch.no_grad():
            logits = model(**inputs)
            predictions = torch.argmax(logits, dim=2).squeeze().tolist()

        tokens = tokenizer.convert_ids_to_tokens(inputs['input_ids'].squeeze())
        elements = []
        current_entity = None
        for token, pred in zip(tokens, predictions):
            label = LABELS[pred]
            if label.startswith('B-'):
                if current_entity:
                    elements.append(current_entity)
                current_entity = {'type': label[2:], 'text': token.replace('##', '')}
            elif label.startswith('I-') and current_entity and current_entity['type'] == label[2:]:
                current_entity['text'] += token.replace('##', '')
            else:
                if current_entity:
                    elements.append(current_entity)
                    current_entity = None
        if current_entity:
            elements.append(current_entity)

        return elements

    except FileNotFoundError:
        # 回退到规则-based方法
        return rule_based_extraction(text)


def rule_based_extraction(text):
    """
    基于规则的技术要素提取
    """
    elements = []

    # 定义关键词模式
    tech_keywords = ['技术', '方法', '装置', '系统', '设备', '算法', '模型']
    func_keywords = ['功能', '作用', '用途', '应用']
    eff_keywords = ['效果', '效率', '性能', '精度', '准确性']

    # 分词
    words = jieba.cut(text)

    for word in words:
        word = word.strip()
        if not word:
            continue

        if any(kw in word for kw in tech_keywords):
            elements.append({'type': 'TECH', 'text': word})
        elif any(kw in word for kw in func_keywords):
            elements.append({'type': 'FUNC', 'text': word})
        elif any(kw in word for kw in eff_keywords):
            elements.append({'type': 'EFF', 'text': word})

    # 去重
    seen = set()
    unique_elements = []
    for elem in elements:
        key = (elem['type'], elem['text'])
        if key not in seen:
            unique_elements.append(elem)
            seen.add(key)

    return unique_elements


def analyze_technical_hotspots(patents_data):
    """
    分析技术热点
    """
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.cluster import KMeans

    # 提取技术要素文本
    tech_texts = []
    for patent in patents_data:
        elements = extract_technical_elements(patent.get('abstract', ''))
        tech_text = ' '.join([elem['text'] for elem in elements])
        tech_texts.append(tech_text)

    # TF-IDF向量化
    vectorizer = TfidfVectorizer(max_features=1000, stop_words='english')
    X = vectorizer.fit_transform(tech_texts)

    # K-means聚类
    kmeans = KMeans(n_clusters=5, random_state=42)
    clusters = kmeans.fit_predict(X)

    # 获取热点关键词
    hotspots = []
    feature_names = vectorizer.get_feature_names_out()
    for i in range(5):
        cluster_center = kmeans.cluster_centers_[i]
        top_indices = cluster_center.argsort()[-10:][::-1]
        top_words = [feature_names[idx] for idx in top_indices]
        hotspots.append({
            'cluster': i,
            'keywords': top_words,
            'count': sum(clusters == i)
        })

    return hotspots
