from flask import Flask, request, jsonify
from flask_cors import CORS

from backend.researcher_analyze import get_yearly_author_keyword_relations, get_author_relations
from emotion_analyze_api import analyze_article
from LDA_analyze_api import process_text, TopicKeywords
from cnki_paper_analyzer import analyze_paper, extract_paper_info

app = Flask(__name__)
CORS(app)  # 启用跨域支持
app.json.ensure_ascii = False  # 确保JSON响应支持中文

# 情感分析接口
@app.route('/analyze', methods=['POST'])
def analyze():
    data = request.get_json()
    if not data or 'text' not in data:
        return jsonify({"error": "No text provided"}), 400

    text = data['text']
    result = analyze_article(text)
    return jsonify(result)

# 主题分析接口
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

# 添加论文分析API
@app.route('/analyze_paper', methods=['POST'])
def paper_analysis():
    data = request.get_json()
    if not data:
        return jsonify({"error": "请提供文本内容"}), 400
    
    # 将text参数传递给abstract参数
    if 'text' in data:
        # 在此处不修改request.json，而是直接创建一个带有abstract字段的新请求
        abstract = data['text']
        # 修改全局变量，临时存储abstract
        app.config['TEMP_ABSTRACT'] = abstract
        
    # 确保cnki_paper_analyzer使用正确的abstract值
    from cnki_paper_analyzer import analyze_paper_with_text
    return analyze_paper_with_text(app.config.get('TEMP_ABSTRACT', ''))

# 添加论文信息提取API
@app.route('/extract_paper', methods=['POST'])
def paper_extraction():
    data = request.get_json()
    if not data or 'text' not in data:
        return jsonify({"error": "请提供文本内容"}), 400
    
    # 从请求中直接获取文本内容
    text = data['text']
    
    # 调用函数进行处理
    from cnki_paper_analyzer import extract_paper_info
    result = extract_paper_info(text)
    return jsonify(result)

@app.route('/relations', methods=['POST'])
def get_researcher_relations():
    """
    查询作者与关键词/其他作者的关系
    参数:
    - authors: 作者列表 (必填)
    - keywords: 关键词列表 (可选)
    """
    data = request.get_json()

    if not data or 'authors' not in data:
        return jsonify({'error': 'Missing required parameter: authors'}), 400

    authors = data.get('authors', [])
    keywords = data.get('keywords', [])

    try:
        if keywords:
            # 查询作者列表与关键词列表的关系
            result = get_yearly_author_keyword_relations(authors, keywords)
        else:
            # 查询每个作者的所有关系
            result = []
            for author in authors:
                author_data = get_author_relations(author)
                if author_data:
                    result.append(author_data)

        return jsonify({'data': result})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/single', methods=['POST'])
def get_single_researcher_relations():
    """
    查询单个作者的所有关系
    参数:
    - author: 作者姓名 (必填)
    """
    data = request.get_json()

    if not data or 'author' not in data:
        return jsonify({'error': 'Missing required parameter: author'}), 400

    author = data['author']

    try:
        result = get_author_relations(author)
        return jsonify({'data': result if result else {}})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
