<template>
  <div class="history">
    <el-card>
      <template #header>
        <div class="header-actions">
          <span>发送历史记录</span>
          <div>
            <el-button type="danger" plain @click="clearHistory">
              <el-icon><Delete /></el-icon>
              清空记录
            </el-button>
            <el-button type="primary" @click="exportHistory">
              <el-icon><Download /></el-icon>
              导出记录
            </el-button>
          </div>
        </div>
      </template>

      <!-- 筛选器 -->
      <div class="filter-bar">
        <el-input
          v-model="searchText"
          placeholder="搜索内容..."
          style="width: 300px"
          clearable
          @input="handleSearch"
        >
          <template #prefix>
            <el-icon><Search /></el-icon>
          </template>
        </el-input>

        <el-select v-model="filterType" placeholder="消息类型" clearable style="width: 150px">
          <el-option label="文本" value="text" />
          <el-option label="Markdown" value="markdown" />
          <el-option label="图片" value="image" />
          <el-option label="图文" value="news" />
          <el-option label="卡片" value="template_card" />
        </el-select>

        <el-select v-model="filterStatus" placeholder="状态" clearable style="width: 120px">
          <el-option label="成功" :value="true" />
          <el-option label="失败" :value="false" />
        </el-select>

        <el-date-picker
          v-model="dateRange"
          type="daterange"
          range-separator="至"
          start-placeholder="开始日期"
          end-placeholder="结束日期"
          style="width: 240px"
        />
      </div>

      <!-- 历史记录表格 -->
      <el-table
        :data="filteredHistory"
        style="width: 100%"
        :height="500"
        stripe
        border
      >
        <el-table-column prop="timestamp" label="发送时间" width="180" sortable>
          <template #default="{ row }">
            {{ formatTime(row.timestamp) }}
          </template>
        </el-table-column>

        <el-table-column prop="type" label="类型" width="100">
          <template #default="{ row }">
            <el-tag :type="getMessageTypeTag(row.type)" size="small">
              {{ getMessageTypeLabel(row.type) }}
            </el-tag>
          </template>
        </el-table-column>

        <el-table-column prop="content" label="内容" min-width="300" show-overflow-tooltip />

        <el-table-column prop="status" label="状态" width="80">
          <template #default="{ row }">
            <el-tag :type="row.success ? 'success' : 'danger'" size="small">
              {{ row.success ? '成功' : '失败' }}
            </el-tag>
          </template>
        </el-table-column>

        <el-table-column prop="message" label="响应信息" min-width="200" show-overflow-tooltip />

        <el-table-column label="操作" width="100" fixed="right">
          <template #default="{ row }">
            <el-button
              type="primary"
              text
              size="small"
              @click="resendMessage(row)"
            >
              重发
            </el-button>
          </template>
        </el-table-column>
      </el-table>

      <!-- 分页 -->
      <div class="pagination-bar">
        <el-pagination
          v-model:current-page="currentPage"
          v-model:page-size="pageSize"
          :total="filteredHistory.length"
          :page-sizes="[10, 20, 50, 100]"
          layout="total, sizes, prev, pager, next, jumper"
        />
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { useAppStore } from '@/stores/app'
import dayjs from 'dayjs'

const appStore = useAppStore()

const searchText = ref('')
const filterType = ref('')
const filterStatus = ref('')
const dateRange = ref([])
const currentPage = ref(1)
const pageSize = ref(20)

// 过滤后的历史记录
const filteredHistory = computed(() => {
  let result = [...appStore.sendHistory]

  // 搜索过滤
  if (searchText.value) {
    result = result.filter(item =>
      item.content.toLowerCase().includes(searchText.value.toLowerCase())
    )
  }

  // 类型过滤
  if (filterType.value) {
    result = result.filter(item => item.type === filterType.value)
  }

  // 状态过滤
  if (filterStatus.value !== '') {
    result = result.filter(item => item.success === filterStatus.value)
  }

  // 日期过滤
  if (dateRange.value && dateRange.value.length === 2) {
    const start = dayjs(dateRange.value[0]).startOf('day')
    const end = dayjs(dateRange.value[1]).endOf('day')
    result = result.filter(item => {
      const itemDate = dayjs(item.timestamp)
      return itemDate.isAfter(start) && itemDate.isBefore(end)
    })
  }

  return result
  // 分页逻辑可以在这里添加
})

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

// 搜索处理
const handleSearch = () => {
  currentPage.value = 1
}

// 清空历史
const clearHistory = () => {
  ElMessageBox.confirm('确定要清空所有发送记录吗？此操作不可恢复。', '提示', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'warning'
  }).then(() => {
    appStore.clearHistory()
    ElMessage.success('已清空所有记录')
  }).catch(() => {})
}

// 导出历史
const exportHistory = () => {
  const data = appStore.sendHistory.map(item => ({
    时间： formatTime(item.timestamp),
    类型：getMessageTypeLabel(item.type),
    内容：item.content,
    状态：item.success ? '成功' : '失败',
    响应：item.message
  }))

  const csvContent = [
    ['时间', '类型', '内容', '状态', '响应'].join(','),
    ...data.map(row =>
      Object.values(row).map(val => `"${val}"`).join(',')
    )
  ].join('\n')

  const blob = new Blob(['\ufeff' + csvContent], { type: 'text/csv;charset=utf-8;' })
  const link = document.createElement('a')
  link.href = URL.createObjectURL(blob)
  link.download = `发送记录_${dayjs().format('YYYYMMDD_HHmmss')}.csv`
  link.click()

  ElMessage.success('导出成功')
}

// 重发消息
const resendMessage = (record) => {
  // 这里可以实现重发逻辑
  ElMessage.info('重发功能开发中...')
}
</script>

<style scoped>
.history {
  padding: 0;
}

.header-actions {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.filter-bar {
  display: flex;
  gap: 15px;
  margin-bottom: 20px;
  flex-wrap: wrap;
}

.pagination-bar {
  margin-top: 20px;
  display: flex;
  justify-content: flex-end;
}
</style>
