<template>
  <div class="send-message">
    <el-card>
      <!-- 消息类型选择 -->
      <el-tabs v-model="messageType" type="border-card" @tab-change="handleTabChange">
        <el-tab-pane label="文本消息" name="text">
          <el-form :model="textForm" label-width="100px" size="large">
            <el-form-item label="消息内容" required>
              <el-input
                v-model="textForm.content"
                type="textarea"
                :rows="6"
                placeholder="请输入消息内容..."
                maxlength="4096"
                show-word-limit
              />
            </el-form-item>
            
            <el-form-item label="@成员">
              <el-select
                v-model="textForm.mentioned_list"
                multiple
                placeholder="选择要@的成员（可选）"
                style="width: 100%"
              >
                <el-option label="@所有人" value="@all" />
                <el-option label="张三" value="zhangsan" />
                <el-option label="李四" value="lisi" />
                <el-option label="王五" value="wangwu" />
              </el-select>
            </el-form-item>
            
            <el-form-item label="@手机号">
              <el-select
                v-model="textForm.mentioned_mobile_list"
                multiple
                placeholder="选择要@的手机号（可选）"
                style="width: 100%"
              >
                <el-option label="13800138000" value="13800138000" />
                <el-option label="13900139000" value="13900139000" />
              </el-select>
            </el-form-item>
            
            <el-form-item>
              <el-button type="primary" size="large" :loading="sending" @click="sendTextMessage">
                <el-icon><Send /></el-icon>
                立即发送
              </el-button>
            </el-form-item>
          </el-form>
        </el-tab-pane>

        <el-tab-pane label="Markdown 消息" name="markdown">
          <el-form :model="markdownForm" label-width="100px" size="large">
            <el-form-item label="Markdown 内容" required>
              <el-input
                v-model="markdownForm.content"
                type="textarea"
                :rows="10"
                placeholder="# 标题&#10;&#10;这是 **Markdown** 内容..."
                maxlength="4096"
                show-word-limit
              />
            </el-form-item>
            
            <el-form-item label="预览">
              <div class="markdown-preview" v-html="renderedMarkdown"></div>
            </el-form-item>
            
            <el-form-item>
              <el-button type="success" size="large" :loading="sending" @click="sendMarkdownMessage">
                <el-icon><Send /></el-icon>
                立即发送
              </el-button>
            </el-form-item>
          </el-form>
        </el-tab-pane>

        <el-tab-pane label="图片消息" name="image">
          <el-form :model="imageForm" label-width="100px" size="large">
            <el-form-item label="选择图片" required>
              <el-upload
                class="image-uploader"
                drag
                :auto-upload="false"
                :on-change="handleImageChange"
                :limit="1"
                accept="image/*"
              >
                <el-icon class="el-icon--upload"><upload-filled /></el-icon>
                <div class="el-upload__text">
                  拖拽文件到此处或<em>点击上传</em>
                </div>
              </el-upload>
            </el-form-item>
            
            <el-form-item v-if="imagePreview" label="图片预览">
              <el-image :src="imagePreview" fit="cover" style="max-width: 300px; max-height: 300px;" />
            </el-form-item>
            
            <el-form-item label="MD5 值">
              <el-input v-model="imageForm.md5" readonly placeholder="自动计算" />
            </el-form-item>
            
            <el-form-item>
              <el-button type="warning" size="large" :loading="sending" @click="sendImageMessage">
                <el-icon><Send /></el-icon>
                立即发送
              </el-button>
            </el-form-item>
          </el-form>
        </el-tab-pane>

        <el-tab-pane label="图文消息" name="news">
          <el-form :model="newsForm" label-width="100px" size="large">
            <el-form-item label="图文列表">
              <div v-for="(article, index) in newsForm.articles" :key="index" class="article-item">
                <el-card shadow="hover" class="article-card">
                  <div class="article-header">
                    <span class="article-title">文章 {{ index + 1 }}</span>
                    <el-button
                      v-if="newsForm.articles.length > 1"
                      type="danger"
                      text
                      size="small"
                      @click="removeArticle(index)"
                    >
                      <el-icon><Delete /></el-icon>
                    </el-button>
                  </div>
                  
                  <el-form-item label="标题" required>
                    <el-input v-model="article.title" placeholder="文章标题" maxlength="128" show-word-limit />
                  </el-form-item>
                  
                  <el-form-item label="描述">
                    <el-input
                      v-model="article.description"
                      type="textarea"
                      :rows="2"
                      placeholder="文章描述（可选）"
                      maxlength="512"
                      show-word-limit
                    />
                  </el-form-item>
                  
                  <el-form-item label="链接" required>
                    <el-input v-model="article.url" placeholder="https://example.com" />
                  </el-form-item>
                  
                  <el-form-item label="图片链接">
                    <el-input v-model="article.picurl" placeholder="https://example.com/image.jpg（可选）" />
                  </el-form-item>
                </el-card>
              </div>
              
              <el-button
                v-if="newsForm.articles.length < 10"
                type="primary"
                plain
                @click="addArticle"
                style="width: 100%; margin-top: 10px;"
              >
                <el-icon><Plus /></el-icon>
                添加文章
              </el-button>
            </el-form-item>
            
            <el-form-item>
              <el-button type="primary" size="large" :loading="sending" @click="sendNewsMessage">
                <el-icon><Send /></el-icon>
                立即发送
              </el-button>
            </el-form-item>
          </el-form>
        </el-tab-pane>

        <el-tab-pane label="卡片消息" name="card">
          <el-form :model="cardForm" label-width="120px" size="large">
            <el-form-item label="卡片类型" required>
              <el-select v-model="cardForm.card_type" placeholder="选择卡片类型" style="width: 100%">
                <el-option label="文本通知型" value="text_notice" />
                <el-option label="图文展示型" value="news_notice" />
              </el-select>
            </el-form-item>
            
            <el-form-item label="主标题" required>
              <el-input v-model="cardForm.main_title" placeholder="卡片主标题" maxlength="128" show-word-limit />
            </el-form-item>
            
            <el-form-item label="主描述">
              <el-input
                v-model="cardForm.main_desc"
                type="textarea"
                :rows="3"
                placeholder="卡片主描述（可选）"
                maxlength="512"
                show-word-limit
              />
            </el-form-item>
            
            <el-form-item label="动作类型" required>
              <el-radio-group v-model="cardForm.card_action_type">
                <el-radio :label="1">打开 URL</el-radio>
                <el-radio :label="2">打开小程序</el-radio>
              </el-radio-group>
            </el-form-item>
            
            <el-form-item v-if="cardForm.card_action_type === 1" label="URL">
              <el-input v-model="cardForm.card_action_url" placeholder="https://example.com" />
            </el-form-item>
            
            <el-form-item v-if="cardForm.card_action_type === 2" label="小程序 AppID">
              <el-input v-model="cardForm.card_action_appid" placeholder="小程序 AppID" />
            </el-form-item>
            
            <el-form-item v-if="cardForm.card_action_type === 2" label="页面路径">
              <el-input v-model="cardForm.card_action_pagepath" placeholder="/pages/index" />
            </el-form-item>
            
            <el-form-item>
              <el-button type="info" size="large" :loading="sending" @click="sendCardMessage">
                <el-icon><Send /></el-icon>
                立即发送
              </el-button>
            </el-form-item>
          </el-form>
        </el-tab-pane>
      </el-tabs>
    </el-card>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { useAppStore } from '@/stores/app'
