from flask import Flask, request, jsonify
from researcher_analyze import get_yearly_author_keyword_relations, get_author_relations

app = Flask(__name__)


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
    app.run(host='0.0.0.0', port=5000, debug=True)