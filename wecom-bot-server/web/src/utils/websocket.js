export class WebSocketClient {
  constructor(url) {
    this.url = url
    this.ws = null
    this.reconnectInterval = 5000
    this.heartbeatInterval = null
    this.messageHandlers = []
    this.statusHandlers = []
  }

  connect() {
    return new Promise((resolve, reject) => {
      try {
        this.ws = new WebSocket(this.url)

        this.ws.onopen = () => {
          console.log('WebSocket connected')
          this.startHeartbeat()
          this.notifyStatus(true)
          resolve()
        }

        this.ws.onmessage = (event) => {
          const data = JSON.parse(event.data)
          this.notifyMessage(data)
        }

        this.ws.onerror = (error) => {
          console.error('WebSocket error:', error)
          reject(error)
        }

        this.ws.onclose = () => {
          console.log('WebSocket closed, reconnecting...')
          this.stopHeartbeat()
          this.notifyStatus(false)
          setTimeout(() => this.connect(), this.reconnectInterval)
        }
      } catch (error) {
        reject(error)
      }
    })
  }

  startHeartbeat() {
    this.heartbeatInterval = setInterval(() => {
      if (this.ws && this.ws.readyState === WebSocket.OPEN) {
        this.send({ type: 'ping' })
      }
    }, 30000)
  }

  stopHeartbeat() {
    if (this.heartbeatInterval) {
      clearInterval(this.heartbeatInterval)
      this.heartbeatInterval = null
    }
  }

  send(message) {
    return new Promise((resolve, reject) => {
      if (!this.ws || this.ws.readyState !== WebSocket.OPEN) {
        reject(new Error('WebSocket not connected'))
        return
      }

      const requestId = `req_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`
      const messageWithId = {
        ...message,
        request_id: requestId
      }

      // 临时处理器处理单次响应
      const handler = (data) => {
        if (data.request_id === requestId) {
          this.removeMessageHandler(tempHandler)
          resolve(data)
        }
      }

      const tempHandler = handler
      this.addMessageHandler(tempHandler)

      this.ws.send(JSON.stringify(messageWithId))
    })
  }

  sendText(content, mentionedList = []) {
    return this.send({
      type: 'text',
      data: {
        content,
        mentioned_list: mentionedList
      }
    })
  }

  sendMarkdown(content) {
    return this.send({
      type: 'markdown',
      data: { content }
    })
  }

  sendImage(base64Data, md5) {
    return this.send({
      type: 'image',
      data: {
        base64_data: base64Data,
        md5: md5
      }
    })
  }

  sendNews(articles) {
    return this.send({
      type: 'news',
      data: { articles }
    })
  }

  sendTemplateCard(config) {
    return this.send({
      type: 'template_card',
      data: config
    })
  }

  addMessageHandler(handler) {
    this.messageHandlers.push(handler)
  }

  removeMessageHandler(handler) {
    const index = this.messageHandlers.indexOf(handler)
    if (index > -1) {
      this.messageHandlers.splice(index, 1)
    }
  }

  notifyMessage(data) {
    this.messageHandlers.forEach(handler => {
      try {
        handler(data)
      } catch (error) {
        console.error('Message handler error:', error)
      }
    })
  }

  addStatusHandler(handler) {
    this.statusHandlers.push(handler)
  }

  removeStatusHandler(handler) {
    const index = this.statusHandlers.indexOf(handler)
    if (index > -1) {
      this.statusHandlers.splice(index, 1)
    }
  }

  notifyStatus(isConnected) {
    this.statusHandlers.forEach(handler => {
      try {
        handler(isConnected)
      } catch (error) {
        console.error('Status handler error:', error)
      }
    })
  }

  disconnect() {
    this.stopHeartbeat()
    if (this.ws) {
      this.ws.close()
      this.ws = null
    }
  }
}

// 创建全局实例
let wsInstance = null

export function getWebSocketClient(url) {
  if (!wsInstance) {
    wsInstance = new WebSocketClient(url)
  }
  return wsInstance
}