import { messageApi } from '@/utils/api'
import { getWebSocketClient } from '@/utils/websocket'
import MarkdownIt from 'markdown-it'

const route = useRoute()
const appStore = useAppStore()

const md = new MarkdownIt()
const messageType = ref('text')
const sending = ref(false)

// 文本消息表单
const textForm = ref({
  content: '',
  mentioned_list: [],
  mentioned_mobile_list: []
})

// Markdown 消息表单
const markdownForm = ref({
  content: ''
})

// 图片消息表单
const imageForm = ref({
  base64_data: '',
  md5: ''
})
const imagePreview = ref('')
const selectedFile = ref(null)

// 图文消息表单
const newsForm = ref({
  articles: [
    {
      title: '',
      description: '',
      url: '',
      picurl: ''
    }
  ]
})

// 卡片消息表单
const cardForm = ref({
  card_type: 'text_notice',
  main_title: '',
  main_desc: '',
  card_action_type: 1,
  card_action_url: '',
  card_action_appid: '',
  card_action_pagepath: ''
})

// Markdown 预览
const renderedMarkdown = computed(() => {
  return md.render(markdownForm.value.content || '')
})

// 处理图片选择
const handleImageChange = (file) => {
  selectedFile.value = file.raw
  const reader = new FileReader()
  
  reader.onload = (e) => {
    imagePreview.value = e.target.result
    imageForm.value.base64_data = e.target.result.split(',')[1]
    
    // 计算 MD5 - 使用简单哈希函数
    imageForm.value.md5 = simpleHash(e.target.result)
  }
  
  reader.readAsDataURL(file.raw)
}

// 简单哈希函数（备用）
const simpleHash = (str) => {
  let hash = 0
  for (let i = 0; i < str.length; i++) {
    const char = str.charCodeAt(i)
    hash = ((hash << 5) - hash) + char
    hash = hash & hash
  }
  return Math.abs(hash).toString(16)
}

// 添加文章
const addArticle = () => {
  newsForm.value.articles.push({
    title: '',
    description: '',
    url: '',
    picurl: ''
  })
}

