import axios from 'axios'

const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api/v1',
  timeout: 30000
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
    console.error('API Error:', error)
    return Promise.reject(error)
  }
)

// API 方法
export const messageApi = {
  // 发送文本消息
  sendText(data) {
    return api.post('/text', data)
  },

  // 发送 Markdown 消息
  sendMarkdown(data) {
    return api.post('/markdown', data)
  },

  // 发送图片消息
  sendImage(data) {
    return api.post('/image', data)
  },

  // 发送图文消息
  sendNews(data) {
    return api.post('/news', data)
  },

  // 发送模板卡片消息
  sendTemplateCard(data) {
    return api.post('/template-card', data)
  },

  // 上传文件
  uploadFile(data) {
    return api.post('/upload-file', null, { params: data })
  },

  // 获取机器人信息
  getBotInfo() {
    return api.get('/bot-info')
  }
}

// 健康检查
export const healthApi = {
  check() {
    return axios.get(import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/health')
  }
}

export default api
