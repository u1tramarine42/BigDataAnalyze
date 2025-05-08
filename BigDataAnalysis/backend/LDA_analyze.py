# -*- coding: utf-8 -*-
"""
独立运行的主题关键词提取程序
"""

import jieba
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.decomposition import LatentDirichletAllocation


import re
import jieba
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.decomposition import LatentDirichletAllocation


class TopicKeywords:
    def __init__(self, train_data, n_components=5, n_top_words=10, max_iter=10, stopwords_file='stopwords.txt'):
        """
        新增stopwords_file参数
        """
        # 加载停用词表
        with open(stopwords_file, 'r', encoding='utf-8') as f:
            self.stopwords = set(line.strip() for line in f)
            
        self.train_data = [self._preprocess_text(data) for data in train_data]
        self.n_components = n_components
        self.n_top_words = n_top_words
        self.max_iter = max_iter

    def _preprocess_text(self, text):
        """预处理文本，添加停用词过滤"""
        # 处理英文
        eng_words = re.findall(r'[a-zA-Z]+', text)
        # 处理中文
        chn_words = jieba.lcut(text)
        # 合并结果并过滤停用词
        words = []
        for word in chn_words:
            word = word.strip()
            if not word:
                continue
            if re.match(r'^[a-zA-Z]+$', word):
                word = word.lower()
                if word not in self.stopwords:  # 过滤英文停用词
                    words.append(word)
            elif word not in self.stopwords:  # 过滤中文停用词
                words.append(word)
        # 添加英文单词(已过滤)
        words.extend(w.lower() for w in eng_words 
                   if w.lower() not in self.stopwords and w.lower() not in words)
        return " ".join(words)

    def print_top_words(self, model, feature_names, n_top_words):
        ret = {}
        for topic_idx, topic in enumerate(model.components_):
            key = "topic_{}".format(topic_idx)
            val = [feature_names[i] for i in topic.argsort()[:-n_top_words - 1:-1]]
            ret[key] = val
        return ret

    def analysis(self):
        tf_vectorizer = CountVectorizer()
        tf = tf_vectorizer.fit_transform(self.train_data)

        lda = LatentDirichletAllocation(
            n_components=self.n_components,
            max_iter=self.max_iter,
            learning_method='online',
            learning_offset=50.,
            random_state=0
        )
        lda.fit(tf)
        tf_feature_names = tf_vectorizer.get_feature_names_out()
        return self.print_top_words(lda, tf_feature_names, self.n_top_words)


def load_data(file_path):
    """加载文本数据"""
    with open(file_path, 'r', encoding='utf-8') as f:
        return [line.strip() for line in f if line.strip()]


if __name__ == "__main__":
    # 配置参数
    DATA_PATH = "./test_data/test_data_cluster.txt"  # 替换为你的文本文件路径
    N_TOPICS = 5  # 主题数量
    N_KEYWORDS = 10  # 每个主题的关键词数量
    MAX_ITER = 20  # 迭代次数

    # 加载数据
    print(f"正在加载数据: {DATA_PATH}")
    train_data = load_data(DATA_PATH)

    # 提取主题关键词
    print("开始提取主题关键词...")
    extractor = TopicKeywords(
        train_data=train_data,
        n_components=N_TOPICS,
        n_top_words=N_KEYWORDS,
        max_iter=MAX_ITER
    )
    results = extractor.analysis()

    # 打印结果
    print("\n主题关键词提取结果:")
    for topic, keywords in results.items():
        print(f"{topic}: {', '.join(keywords)}")