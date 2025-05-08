from flask import Flask, request, jsonify
from LDA_analyze import TopicKeywords
import re
import os

app = Flask(__name__)


def process_text(text):
    """预处理文本，分割为有效段落"""
    # 移除参考文献部分
    text = re.split(r'参考文献[:：]', text)[0]
    # 按段落分割
    paragraphs = [p.strip() for p in re.split(r'\n\n+', text) if len(p.strip()) > 50]
    return paragraphs


@app.route('/extract_keywords', methods=['POST'])
def extract_keywords():
    # 获取请求数据
    data = request.get_json()
    if not data or 'text' not in data:
        return jsonify({"error": "请提供文本内容"}), 400

    # 预处理文本
    paragraphs = process_text(data['text'])
    if not paragraphs:
        return jsonify({"error": "无有效文本内容"}), 400

    # 初始化LDA分析器
    extractor = TopicKeywords(
        train_data=paragraphs,
        n_components=5,  # 主题数
        n_top_words=10,  # 每个主题的关键词数
        max_iter=20  # 迭代次数
    )

    # 执行分析
    try:
        results = extractor.analysis()
        return jsonify(results)
    except Exception as e:
        return jsonify({"error": f"分析失败: {str(e)}"}), 500


if __name__ == '__main__':
    # 确保输出目录存在
    app.run(host='0.0.0.0', port=5000, debug=True)