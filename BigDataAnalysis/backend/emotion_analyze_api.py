from flask import Flask, request, jsonify
from emotion_analyze import predict_
import re
import os

app = Flask(__name__)


def analyze_article(text):
    # 获取参考文献之前的内容
    main_content = re.split(r'参考文献\s*[:：]?\s*([\s\S]+?)(?=\s*\d{6}-\d{2}|$)', text)[0]

    # 按每100字分割文本
    segments = []
    for i in range(0, len(main_content), 100):
        segment = main_content[i:i + 100].strip()
        if segment:  # 跳过空片段
            segments.append(segment)

    # 初始化情感计数器
    emotion_counts = {
        "Confused": 0,
        "Critical": 0,
        "Supportive": 0,
        "Neutral": 0,
        "Anticipatory": 0,
        "Surprised": 0
    }

    # 确保模型已加载
    if not os.path.exists("./model/model.m"):
        from emotion_analyze import classification_
        classification_()

    # 分析每个文本段
    for segment in segments:
        print(segment)
        emotion = predict_(segment)
        if emotion in emotion_counts:
            emotion_counts[emotion] += 1

    return emotion_counts


@app.route('/analyze', methods=['POST'])
def analyze():
    data = request.get_json()
    if not data or 'text' not in data:
        return jsonify({"error": "No text provided"}), 400

    text = data['text']
    result = analyze_article(text)
    return jsonify(result)


if __name__ == '__main__':
    app.run(debug=True, port=5000)