// 删除文章
const removeArticle = (index) => {
  newsForm.value.articles.splice(index, 1)
}

// Tab 切换
const handleTabChange = (type) => {
  messageType.value = type
}

// 发送文本消息
const sendTextMessage = async () => {
  if (!textForm.value.content.trim()) {
    ElMessage.warning('请输入消息内容')
    return
  }

  await sendMessage('text', async () => {
    return await messageApi.sendText({
      content: textForm.value.content,
      mentioned_list: textForm.value.mentioned_list,
      mentioned_mobile_list: textForm.value.mentioned_mobile_list
    })
  })
}

// 发送 Markdown 消息
const sendMarkdownMessage = async () => {
  if (!markdownForm.value.content.trim()) {
    ElMessage.warning('请输入 Markdown 内容')
    return
  }

  await sendMessage('markdown', async () => {
    return await messageApi.sendMarkdown({
      content: markdownForm.value.content
    })
  })
}

// 发送图片消息
const sendImageMessage = async () => {
  if (!imageForm.value.base64_data) {
    ElMessage.warning('请选择图片')
    return
  }

  await sendMessage('image', async () => {
    return await messageApi.sendImage({
      base64_data: imageForm.value.base64_data,
      md5: imageForm.value.md5
    })
  })
}

// 发送图文消息
const sendNewsMessage = async () => {
  const validArticles = newsForm.value.articles.filter(a => a.title && a.url)
  if (validArticles.length === 0) {
    ElMessage.warning('请至少填写一篇图文的标题和链接')
    return
  }

  await sendMessage('news', async () => {
    return await messageApi.sendNews({
      articles: validArticles
    })
  })
}

// 发送卡片消息
const sendCardMessage = async () => {
  if (!cardForm.value.main_title) {
    ElMessage.warning('请输入主标题')
    return
  }

  await sendMessage('template_card', async () => {
    return await messageApi.sendTemplateCard({
      card_type: cardForm.value.card_type,
      main_title: cardForm.value.main_title,
      main_desc: cardForm.value.main_desc,
      card_action_type: cardForm.value.card_action_type,
      card_action_url: cardForm.value.card_action_url,
      card_action_appid: cardForm.value.card_action_appid,
      card_action_pagepath: cardForm.value.card_action_pagepath
    })
  })
}

// 通用发送逻辑
const sendMessage = async (type, sendFn) => {
  sending.value = true
  
  try {
    const result = await sendFn()
    
    // 记录历史
    appStore.addHistory({
      type,
      content: type === 'text' ? textForm.value.content : 
               type === 'markdown' ? markdownForm.value.content : 
               type === 'news' ? `${newsForm.value.articles.length}篇图文` :
               type === 'card' ? cardForm.value.main_title : '图片',
      success: result.success,
      message: result.message
    })
    
    if (result.success) {
      ElMessage.success('发送成功')
      // 清空表单
      resetForm(type)
    } else {
      ElMessage.error(`发送失败：${result.message}`)
    }
  } catch (error) {
    ElMessage.error(`发送失败：${error.message}`)
    appStore.addHistory({
      type,
      content: '发送失败',
      success: false,
      message: error.message
    })
  } finally {
    sending.value = false
  }
}

// 重置表单
const resetForm = (type) => {
  if (type === 'text') {
    textForm.value = {
      content: '',
      mentioned_list: [],
      mentioned_mobile_list: []
    }
  } else if (type === 'markdown') {
    markdownForm.value = { content: '' }
  } else if (type === 'image') {
    imageForm.value = { base64_data: '', md5: '' }
    imagePreview.value = ''
    selectedFile.value = null
  } else if (type === 'news') {
    newsForm.value = {
      articles: [{ title: '', description: '', url: '', picurl: '' }]
    }
  } else if (type === 'card') {
    cardForm.value = {
      card_type: 'text_notice',
      main_title: '',
      main_desc: '',
      card_action_type: 1,
      card_action_url: '',
      card_action_appid: '',
      card_action_pagepath: ''
    }
  }
}

// 根据 URL 参数切换 Tab
onMounted(() => {
  const type = route.query.type
  if (type && ['text', 'markdown', 'image', 'news', 'card'].includes(type)) {
    messageType.value = type
  }
})
</script>

<style scoped>
.send-message {
  padding: 0;
}

.markdown-preview {
  border: 1px solid #dcdfe6;
  border-radius: 4px;
  padding: 15px;
  background-color: #f5f7fa;
  min-height: 100px;
}

.image-uploader {
  width: 100%;
}

.article-item {
  margin-bottom: 15px;
}

.article-card {
  border-left: 3px solid #409EFF;
}

.article-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 15px;
}

.article-title {
  font-weight: bold;
  font-size: 16px;
  color: #303133;
}
</style>
