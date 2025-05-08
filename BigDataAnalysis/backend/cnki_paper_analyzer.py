import re
from json import JSONEncoder  # 改用标准库导入

from flask import Flask, request, jsonify
from flask_cors import CORS  # 导入CORS
import jieba
from sklearn.feature_extraction.text import TfidfVectorizer
from collections import defaultdict, Counter
import numpy as np
from gensim import corpora, models

app = Flask(__name__)
CORS(app)  # 启用CORS
app.json.ensure_ascii = False
'''
@app.route('/')
def hello_world():  # put application's code here
    return 'Hello World!'
'''
stopwords = set(open('stopwords.txt', encoding='utf-8').read().splitlines())  # 停用词表
vectorizer = TfidfVectorizer(
    tokenizer=lambda text: [w for w in jieba.lcut(text) if w not in stopwords],
    ngram_range=(1, 2),  # 捕获单字和双字词
    min_df=0.01  # 忽略低频词（假设有语料库）
)
class NumpyEncoder(JSONEncoder):
    def default(self, obj):
        if isinstance(obj, (np.float32, np.float64)):
            return float(obj)
        elif isinstance(obj, np.integer):
            return int(obj)
        return super().default(obj)

app.json_encoder = NumpyEncoder  # 应用到Flask应用
def lda_keywords(text, num_topics=3):
    words = [jieba.lcut(text)]
    dictionary = corpora.Dictionary(words)
    corpus = [dictionary.doc2bow(doc) for doc in words]
    lda = models.LdaModel(corpus, num_topics=num_topics, id2word=dictionary)
    return lda.show_topic(0)  # 返回第一个主题的关键词



def textrank_keywords(text, top_n=20):
    # 预处理文本，处理连字符情况
    processed_text = re.sub(r'(\w)-(\w)', r'\1\2', text)  # 将d-wave转为dwave

    words = [word for word in jieba.lcut(processed_text)
             if len(word) > 2 and  # 过滤单字符和双字母词
             word not in stopwords and
             not re.match(r'^[a-zA-Z]{2}$', word)]  # 过滤双字母英文单词

    # ... 后面的共现图和PageRank计算代码保持不变 ...
    graph = defaultdict(lambda: defaultdict(int))
    window_size = 3
    for i in range(len(words)):
        for j in range(i + 1, min(i + window_size, len(words))):
            graph[words[i]][words[j]] += 1
            graph[words[j]][words[i]] += 1

    # PageRank迭代
    scores = defaultdict(float)
    damping = 0.85
    for _ in range(10):
        new_scores = defaultdict(float)
        for word in graph:
            new_scores[word] = (1 - damping) + damping * sum(
                graph[other][word] / sum(graph[other].values()) * scores[other]
                for other in graph if word in graph[other]
            )
        scores = new_scores

    # 返回关键词及其TextRank分数
    sorted_keywords = sorted(scores.items(), key=lambda x: x[1], reverse=True)[:top_n]
    return [{"keyword": k, "score": float(v)} for k, v in sorted_keywords]


def tfidf_keywords(text, corpus=None):
    """改进版关键词提取
    Args:
        text: 待分析文本
        corpus: 可选背景语料库（增强IDF效果）
    """
    # 文本预处理 - 去标点、过滤停用词和空格
    text_clean = re.sub(r'[^\w\s]', '', text)  # 去标点
    words = [w.strip().lower() for w in jieba.lcut(text_clean)  # 统一转为小写
             if len(w.strip()) > 1 and  # 过滤单字符
             w not in stopwords and  # 过滤停用词
             w.strip() and  # 过滤空格
             not re.match(r'^\W+$', w)]  # 过滤纯标点符号
    text_clean = ' '.join(words)

    # 动态训练或复用模型
    if corpus:
        vectorizer.fit(corpus + [text_clean])
    else:
        vectorizer.fit([text_clean])

    # 提取关键词
    tfidf_matrix = vectorizer.transform([text_clean])
    feature_names = vectorizer.get_feature_names_out()
    scores = tfidf_matrix.toarray()[0]

    # 按得分排序并去除重复项和空格
    unique_keywords = {}
    for i in sorted(range(len(scores)), key=lambda x: scores[x], reverse=True):
        word = feature_names[i].strip()
        if word and word not in unique_keywords:
            unique_keywords[word] = scores[i]
            if len(unique_keywords) >= 20:  # 修改为20
                break
    return [{"keyword": k, "score": float(v)} for k, v in unique_keywords.items() if float(v) >= 0.0075]


