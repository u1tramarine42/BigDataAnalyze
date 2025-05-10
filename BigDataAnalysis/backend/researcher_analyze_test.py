import requests
import json

# 测试服务器配置
BASE_URL = "http://127.0.0.1:5000/"


def test_relations_endpoint():
    """测试/relations接口"""
    url = f"{BASE_URL}relations"

    print("\n=== 测试/relations接口 ===")

    # 测试用例1: 正常查询作者与关键词的关系
    print("\n测试用例1: 正常查询作者与关键词的关系")
    data = {
        "authors": ["王宝楠", "水恒华"],
        "keywords": ["量子退火", "D-Wave量子计算机","人工智能"]
    }
    make_request(url, data)

    # 测试用例2: 只查询作者关系(不提供keywords)
    print("\n测试用例2: 只查询作者关系")
    data = {
        "authors": ["王宝楠", "张三"]
    }
    make_request(url, data)

    # 测试用例3: 缺少必要参数
    print("\n测试用例3: 缺少必要参数")
    data = {
        "keywords": ["量子退火"]
    }
    make_request(url, data)


def test_single_endpoint():
    """测试/single接口"""
    url = f"{BASE_URL}single"

    print("\n=== 测试/single接口 ===")

    # 测试用例1: 正常查询单个作者
    print("\n测试用例1: 正常查询单个作者")
    data = {
        "author": "王潮"
    }
    make_request(url, data)

    # 测试用例2: 查询不存在的作者
    print("\n测试用例2: 查询不存在的作者")
    data = {
        "author": "李四"
    }
    make_request(url, data)

    # 测试用例3: 缺少必要参数
    print("\n测试用例3: 缺少必要参数")
    data = {}
    make_request(url, data)


def make_request(url, data):
    """通用请求函数"""
    try:
        response = requests.post(url, json=data)
        response.raise_for_status()
        print(f"请求成功 - 状态码: {response.status_code}")
        print("响应内容:")
        print(json.dumps(response.json(), indent=2, ensure_ascii=False))
    except requests.exceptions.HTTPError as err:
        print(f"HTTP错误: {err}")
    except requests.exceptions.RequestException as err:
        print(f"请求错误: {err}")


if __name__ == "__main__":
    print("=== 开始测试研究者分析API ===")
    test_relations_endpoint()
    test_single_endpoint()
    print("\n=== 测试完成 ===")