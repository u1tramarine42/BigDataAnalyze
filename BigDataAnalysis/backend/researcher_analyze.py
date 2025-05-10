# -*- coding: utf-8 -*-
# 文件名: relationship_analyzer_v2.py

import pandas as pd
import os

# --- 常量定义 ---
AUTHOR_KEYWORD_RELATION_KEY = '作者-关键词'
AUTHOR_AUTHOR_RELATION_KEY = '作者-作者'
ALL_YEARS_KEY = 'all'  # 用于表示所有年份的聚合数据

# --- 文件路径模板 (保持与原脚本一致，可根据实际情况修改或参数化) ---
# 作者-关键词关系矩阵文件
A_K_RELATIONSHIP_MATRIX_TEMPLATE = "./rm/a_k_relationship_matrix_{year}_output.csv"
A_K_RELATIONSHIP_MATRIX_OVERALL = "./rm/a_k_relationship_matrix_output.csv"
# 作者-作者关系矩阵文件
A_A_RELATIONSHIP_MATRIX_TEMPLATE = "./rm/a_a_relationship_matrix_{year}_output.csv"
A_A_RELATIONSHIP_MATRIX_OVERALL = "./rm/a_a_relationship_matrix_output.csv"

# 分析的年份列表 (保持与原脚本一致)
YEARS_TO_ANALYZE = [2019, 2020, 2021, 2022, 2023, 2024, 2025]


def _load_relationship_matrix(filepath):
    """
    辅助函数：加载关系矩阵CSV文件。

    参数:
    filepath (str): CSV文件的路径。

    返回:
    pd.DataFrame or None: 如果成功加载则返回DataFrame，否则返回None。
    """
    if not os.path.exists(filepath):
        # 文件不存在时，可以选择打印信息或静默处理
        # print(f"信息: 矩阵文件未找到: {filepath}")
        return None
    try:
        matrix_df = pd.read_csv(filepath, index_col=0, encoding='utf-8-sig')
        return matrix_df
    except Exception as e:
        print(f"错误: 加载矩阵文件 '{filepath}' 失败: {e}。")
        return None


def _extract_specific_relations(matrix_df, entity_name, target_entities):
    """
    辅助函数：从已加载的矩阵中提取指定实体与目标实体列表之间的非零关系计数。

    参数:
    matrix_df (pd.DataFrame): 已加载的关系矩阵，索引为主要实体（如作者）。
    entity_name (str): 要查询的主要实体的名称（如作者名）。
    target_entities (list): 一个包含目标次要实体名称（如关键词列表或作者列表）的字符串列表。

    返回:
    dict: 一个字典，包含目标实体及其对应的非零计数值。
          例如：{ "关键词X": 计数, "关键词Y": 计数 }
          如果主要实体不在矩阵中，或没有与任何目标实体的非零关联，则返回空字典。
    """
    relations_counts = {}
    if matrix_df is not None and entity_name in matrix_df.index:
        for target_entity in target_entities:
            if target_entity in matrix_df.columns:
                count = matrix_df.loc[entity_name, target_entity]
                if pd.notna(count) and count > 0:
                    relations_counts[target_entity] = int(count)
    return relations_counts


def _extract_all_relations(matrix_df, entity_name):
    """
    辅助函数：从已加载的矩阵中提取指定实体与矩阵中所有其他实体（列）的非零关系计数。

    参数:
    matrix_df (pd.DataFrame): 已加载的关系矩阵，索引为主要实体（如作者）。
    entity_name (str): 要查询的主要实体的名称（如作者名）。

    返回:
    dict: 一个字典，包含所有相关的次要实体及其对应的非零计数值。
          例如：{ "关键词X": 计数, "合作者Y": 计数 }
          如果主要实体不在矩阵中，或没有任何非零关联，则返回空字典。
    """
    relations_counts = {}
    if matrix_df is not None and entity_name in matrix_df.index:
        for column_name in matrix_df.columns:
            count = matrix_df.loc[entity_name, column_name]
            if pd.notna(count) and count > 0:
                relations_counts[column_name] = int(count)
    return relations_counts