def frequency_keywords(text_o, top_n=20):
    text = re.sub(r'(\w)-(\w)', r'\1\2', text_o)  # 将d-wave转为dwave
    """基于词频的关键词提取"""
    words = [w.strip().lower() for w in jieba.lcut(text)  # 统一转为小写
             if len(w.strip()) > 2 and  # 过滤单字符和双字母词
             w not in stopwords and
             w.strip() and
             not re.match(r'^\W+$', w) and  # 过滤纯标点符号
             not w.strip().isdigit()]  # 新增：过滤纯数字词

    word_counts = defaultdict(int)
    for word in words:
        word_counts[word] += 1

    sorted_words = sorted(word_counts.items(), key=lambda x: x[1], reverse=True)[:top_n]
    return [{"keyword": k, "score": float(v)} for k, v in sorted_words]


def pos_keywords(text, top_n=5):
    """基于词性的关键词提取(提取名词和动词)"""
    import jieba.posseg as pseg

    words = pseg.cut(text)
    keywords = []
    for word, flag in words:
        if (word not in stopwords and
                word.strip() and
                not re.match(r'^\W+$', word) and
                flag.startswith(('n', 'v'))):  # 名词和动词
            keywords.append(word)

    # 按词频排序
    word_counts = defaultdict(int)
    for word in keywords:
        word_counts[word] += 1

    sorted_words = sorted(word_counts.items(), key=lambda x: x[1], reverse=True)[:top_n]
    return [{"keyword": k, "score": float(v)} for k, v in sorted_words]


def mutual_info_keywords(text, top_n=5):
    """基于互信息的关键词提取(适合提取专业术语)"""
    from sklearn.feature_extraction.text import CountVectorizer

    # 获取所有可能的2-gram
    vectorizer = CountVectorizer(ngram_range=(2, 2), tokenizer=lambda x: jieba.lcut(x))
    X = vectorizer.fit_transform([text])
    ngrams = vectorizer.get_feature_names_out()

    # 计算互信息
    word_scores = {}
    total_count = X.sum()
    for i, ngram in enumerate(ngrams):
        word1, word2 = ngram.split()
        if (word1 in stopwords or word2 in stopwords or
                not word1.strip() or not word2.strip()):
            continue

        # 计算互信息
        p_xy = X[0, i] / total_count
        p_x = sum(X[0, j] for j, ng in enumerate(ngrams) if ng.startswith(word1)) / total_count
        p_y = sum(X[0, j] for j, ng in enumerate(ngrams) if ng.endswith(word2)) / total_count
        mi = p_xy * np.log2(p_xy / (p_x * p_y + 1e-10))

        word_scores[ngram] = mi

    sorted_words = sorted(word_scores.items(), key=lambda x: x[1], reverse=True)[:top_n]
    return [{"keyword": k, "score": float(v)} for k, v in sorted_words]
