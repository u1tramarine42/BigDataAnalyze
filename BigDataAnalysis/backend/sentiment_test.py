from flask import Flask, request, jsonify
from transformers import pipeline
from langdetect import detect
import numpy as np
import re

app = Flask(__name__)

# 初始化各语言模型（首次运行会自动下载）
MODELS = {
    'en': pipeline("text-classification",
                   model="finiteautomata/bertweet-base-sentiment-analysis"),
    'zh': pipeline("text-classification",
                   model="bert-base-chinese"),
    'default': pipeline("text-classification",
                        model="distilbert-base-multilingual-cased")
}


# 语言检测函数
def detect_language(text):
    try:
        # 取前1000字符检测（提高性能）
        lang = detect(text[:1000])
        return 'zh' if lang == 'zh-cn' else lang
    except:
        return 'en'  # 默认英语


# 论文文本预处理
def preprocess_paper(text):
    # 去除特殊字符但保留标点
    text = re.sub(r'[^\w\s.,;:!?()\u4e00-\u9fff]', ' ', text)
    # 分句（简单实现）
    sentences = re.split(r'(?<=[.!?])\s+', text)
    return [s.strip() for s in sentences if len(s.strip()) > 10]


@app.route('/analyze', methods=['POST'])
def analyze_paper():
    data = request.get_json()
    paper_text = data.get('paper_text', '')

    if not paper_text:
        return jsonify({"error": "No paper text provided"}), 400

    # 预处理
    sentences = preprocess_paper(paper_text)
    if not sentences:
        return jsonify({"error": "No valid sentences found"}), 400

    # 检测语言（取第一句的语言）
    lang = detect_language(sentences[0])
    model = MODELS.get(lang, MODELS['default'])

    # 分析每个句子
    results = {
        "language": lang,
        "sentences": [],
        "sentiment_distribution": {"positive": 0, "negative": 0, "neutral": 0}
    }

    for sentence in sentences:
        try:
            # 情感分析
            result = model(sentence)[0]
            label = result['label'].lower()

            # 统一标签格式
            if 'pos' in label:
                label = 'positive'
            elif 'neg' in label:
                label = 'negative'
            else:
                label = 'neutral'

            # 记录结果
            results["sentences"].append({
                "text": sentence,
                "sentiment": label,
                "confidence": round(float(result['score']), 4)
            })
            results["sentiment_distribution"][label] += 1

        except Exception as e:
            print(f"Error analyzing sentence: {e}")
            continue

    # 计算整体情感
    total = len(results["sentences"])
    if total > 0:
        pos_ratio = results["sentiment_distribution"]["positive"] / total
        neg_ratio = results["sentiment_distribution"]["negative"] / total

        if pos_ratio > 0.5:
            results["overall_sentiment"] = "positive"
        elif neg_ratio > 0.5:
            results["overall_sentiment"] = "negative"
        else:
            results["overall_sentiment"] = "neutral"

    return jsonify(results)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)