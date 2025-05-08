import { createApp } from 'vue'
import App from './App.vue'
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'
import axios from 'axios'

// 处理ResizeObserver错误
const debounce = (fn, delay) => {
  let timer = null
  return function() {
    let context = this
    let args = arguments
    clearTimeout(timer)
    timer = setTimeout(function() {
      fn.apply(context, args)
    }, delay)
  }
}

// 覆盖原生的ResizeObserver，以防止ResizeObserver loop limit exceeded错误
const _ResizeObserver = window.ResizeObserver
window.ResizeObserver = class ResizeObserver extends _ResizeObserver {
  constructor(callback) {
    callback = debounce(callback, 20)
    super(callback)
  }
}

// 全局捕获浏览器控制台错误
window.addEventListener('error', (event) => {
  if (event.message === 'ResizeObserver loop limit exceeded' || 
      event.message === 'ResizeObserver loop completed with undelivered notifications.') {
    event.stopImmediatePropagation()
  }
})

const app = createApp(App)
app.use(ElementPlus)
app.config.globalProperties.$axios = axios

// 添加全局错误处理器
app.config.errorHandler = (err, vm, info) => {
  // 忽略ResizeObserver错误
  if (err.message && (
    err.message.includes('ResizeObserver') || 
    err.message.includes('loop limit exceeded') ||
    err.message.includes('loop completed with undelivered notifications')
  )) {
    return; // 忽略这类错误
  }
  console.error('Global error:', err, info);
};

// 添加全局警告处理器
app.config.warnHandler = (msg, vm, trace) => {
  // 忽略特定的警告
  if (msg.includes('ResizeObserver')) {
    return; // 忽略这类警告
  }
  console.warn('Global warning:', msg, trace);
};

app.mount('#app')
