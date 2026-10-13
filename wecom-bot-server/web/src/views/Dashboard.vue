<template>
  <div class="dashboard">
    <!-- 统计卡片 -->
    <el-row :gutter="20" class="stats-row">
      <el-col :span="6">
        <el-card class="stat-card">
          <div class="stat-content">
            <div class="stat-icon" style="background-color: #409EFF;">
              <el-icon :size="32"><Message /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-value">{{ todayCount }}</div>
              <div class="stat-label">今日发送</div>
            </div>
          </div>
        </el-card>
      </el-col>

      <el-col :span="6">
        <el-card class="stat-card">
          <div class="stat-content">
            <div class="stat-icon" style="background-color: #67C23A;">
              <el-icon :size="32"><SuccessFilled /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-value">{{ successCount }}</div>
              <div class="stat-label">成功数量</div>
            </div>
          </div>
        </el-card>
      </el-col>

      <el-col :span="6">
        <el-card class="stat-card">
          <div class="stat-content">
            <div class="stat-icon" style="background-color: #E6A23C;">
              <el-icon :size="32"><Document /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-value">{{ totalHistory }}</div>
              <div class="stat-label">总记录数</div>
            </div>
          </div>
        </el-card>
      </el-col>

      <el-col :span="6">
        <el-card class="stat-card">
          <div class="stat-content">
            <div class="stat-icon" style="background-color: #F56C6C;">
              <el-icon :size="32"><Connection /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-value">{{ isConnected ? '正常' : '异常' }}</div>
              <div class="stat-label">连接状态</div>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 快捷操作 -->
    <el-row :gutter="20" class="quick-actions">
      <el-col :span="12">
        <el-card>
          <template #header>
            <div class="card-header">
              <span>快捷发送</span>
            </div>
          </template>
          
          <div class="quick-buttons">
            <el-button type="primary" @click="goToPage('/send-message?type=text')">
              <el-icon><EditPen /></el-icon>
              文本消息
            </el-button>
            <el-button type="success" @click="goToPage('/send-message?type=markdown')">
              <el-icon><Markdown /></el-icon>
              Markdown
            </el-button>
            <el-button type="warning" @click="goToPage('/send-message?type=news')">
              <el-icon><Picture /></el-icon>
              图文消息
            </el-button>
            <el-button type="info" @click="goToPage('/send-message?type=card')">
              <el-icon><Grid /></el-icon>
              卡片消息
            </el-button>
          </div>
        </el-card>
      </el-col>

      <el-col :span="12">
        <el-card>
          <template #header>
            <div class="card-header">
              <span>机器人信息</span>
            </div>
          </template>
          
          <el-descriptions :column="1" size="small">
            <el-descriptions-item label="Webhook Key">
              <el-tag size="small">{{ botInfo?.webhook_key || '未配置' }}</el-tag>
            </el-descriptions-item>
            <el-descriptions-item label="状态">
              <el-tag :type="botInfo?.status === 'active' ? 'success' : 'warning'" size="small">
                {{ botInfo?.status || '未知' }}
              </el-tag>
            </el-descriptions-item>
            <el-descriptions-item label="发送地址">
              <el-text type="info" size="small" truncated>
                {{ botInfo?.send_url || '-' }}
              </el-text>
            </el-descriptions-item>
          </el-descriptions>
        </el-card>
      </el-col>
    </el-row>

    <!-- 最近记录 -->
    <el-card class="recent-history">
      <template #header>
        <div class="card-header">
          <span>最近发送记录</span>
          <el-button type="primary" text @click="goToPage('/history')">
            查看更多
            <el-icon><ArrowRight /></el-icon>
          </el-button>
        </div>
      </template>
      
      <el-table :data="recentRecords" style="width: 100%" :height="300">
        <el-table-column prop="type" label="类型" width="100">
          <template #default="{ row }">
            <el-tag :type="getMessageTypeTag(row.type)" size="small">
              {{ getMessageTypeLabel(row.type) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="content" label="内容" min-width="200" show-overflow-tooltip />
        <el-table-column prop="status" label="状态" width="80">
          <template #default="{ row }">
            <el-tag :type="row.success ? 'success' : 'danger'" size="small">
              {{ row.success ? '成功' : '失败' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="timestamp" label="时间" width="180">
          <template #default="{ row }">
            {{ formatTime(row.timestamp) }}
          </template>
        </el-table-column>
      </el-table>
    </el-card>
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAppStore } from '@/stores/app'
import { messageApi } from '@/utils/api'
import dayjs from 'dayjs'

const router = useRouter()
const appStore = useAppStore()

const botInfo = ref(null)

const isConnected = computed(() => appStore.isConnected)
const recentRecords = computed(() => appStore.sendHistory.slice(0, 10))
const todayCount = computed(() => {
  const today = dayjs().format('YYYY-MM-DD')
  return appStore.sendHistory.filter(record => 
    dayjs(record.timestamp).format('YYYY-MM-DD') === today
  ).length
})
const successCount = computed(() => {
  return appStore.sendHistory.filter(record => record.success).length
})
const totalHistory = computed(() => appStore.sendHistory.length)

// 获取机器人信息
const fetchBotInfo = async () => {
  try {
    const res = await messageApi.getBotInfo()
    if (res.success) {
      botInfo.value = res.data
      appStore.botInfo = res.data
    }
  } catch (error) {
    console.error('获取机器人信息失败:', error)
  }
}

// 跳转到指定页面
const goToPage = (path) => {
  router.push(path)
}

// 消息类型标签
const getMessageTypeLabel = (type) => {
  const labels = {
    text: '文本',
    markdown: 'Markdown',
    image: '图片',
    news: '图文',
    template_card: '卡片',
    file: '文件'
  }
  return labels[type] || type
}

const getMessageTypeTag = (type) => {
  const tags = {
    text: '',
    markdown: 'success',
    image: 'warning',
    news: 'primary',
    template_card: 'info',
    file: 'danger'
  }
  return tags[type] || ''
}

// 格式化时间
const formatTime = (timestamp) => {
  return dayjs(timestamp).format('YYYY-MM-DD HH:mm:ss')
}

onMounted(() => {
  fetchBotInfo()
})
</script>

<style scoped>
.dashboard {
  padding: 0;
}

.stats-row {
  margin-bottom: 20px;
}

.stat-card {
  cursor: pointer;
  transition: transform 0.2s;
}

.stat-card:hover {
  transform: translateY(-2px);
}

.stat-content {
  display: flex;
  align-items: center;
  gap: 15px;
}

.stat-icon {
  width: 60px;
  height: 60px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #fff;
}

.stat-info {
  flex: 1;
}

.stat-value {
  font-size: 24px;
  font-weight: bold;
  color: #303133;
  margin-bottom: 5px;
}

.stat-label {
  font-size: 14px;
  color: #909399;
}

.quick-actions {
  margin-bottom: 20px;
}

.quick-buttons {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
}

.quick-buttons .el-button {
  flex: 1;
  min-width: 120px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.recent-history {
  margin-bottom: 20px;
}
</style>
