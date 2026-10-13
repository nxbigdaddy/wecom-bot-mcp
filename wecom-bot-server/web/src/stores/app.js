import { defineStore } from 'pinia'
import { ref } from 'vue'

export const useAppStore = defineStore('app', () => {
  const apiBaseUrl = ref(import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000')
  const wsUrl = ref(import.meta.env.VITE_WS_URL || 'ws://localhost:8000/ws')
  const isConnected = ref(false)
  const botInfo = ref(null)
  
  // 发送历史
  const sendHistory = ref([])

  // 添加发送记录
  const addHistory = (record) => {
    sendHistory.value.unshift({
      ...record,
      timestamp: new Date().toISOString()
    })
    // 只保留最近 100 条
    if (sendHistory.value.length > 100) {
      sendHistory.value = sendHistory.value.slice(0, 100)
    }
  }

  // 清空历史
  const clearHistory = () => {
    sendHistory.value = []
  }

  return {
    apiBaseUrl,
    wsUrl,
    isConnected,
    botInfo,
    sendHistory,
    addHistory,
    clearHistory
  }
})
