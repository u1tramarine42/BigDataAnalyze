# -*- coding: utf-8 -*-
from __future__ import print_function

import codecs

import pandas as pd
import csv
import numpy as np
import time
from Segment_ import Seg
import gensim
from gensim.models.word2vec import LineSentence
from gensim.models import Word2Vec
from sklearn import svm
from sklearn.model_selection import train_test_split
from sklearn.metrics import confusion_matrix
from classification_utilities import display_cm
import joblib
import multiprocessing
import warnings

MODEL = None
WORD2VEC = None
SEG = None

warnings.filterwarnings(action='ignore', category=UserWarning, module='gensim')
def init_models():
    global MODEL, WORD2VEC, SEG
    if MODEL is None:
        MODEL = joblib.load("./model/model.m")
    if WORD2VEC is None:
        WORD2VEC = gensim.models.KeyedVectors.load_word2vec_format(
            './data/data.seg.text.vector', binary=False)
    if SEG is None:
        SEG = Seg()

def read_data():
    wds = Seg()
    target = codecs.open('./data/data.seg.txt', 'w', encoding='utf8')
    with open('./data/data.txt', encoding='utf8') as f:
        line = f.readline()
        while line:
            seg_list = wds.cut(line, cut_all=False)
            line_seg = ' '.join(seg_list)
            if len(line_seg) < 50:
                pass
            else:
                target.writelines(line_seg)
            line = f.readline()
        f.close()
        target.close()


def getWordVecs(wordList, model):
    vecs = []
    for word in wordList:
        word = word.replace('\n', '')
        try:
            # 如果是Word2Vec模型使用model.wv[word]，如果是KeyedVectors直接使用model[word]
            vec = model[word] if isinstance(model, gensim.models.KeyedVectors) else model.wv[word]
            vecs.append(vec)
        except KeyError:
            continue
    return np.array(vecs, dtype='float')


def buildVecs(data, model):
    label = []
    fileVecs = []
    for line in data:
        wordList = line.split(' ')
        vecs = getWordVecs(wordList, model)
        if len(vecs) > 0:
            vecsArray = sum(np.array(vecs)) / len(vecs)
            fileVecs.append(vecsArray)
            label.append(line[0])
    return fileVecs, label


def get_data_wordvec():
    inp = './data/data.seg.txt'
    f = codecs.open(inp, mode='r', encoding='utf-8')
    line = f.readlines()
    data = []
    for i in line:
        data.append(i)
    f.close()
    return data


def word2vec_():
    inp = './data/data.seg.txt'
    outp = './data/data.seg.text.vector'
    # 检查模型文件是否存在
    if not os.path.exists(outp):
        f = codecs.open(inp, mode='r', encoding='utf-8')
        line = f.readlines()
        data = []
        for i in line:
            data.append(i)
        f.close()

        model_ = Word2Vec(LineSentence(inp), vector_size=100, window=5, min_count=5,
                          workers=multiprocessing.cpu_count())
        model_.wv.save_word2vec_format(outp, binary=False)
        Input22, label = buildVecs(data, model_)

        X = Input22[:]
        df_x = pd.DataFrame(X)
        df_y = pd.DataFrame(label)
        data = pd.concat([df_y, df_x], axis=1)
        data.to_csv('./data/word2vec.csv')


def classification_():
    # 检查分类模型是否存在
    if not os.path.exists("./model/model.m"):
        df = pd.read_csv('./data/word2vec.csv')
        y = df.iloc[:, 1]
        labels = ["表达开心", "表达伤心", "表达恶心", "表达生气", "表达害怕", "表达惊喜"]
        x = df.iloc[:, 2:]
        X_train, X_test, y_train, y_test = train_test_split(x, y, test_size=0.3, random_state=42)
        print('支持向量机....')
        clf = svm.SVC(C=100, probability=True)
        clf.fit(X_train, y_train)
        joblib.dump(clf, "./model/model.m")
        print('混淆矩阵')
        cv_conf = confusion_matrix(y_test, clf.predict(X_test))
        display_cm(cv_conf, labels, display_metrics=True, hide_zeros=False)
        print('准确率: %.2f' % clf.score(x, y))
        print('..................................')


def predict_(text):
    init_models()  # 初始化模型

    # 分词
    seg_list = SEG.cut(text, cut_all=False)
    line_seg = ' '.join(seg_list).split(' ')

    # 获取词向量
    vecs = []
    for word in line_seg:
        try:
            vecs.append(WORD2VEC[word])
        except KeyError:
            continue

    if vecs:
        vecsArray = sum(np.array(vecs)) / len(vecs)
        vecsArray = vecsArray.reshape(1, 100)
        kk = MODEL.predict(vecsArray)

        # 使用字典映射提高效率
        emotion_map = {
            0: "Confused",
            1: "Critical",
            2: "Supportive",
            3: "Neutral",
            4: "Anticipatory",
            5: "Surprised"
        }
        return emotion_map.get(kk[0], "Neutral")
    return "Neutral"

if __name__ == '__main__':
    import os

    # 确保目录存在
    os.makedirs('./data', exist_ok=True)
    os.makedirs('./model', exist_ok=True)

    # 示例用法
    read_data()
    word2vec_()
    classification_()

    # 测试预测
    test_text = "i am feel lonely"
    result = predict_(test_text)
    print(f"预测结果: {result}")