def get_yearly_author_keyword_relations(target_authors, target_keywords):
    """
    从按年份存储的作者-关键词及作者-作者关系矩阵CSV文件中，
    查找指定作者列表与指定关键词列表之间的非零关系数据，以及指定作者之间的关系数据。

    参数:
    target_authors (list): 一个包含目标作者姓名的字符串列表。
    target_keywords (list): 一个包含目标关键词的字符串列表。

    返回:
    list: 一个列表，每个元素是一个字典，代表一位作者的数据。格式如下：
          [
            {
              "作者A": {
                "作者-关键词": {
                  "all": { "关键词X": 计数, "关键词Y": 计数 }, // 所有年份汇总数据
                  "2024": { "关键词Z": 计数 } // 特定年份数据
                },
                "作者-作者": {
                  "all": { "作者B": 计数 },
                  "2024": { "作者C": 计数 }
                }
              }
            },
            ...
          ]
          如果某作者在某年份/总体没有与目标关键词/作者的非零关联，则对应条目可能为空字典。
    """
    results = []

    if not target_authors:
        print("警告: 目标作者列表 (target_authors) 为空，无法进行查询。")
        return results
    if not target_keywords:
        print("警告: 目标关键词列表 (target_keywords) 为空，作者-关键词关系查询将受限。")
        # 注意：作者-作者关系仍然可以查询

    for author_name in target_authors:
        author_centric_data = {
            AUTHOR_KEYWORD_RELATION_KEY: {},
            AUTHOR_AUTHOR_RELATION_KEY: {}
        }

        # 1. 处理作者-关键词关系 (总体)
        ak_overall_matrix_df = _load_relationship_matrix(A_K_RELATIONSHIP_MATRIX_OVERALL)
        if ak_overall_matrix_df is not None and target_keywords:  # 仅当关键词列表非空时查询
            overall_ak_relations = _extract_specific_relations(ak_overall_matrix_df, author_name, target_keywords)
            if overall_ak_relations:
                author_centric_data[AUTHOR_KEYWORD_RELATION_KEY][ALL_YEARS_KEY] = overall_ak_relations

        # 2. 处理作者-作者关系 (总体)
        # 对于作者-作者关系，目标作者也是从 target_authors 中选取（排除自身）
        # 如果只想看 target_authors 列表内部作者之间的关系，可以这样做。
        # 如果想看 target_authors 与矩阵中所有其他作者的关系，需要调整 _extract_specific_relations 或使用 _extract_all_relations
        other_target_authors = [ta for ta in target_authors if ta != author_name]  # 排除作者自身

        aa_overall_matrix_df = _load_relationship_matrix(A_A_RELATIONSHIP_MATRIX_OVERALL)
        if aa_overall_matrix_df is not None and other_target_authors:
            overall_aa_relations = _extract_specific_relations(aa_overall_matrix_df, author_name, other_target_authors)
            if overall_aa_relations:
                author_centric_data[AUTHOR_AUTHOR_RELATION_KEY][ALL_YEARS_KEY] = overall_aa_relations

        # 3. 按年份处理
        for year in YEARS_TO_ANALYZE:
            year_str = str(year)  # 文件名模板中使用字符串年份

            # 3a. 处理作者-关键词关系 (按年份)
            ak_yearly_filepath = A_K_RELATIONSHIP_MATRIX_TEMPLATE.format(year=year_str)
            ak_yearly_matrix_df = _load_relationship_matrix(ak_yearly_filepath)
            if ak_yearly_matrix_df is not None and target_keywords:
                yearly_ak_relations = _extract_specific_relations(ak_yearly_matrix_df, author_name, target_keywords)
                if yearly_ak_relations:
                    author_centric_data[AUTHOR_KEYWORD_RELATION_KEY][year_str] = yearly_ak_relations

            # 3b. 处理作者-作者关系 (按年份)
            aa_yearly_filepath = A_A_RELATIONSHIP_MATRIX_TEMPLATE.format(year=year_str)
            aa_yearly_matrix_df = _load_relationship_matrix(aa_yearly_filepath)
            if aa_yearly_matrix_df is not None and other_target_authors:
                yearly_aa_relations = _extract_specific_relations(aa_yearly_matrix_df, author_name,
                                                                  other_target_authors)
                if yearly_aa_relations:
                    author_centric_data[AUTHOR_AUTHOR_RELATION_KEY][year_str] = yearly_aa_relations

        # 只有当作者有任何数据时才添加到结果中
        if author_centric_data[AUTHOR_KEYWORD_RELATION_KEY] or author_centric_data[AUTHOR_AUTHOR_RELATION_KEY]:
            results.append({author_name: author_centric_data})

    return results