@app.route('/analyze_paper', methods=['POST'])
def analyze_paper():
    # 获取前端传来的论文数据
    data = request.get_json()
    if not data:
        return jsonify({"error": "No data provided"}), 400

    # 提取论文摘要，支持'abstract'或'text'字段
    abstract = data.get('abstract', '') or data.get('text', '')
    if not abstract:
        return jsonify({"error": "No abstract or text provided"}), 400

    # 使用 jieba 进行分词
    words_jieba = [w for w in jieba.lcut(abstract)
                   if w not in stopwords and  # 过滤停用词
                   w.strip() and  # 过滤空格
                   not re.match(r'^\W+$', w)]  # 过滤纯标点符号
    from collections import Counter
    top10_words = Counter(words_jieba).most_common(10)
    top10_keywords = [{"word": word, "count": count} for word, count in top10_words]
    # 使用 TF-IDF 提取关键词
    vectorizer = TfidfVectorizer()
    tfidf_matrix = vectorizer.fit_transform([abstract])
    feature_names = vectorizer.get_feature_names_out()
    dense = tfidf_matrix.todense()
    doc = dense[0].tolist()[0]
    phrase_scores = [pair for pair in zip(range(0, len(doc)), doc) if pair[1] > 0]
    sorted_phrase_scores = sorted(phrase_scores, key=lambda t: t[1] * -1)
    top_keywords = [feature_names[idx] for (idx, score) in sorted_phrase_scores[:5]]

    textrank_kws = textrank_keywords(abstract)#基于图排序的textrank算法
    tfidf_kws= tfidf_keywords(abstract)#TF-IDF
    #lda_kws = lda_keywords(abstract)#LDA
    freq_kws = frequency_keywords(abstract)  # 基于词频
    pos_kws = pos_keywords(abstract)  # 基于词性
    #mi_kws = mutual_info_keywords(abstract)  # 基于互信息

    result = {
        "jieba_words": words_jieba,
        "tfidf_keywords": tfidf_kws,
        "textrank_keywords": textrank_kws,
        "frequency_keywords": freq_kws,
        "pos_keywords": pos_kws,
        "top10_keywords": top10_keywords,
        # "mutual_info_keywords": mi_kws,
        # "LDA":lda_kws
    }

    return jsonify(result)

def analyze_paper_with_text(abstract):
    """直接处理传入的文本，而不是从请求中获取"""
    if not abstract:
        return jsonify({"error": "缺少摘要内容"}), 400

    # 使用 jieba 进行分词
    words_jieba = [w for w in jieba.lcut(abstract)
                   if w not in stopwords and  # 过滤停用词
                   w.strip() and  # 过滤空格
                   not re.match(r'^\W+$', w)]  # 过滤纯标点符号


    # 使用 TF-IDF 提取关键词
    vectorizer = TfidfVectorizer()
    tfidf_matrix = vectorizer.fit_transform([abstract])
    feature_names = vectorizer.get_feature_names_out()
    dense = tfidf_matrix.todense()
    doc = dense[0].tolist()[0]
    phrase_scores = [pair for pair in zip(range(0, len(doc)), doc) if pair[1] > 0]
    sorted_phrase_scores = sorted(phrase_scores, key=lambda t: t[1] * -1)
    top_keywords = [feature_names[idx] for (idx, score) in sorted_phrase_scores[:5]]

    textrank_kws = textrank_keywords(abstract)  # 基于图排序的textrank算法
    tfidf_kws = tfidf_keywords(abstract)  # TF-IDF
    freq_kws = frequency_keywords(abstract)  # 基于词频
    pos_kws = pos_keywords(abstract)  # 基于词性
    top10_keywords = [{"word": item["keyword"], "count": int(item["score"])} for item in freq_kws[:10]]
    result = {
        "jieba_words": words_jieba,
        "tfidf_keywords": tfidf_kws,
        "textrank_keywords": textrank_kws,
        "frequency_keywords": freq_kws,
        "pos_keywords": pos_kws,
        "top10_keywords": top10_keywords,
    }

    return jsonify(result)

# ... 前面代码保持不变 ...

