import os
from transformers import BertTokenizer

# 强制清除旧缓存（重要！）
os.environ['TRANSFORMERS_CACHE'] = './models'  # 指定新缓存目录
os.environ['HF_ENDPOINT'] = 'https://hf-mirror.com'  # 使用国内镜像

# 确保目录存在
os.makedirs('./models', exist_ok=True)

try:
    # 强制重新下载
    tokenizer = BertTokenizer.from_pretrained(
        'bert-base-chinese',
        cache_dir='./models',
        force_download=True,  # 关键参数
        resume_download=False  # 禁用断点续传
    )
    print("下载成功！模型保存在：", os.path.abspath('./models'))
except Exception as e:
    print(f"下载失败，请尝试手动下载方案：{e}")