def get_author_relations(author_name):
    """
    从按年份存储的作者-关键词及作者-作者关系矩阵CSV文件中，
    查找指定作者与矩阵中所有关键词及所有其他作者的非零关系数据。

    参数:
    author_name (str): 目标作者的姓名。

    返回:
    dict: 一个字典，代表该作者的数据。格式如下：
          {
            "作者A": {
              "作者-关键词": {
                "all": { "关键词X": 计数, "关键词Y": 计数 }, // 所有年份汇总数据
                "2024": { "关键词Z": 计数 } // 特定年份数据
              },
              "作者-作者": {
                "all": { "作者B": 计数, "作者D": 计数 },
                "2024": { "作者C": 计数 }
              }
            }
          }
          如果作者没有任何非零关联，则对应条目可能为空字典，或整个内部字典为空。
          如果作者名为空或未提供，返回空字典。
    """
    if not author_name:
        print("警告: 目标作者姓名 (author_name) 为空，无法进行查询。")
        return {}

    author_centric_data = {
        AUTHOR_KEYWORD_RELATION_KEY: {},
        AUTHOR_AUTHOR_RELATION_KEY: {}
    }

    # 1. 处理作者-关键词关系 (总体) - 与矩阵中所有关键词
    ak_overall_matrix_df = _load_relationship_matrix(A_K_RELATIONSHIP_MATRIX_OVERALL)
    if ak_overall_matrix_df is not None:
        overall_ak_relations = _extract_all_relations(ak_overall_matrix_df, author_name)
        if overall_ak_relations:
            author_centric_data[AUTHOR_KEYWORD_RELATION_KEY][ALL_YEARS_KEY] = overall_ak_relations

    # 2. 处理作者-作者关系 (总体) - 与矩阵中所有其他作者
    aa_overall_matrix_df = _load_relationship_matrix(A_A_RELATIONSHIP_MATRIX_OVERALL)
    if aa_overall_matrix_df is not None:
        overall_aa_relations = _extract_all_relations(aa_overall_matrix_df, author_name)
        # 剔除与作者自身的关系（如果存在）
        if author_name in overall_aa_relations:
            del overall_aa_relations[author_name]
        if overall_aa_relations:
            author_centric_data[AUTHOR_AUTHOR_RELATION_KEY][ALL_YEARS_KEY] = overall_aa_relations

    # 3. 按年份处理
    for year in YEARS_TO_ANALYZE:
        year_str = str(year)

        # 3a. 处理作者-关键词关系 (按年份) - 与矩阵中所有关键词
        ak_yearly_filepath = A_K_RELATIONSHIP_MATRIX_TEMPLATE.format(year=year_str)
        ak_yearly_matrix_df = _load_relationship_matrix(ak_yearly_filepath)
        if ak_yearly_matrix_df is not None:
            yearly_ak_relations = _extract_all_relations(ak_yearly_matrix_df, author_name)
            if yearly_ak_relations:
                author_centric_data[AUTHOR_KEYWORD_RELATION_KEY][year_str] = yearly_ak_relations

        # 3b. 处理作者-作者关系 (按年份) - 与矩阵中所有其他作者
        aa_yearly_filepath = A_A_RELATIONSHIP_MATRIX_TEMPLATE.format(year=year_str)
        aa_yearly_matrix_df = _load_relationship_matrix(aa_yearly_filepath)
        if aa_yearly_matrix_df is not None:
            yearly_aa_relations = _extract_all_relations(aa_yearly_matrix_df, author_name)
            # 剔除与作者自身的关系（如果存在）
            if author_name in yearly_aa_relations:
                del yearly_aa_relations[author_name]
            if yearly_aa_relations:
                author_centric_data[AUTHOR_AUTHOR_RELATION_KEY][year_str] = yearly_aa_relations

    if author_centric_data[AUTHOR_KEYWORD_RELATION_KEY] or author_centric_data[AUTHOR_AUTHOR_RELATION_KEY]:
        return {author_name: author_centric_data}
    else:
        # 如果该作者没有任何数据，可以返回一个包含作者名但内部为空的结构，或直接空字典
        # return {author_name: author_centric_data} # 包含作者名，内部为空
        return {}  # 直接返回空字典，表示未查到该作者的任何有效数据


