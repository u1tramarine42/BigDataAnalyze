import axios from 'axios'

// 配置API基础URL
const baseURL = 'http://localhost:5000'

// 创建axios实例
const api = axios.create({
  baseURL,
  timeout: 0, // 0表示无超时限制
  headers: {
    'Content-Type': 'application/json'
  }
})

// 请求拦截器
api.interceptors.request.use(
  config => {
    return config
  },
  error => {
    return Promise.reject(error)
  }
)

// 响应拦截器
api.interceptors.response.use(
  response => {
    return response.data
  },
  error => {
    return Promise.reject(error)
  }
)

// 情感分析API
export function emotionAnalyze(text) {
  return api.post('/analyze', { text })
}

// 主题分析API
export function topicAnalyze(text) {
  return api.post('/extract_keywords', { text })
}

// 论文关键词分析API
export function paperAnalyze(data) {
  return api.post('/analyze_paper', data)
}

// 论文信息提取API
export function extractPaperInfo(text) {
  return api.post('/extract_paper', { text })
}

export default api 