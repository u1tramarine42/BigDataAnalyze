# 论文分析系统前端

本项目是论文分析系统的前端部分，基于Vue.js开发，提供论文情感分析和主题分析功能的可视化界面。

## 功能特性

- 论文文本输入界面
- 情感分析可视化（雷达图形式展示六种情感倾向）
- 主题分析可视化（展示多个主题及其关键词）

## 项目设置

### 安装依赖
```
npm install
```

### 开发模式启动
```
npm run serve
```

### 编译生产版本
```
npm run build
```

## 使用说明

1. 确保后端服务已启动（默认地址：http://localhost:5000）
2. 在文本框中输入或粘贴论文内容
3. 点击"分析"按钮进行处理
4. 在下方选项卡中查看分析结果

## 技术栈

- Vue.js 3
- Element Plus UI库
- ECharts 图表库
- Axios HTTP客户端

### Lints and fixes files
```
npm run lint
```

### Customize configuration
See [Configuration Reference](https://cli.vuejs.org/config/).