if __name__ == '__main__':
    print("--- 关系分析脚本执行示例 ---")

    # --- 示例1: 查询特定作者列表与特定关键词列表的关系 ---
    # 假设的查询参数
    sample_authors = ['王宝楠', '水恒华', '张三']  # 张三可能不存在于某些文件中
    sample_keywords = ['量子退火', 'D-Wave量子计算机', '人工智能']  # 人工智能可能不存在

    print(f"\n查询1: 作者列表 {sample_authors} 与关键词列表 {sample_keywords} 的关系")
    # 注意：原脚本中的函数名为 get_yearly_author_keyword_relations，此处保持一致
    retrieved_data_specific = get_yearly_author_keyword_relations(
        target_authors=sample_authors,
        target_keywords=sample_keywords,
    )

    print("\n查询1结果:")
    if retrieved_data_specific:
        for item in retrieved_data_specific:
            print(item)
    else:
        print("未查询到任何数据或输入参数不满足要求。")

    # --- 示例2: 查询单个作者与所有关键词/其他作者的关系 ---
    sample_single_author = '王宝楠'
    print(f"\n查询2: 作者 '{sample_single_author}' 与所有相关实体的关系")
    # 注意：原脚本中的函数名为 get_author_keyword_relations，此处修改为更通用的 get_author_relations
    # 并调整其内部逻辑以匹配“与所有”这一概念
    retrieved_data_single_author_all = get_author_relations(
        author_name=sample_single_author
    )

    print("\n查询2结果:")
    if retrieved_data_single_author_all:
        # 由于函数返回单个作者的字典或空字典
        print(retrieved_data_single_author_all)
    else:
        print(f"未查询到作者 '{sample_single_author}' 的任何数据或作者名为空。")

    # --- 示例3: 查询一个可能不存在的作者 ---
    non_existent_author = '李四'
    print(f"\n查询3: 作者 '{non_existent_author}' 与所有相关实体的关系")
    retrieved_data_non_existent = get_author_relations(
        author_name=non_existent_author
    )
    print("\n查询3结果:")
    if retrieved_data_non_existent:
        print(retrieved_data_non_existent)
    else:
        print(f"未查询到作者 '{non_existent_author}' 的任何数据。")

    # --- 重要提示 ---
    # 为了使此脚本成功运行并返回数据，你需要确保：
    # 1. `./rm/` 目录存在。
    # 2. 相关的CSV文件 (如 a_k_relationship_matrix_2019_output.csv, a_k_relationship_matrix_output.csv 等)
    #    存在于 `./rm/` 目录下，并且其内部格式符合脚本预期（第一列为作者名作为索引，列为关键词或其他作者名）。
    # 3. CSV文件使用 'utf-8-sig' 编码。

    # 如果没有这些文件，脚本中的 _load_relationship_matrix 函数会返回 None，
    # 从而导致查询结果为空。你可以根据需要创建一些示例CSV文件进行测试。
    # 例如，一个简单的 a_k_relationship_matrix_output.csv 文件可能如下：
    # ,量子退火,D-Wave量子计算机,机器学习
    # 王宝楠,5,3,0
    # 水恒华,0,2,7

    print("\n--- 脚本执行完毕 ---")