def extract_paper_info(text):
    lines = [line.strip() for line in text.strip().split('\n') if line.strip()]

    # 提取标题（第一个非空行的第一个空格前的内容）
    title = None
    if lines:
        first_line = lines[0]
        space_pos = first_line.find(' ')
        if space_pos > 0:
            title = first_line[:space_pos]
        else:
            title = first_line  # 如果没有空格，整行作为标题

    # 提取作者（第一个空格后到第一个句号前的内容）
    authors = []
    if lines:
        first_line = lines[0]
        space_pos = first_line.find(' ')
        if space_pos > 0:
            rest_content = first_line[space_pos + 1:]
            period_pos = rest_content.find('.')
            author_text = rest_content[:period_pos].strip() if period_pos > 0 else rest_content.strip()

            # 改进后的分割逻辑：先按逗号/顿号分割，再处理每个部分
            author_parts = re.split(r'[,，、]', author_text)
            for part in author_parts:
                # 去除数字和*号，然后按空格分割
                clean_part = re.sub(r'[\d\*]', '', part).strip()
                if clean_part:
                    # 按空格分割并过滤空字符串
                    names = [name for name in clean_part.split() if name]
                    authors.extend(names)


    # 提取发表单位（第一个句号后到第一个*前的内容）
    institution_match = re.search(r'\.(.+?)(?=\*)', text)
    institutions = institution_match.group(1).strip() if institution_match else None

    if institutions:
        institutions = re.sub(r'\s+', ' ', institutions)  # 将多个连续空格替换为单个空格
        institutions = institutions.replace(' ,', ',').replace(', ', ',')  # 处理逗号周围的空格

    # 提取分类号
    category_match = re.search(r'中图分类号\s*[:：]?\s*([A-Z0-9.-]+)', text)
    category_code = category_match.group(1).strip() if category_match else None

    # 提取文献标识码
    document_code_match = re.search(r'文献标[识志]码\s*[:：]?\s*([A-Z])', text)
    document_code = document_code_match.group(1).strip() if document_code_match else None

    # 提取日期信息
    submission_date = re.search(r'收稿日期\s*[:：]\s*(\d{4}-\d{2}-\d{2})', text)
    submission_date = submission_date.group(1) if submission_date else None

    acceptance_date = re.search(r'接受日期\s*[:：]\s*(\d{4}-\d{2}-\d{2})', text)
    acceptance_date = acceptance_date.group(1) if acceptance_date else None

    online_date = re.search(r'网络出版日期\s*[:：]\s*(\d{4}-\d{2}-\d{2})', text)
    online_date = online_date.group(1) if online_date else None

    # 提取摘要（从"摘要"到"关键词"前）
    abstract_match = re.search(r'摘要\s*[:：]?\s*([\s\S]+?)\s*关键词', text)
    abstract = abstract_match.group(1).strip() if abstract_match else None

    # 如果匹配失败，尝试更宽松的匹配模式
    if not abstract:
        abstract_match = re.search(r'摘要\s*[:：]?\s*([\s\S]+)', text)
        abstract = abstract_match.group(1).strip() if abstract_match else None

    # 提取关键词（从"关键词"到下一个标题前）
    keywords_match = re.search(r'关键词\s*[:：]?\s*([^PACS]+?)(?=\s*PACS)', text)
    keywords = []

    if keywords_match:
        # 提取关键词部分
        keywords_text = keywords_match.group(1).strip()
        # 改进的分割逻辑：直接按中文逗号分割，保留完整关键词
        keywords = [kw.strip() for kw in re.split(r'[，,]', keywords_text) if kw.strip()]

    # 提取参考文献（从"参考文献"到文本结束或遇到六位数字-数字格式）
    references_match = re.search(r'参考文献\s*[:：]?\s*([\s\S]+?)(?=\s*\d{6}-\d{2}|$)', text)
    references = []
    if references_match:
        references_text = references_match.group(1)
        references = [ref.strip() for ref in re.split(r'\n\s*\d+\.\s+', references_text) if ref.strip()]

    return {
        "题目": title,
        "作者": authors,
        "发表单位": institutions,
        "中图分类号": category_code,
        "文献标志码": document_code,
        "收稿日期": submission_date,
        "接受日期": acceptance_date,
        "网络发表日期": online_date,
        "摘要": abstract,
        "关键词": keywords,
        "参考文献": references
    }


@app.route('/extract_paper', methods=['POST'])
def extract_paper():
    data = request.get_json()
    if not data or 'text' not in data:
        return jsonify({"error": "No text provided"}), 400

    paper_text = data['text']
    result = extract_paper_info(paper_text)
    return jsonify(result)


# ... 后面代码保持不变 ...

if __name__ == '__main__':
    app.run(debug=True)