import requests
from flask import Flask, request, jsonify, render_template_string

app = Flask(__name__)
app.json.ensure_ascii = False
# 定义 HTML 模板字符串
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <title>论文分析</title>
</head>
<body>
    <h1>论文摘要分析</h1>
    <form action="/analyze_paper_form" method="post">
        <label for="abstract">请输入论文摘要:</label><br>
        <textarea id="abstract" name="abstract" rows="4" cols="50"></textarea><br>
        <input type="submit" value="提交">
    </form>
    {% if result %}
        <h1>分析结果</h1>
        <pre>{{ result|tojson(indent=4) }}</pre>
    {% endif %}
</body>
</html>
"""

@app.route('/tester')
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route('/analyze_paper_form', methods=['POST'])
def analyze_paper():
    abstract = request.form.get('abstract', '')
    if not abstract:
        return render_template_string(HTML_TEMPLATE, result={"error": "缺少摘要内容"})

    # 发送POST请求到分词服务
    response = requests.post(
        'http://127.0.0.1:5000/analyze_paper',
        json={'abstract': abstract}
    )

    if response.status_code == 200:
        result = {
            "分析结果": response.json(),
            "原始摘要": abstract

        }
    else:
        result = {"error": "分词服务调用失败"}

    return render_template_string(HTML_TEMPLATE, result=result)

if __name__ == '__main__':
    app.run(debug=True,port=5001)