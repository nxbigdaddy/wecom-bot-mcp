<template>
  <div class="scheduler">
    <el-card>
      <template #header>
        <div class="header-actions">
          <span>定时任务管理</span>
          <el-button type="primary" @click="showAddDialog">
            <el-icon><Plus /></el-icon>
            创建任务
          </el-button>
        </div>
      </template>

      <!-- 搜索栏 -->
      <div class="search-bar">
        <el-input
          v-model="searchText"
          placeholder="搜索任务名称、描述..."
          style="width: 300px"
          clearable
          @input="handleSearch"
        >
          <template #prefix>
            <el-icon><Search /></el-icon>
          </template>
        </el-input>

        <el-select v-model="filterStatus" placeholder="任务状态" clearable style="width: 150px">
          <el-option label="启用" :value="true" />
          <el-option label="禁用" :value="false" />
        </el-select>

        <el-select v-model="filterType" placeholder="任务类型" clearable style="width: 150px">
          <el-option label="文本消息" value="text" />
          <el-option label="Markdown" value="markdown" />
          <el-option label="图片" value="image" />
          <el-option label="图文" value="news" />
          <el-option label="卡片" value="card" />
        </el-select>
      </div>

      <!-- 任务表格 -->
      <el-table :data="filteredTasks" style="width: 100%" stripe border>
        <el-table-column prop="id" label="ID" width="80" />
        
        <el-table-column prop="name" label="任务名称" min-width="150" />
        
        <el-table-column prop="description" label="描述" min-width="200" show-overflow-tooltip />
        
        <el-table-column prop="type" label="消息类型" width="100">
          <template #default="{ row }">
            <el-tag :type="getMessageTypeTag(row.type)" size="small">
              {{ getMessageTypeLabel(row.type) }}
            </el-tag>
          </template>
        </el-table-column>
        
        <el-table-column prop="schedule" label="执行计划" width="180">
          <template #default="{ row }">
            <div class="schedule-info">
              <el-tag size="small" :type="getScheduleTypeTag(row.scheduleType)">
                {{ getScheduleTypeLabel(row.scheduleType) }}
              </el-tag>
              <span class="schedule-text">{{ row.schedule }}</span>
            </div>
          </template>
        </el-table-column>
        
        <el-table-column prop="status" label="状态" width="80">
          <template #default="{ row }">
            <el-tag :type="row.status ? 'success' : 'info'" size="small">
              {{ row.status ? '启用' : '禁用' }}
            </el-tag>
          </template>
        </el-table-column>
        
        <el-table-column prop="last_run" label="上次执行" width="180">
          <template #default="{ row }">
            {{ row.last_run || '未执行' }}
          </template>
        </el-table-column>
        
        <el-table-column prop="next_run" label="下次执行" width="180">
          <template #default="{ row }">
            <el-tag v-if="row.next_run" size="small" type="warning">
              {{ row.next_run }}
            </el-tag>
            <span v-else>-</span>
          </template>
        </el-table-column>
        
        <el-table-column label="操作" width="280" fixed="right">
          <template #default="{ row }">
            <el-button
              type="primary"
              text
              size="small"
              @click="showEditDialog(row)"
            >
              编辑
            </el-button>
            <el-button
              :type="row.status ? 'warning' : 'success'"
              text
              size="small"
              @click="toggleTaskStatus(row)"
            >
              {{ row.status ? '禁用' : '启用' }}
            </el-button>
            <el-button
              type="info"
              text
              size="small"
              @click="runNow(row)"
            >
              立即执行
            </el-button>
            <el-button
              type="danger"
              text
              size="small"
              @click="deleteTask(row)"
            >
              删除
            </el-button>
          </template>
        </el-table-column>
      </el-table>

      <!-- 分页 -->
      <div class="pagination-bar">
        <el-pagination
          v-model:current-page="currentPage"
          v-model:page-size="pageSize"
          :total="filteredTasks.length"
          :page-sizes="[10, 20, 50, 100]"
          layout="total, sizes, prev, pager, next, jumper"
        />
      </div>
    </el-card>

    <!-- 添加/编辑任务对话框 -->
    <el-dialog
      v-model="dialogVisible"
      :title="isEdit ? '编辑任务' : '创建定时任务'"
      width="800px"
    >
      <el-form :model="taskForm" label-width="120px" :rules="rules" ref="taskFormRef">
        <el-row :gutter="20">
          <!-- 基本信息 -->
          <el-col :span="24">
            <h4 class="form-section-title">基本信息</h4>
          </el-col>
          
          <el-col :span="12">
            <el-form-item label="任务名称" prop="name">
              <el-input v-model="taskForm.name" placeholder="如：每日早报" />
            </el-form-item>
          </el-col>
          
          <el-col :span="12">
            <el-form-item label="任务描述">
              <el-input v-model="taskForm.description" placeholder="任务描述（可选）" />
            </el-form-item>
          </el-col>
          
          <el-col :span="12">
            <el-form-item label="消息类型" prop="type">
              <el-select v-model="taskForm.type" placeholder="选择消息类型" style="width: 100%" @change="onMessageTypeChange">
                <el-option label="文本消息" value="text" />
                <el-option label="Markdown 消息" value="markdown" />
                <el-option label="图片消息" value="image" />
                <el-option label="图文消息" value="news" />
                <el-option label="卡片消息" value="card" />
              </el-select>
            </el-form-item>
          </el-col>
          
          <el-col :span="12">
            <el-form-item label="任务状态">
              <el-switch v-model="taskForm.status" active-text="启用" inactive-text="禁用" />
            </el-form-item>
          </el-col>
        </el-row>

        <!-- 执行计划 -->
        <el-row :gutter="20">
          <el-col :span="24">
            <h4 class="form-section-title">执行计划</h4>
          </el-col>
          
          <el-col :span="12">
            <el-form-item label="执行类型" prop="scheduleType">
              <el-select v-model="taskForm.scheduleType" placeholder="选择执行类型" style="width: 100%" @change="onScheduleTypeChange">
                <el-option label="一次性执行" value="once" />
                <el-option label="每分钟" value="minute" />
                <el-option label="每小时" value="hour" />
                <el-option label="每天" value="day" />
                <el-option label="每周" value="week" />
                <el-option label="每月" value="month" />
                <el-option label="自定义 Cron" value="cron" />
              </el-select>
            </el-form-item>
          </el-col>
          
          <el-col :span="12" v-if="taskForm.scheduleType === 'once'">
            <el-form-item label="执行时间" prop="schedule">
              <el-date-picker
                v-model="taskForm.schedule"
                type="datetime"
                placeholder="选择执行时间"
                format="YYYY-MM-DD HH:mm:ss"
                value-format="YYYY-MM-DD HH:mm:ss"
                style="width: 100%"
              />
            </el-form-item>
          </el-col>
          
          <el-col :span="12" v-if="['minute', 'hour', 'day', 'week', 'month'].includes(taskForm.scheduleType)">
            <el-form-item label="执行时间" prop="schedule">
              <el-time-picker
                v-model="taskForm.schedule"
                format="HH:mm"
                value-format="HH:mm"
                placeholder="选择时间"
                style="width: 100%"
              />
            </el-form-item>
          </el-col>
          
          <el-col :span="12" v-if="taskForm.scheduleType === 'week'">
            <el-form-item label="执行星期">
              <el-select v-model="taskForm.weekday" placeholder="选择星期" style="width: 100%">
                <el-option label="星期一" :value="1" />
                <el-option label="星期二" :value="2" />
                <el-option label="星期三" :value="3" />
                <el-option label="星期四" :value="4" />
                <el-option label="星期五" :value="5" />
                <el-option label="星期六" :value="6" />
                <el-option label="星期日" :value="0" />
              </el-select>
            </el-form-item>
          </el-col>
          
          <el-col :span="12" v-if="taskForm.scheduleType === 'month'">
            <el-form-item label="执行日期">
              <el-input-number v-model="taskForm.day" :min="1" :max="31" :step="1" style="width: 100%" />
            </el-form-item>
          </el-col>
          
          <el-col :span="24" v-if="taskForm.scheduleType === 'cron'">
            <el-form-item label="Cron 表达式" prop="schedule">
              <el-input v-model="taskForm.schedule" placeholder="*/5 * * * * (每 5 分钟)" />
              <div class="form-tip">
                格式：分 时 日 月 星期，例如：0 9 * * * (每天 9 点)
              </div>
            </el-form-item>
          </el-col>
        </el-row>

        <!-- 消息内容 -->
        <el-row :gutter="20">
          <el-col :span="24">
            <h4 class="form-section-title">消息内容</h4>
          </el-col>
          
          <el-col :span="24" v-if="taskForm.type === 'text'">
            <el-form-item label="消息内容" prop="content">
              <el-input
                v-model="taskForm.content"
                type="textarea"
                :rows="4"
                placeholder="请输入文本消息内容"
                maxlength="4096"
                show-word-limit
              />
            </el-form-item>
          </el-col>
          
          <el-col :span="24" v-if="taskForm.type === 'markdown'">
            <el-form-item label="Markdown 内容" prop="content">
              <el-input
                v-model="taskForm.content"
                type="textarea"
                :rows="6"
                placeholder="# 标题&#10;&#10;这是 **Markdown** 内容..."
                maxlength="4096"
                show-word-limit
              />
            </el-form-item>
          </el-col>
          
          <el-col :span="24" v-if="taskForm.type === 'news'">
            <el-form-item label="图文列表">
              <div v-for="(article, index) in taskForm.articles" :key="index" class="article-item">
                <el-card shadow="hover" class="article-card">
                  <div class="article-header">
                    <span class="article-title">文章 {{ index + 1 }}</span>
                    <el-button
                      v-if="taskForm.articles.length > 1"
                      type="danger"
                      text
                      size="small"
                      @click="removeArticle(index)"
                    >
                      <el-icon><Delete /></el-icon>
                    </el-button>
                  </div>
                  <el-row :gutter="15">
                    <el-col :span="12">
                      <el-form-item label="标题" required>
                        <el-input v-model="article.title" placeholder="文章标题" maxlength="128" />
                      </el-form-item>
                    </el-col>
                    <el-col :span="12">
                      <el-form-item label="链接" required>
                        <el-input v-model="article.url" placeholder="https://example.com" />
                      </el-form-item>
                    </el-col>
                  </el-row>
                  <el-form-item label="描述">
                    <el-input v-model="article.description" type="textarea" :rows="2" placeholder="文章描述" maxlength="512" />
                  </el-form-item>
                  <el-form-item label="图片链接">
                    <el-input v-model="article.picurl" placeholder="https://example.com/image.jpg" />
                  </el-form-item>
                </el-card>
              </div>
              <el-button
                v-if="taskForm.articles.length < 10"
                type="primary"
                plain
                @click="addArticle"
                style="width: 100%"
              >
                <el-icon><Plus /></el-icon>
                添加文章
              </el-button>
            </el-form-item>
          </el-col>
          
          <el-col :span="24" v-if="taskForm.type === 'card'">
            <el-form-item label="卡片类型">
              <el-select v-model="taskForm.cardType" placeholder="选择卡片类型" style="width: 100%">
                <el-option label="文本通知型" value="text_notice" />
                <el-option label="图文展示型" value="news_notice" />
              </el-select>
            </el-form-item>
            <el-form-item label="主标题">
              <el-input v-model="taskForm.mainTitle" placeholder="卡片主标题" maxlength="128" />
            </el-form-item>
            <el-form-item label="主描述">
              <el-input v-model="taskForm.mainDesc" type="textarea" :rows="3" placeholder="卡片主描述" maxlength="512" />
            </el-form-item>
          </el-col>
        </el-row>
      </el-form>
      
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="saveTask" :loading="saving">保存</el-button>
      </template>
    </el-dialog>

    <!-- 执行历史对话框 -->
    <el-dialog v-model="historyVisible" title="执行历史" width="800px">
      <el-table :data="executionHistory" style="width: 100%" stripe border>
        <el-table-column prop="time" label="执行时间" width="180" />
        <el-table-column prop="status" label="状态" width="80">
          <template #default="{ row }">
            <el-tag :type="row.status ? 'success' : 'danger'" size="small">
              {{ row.status ? '成功' : '失败' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="message" label="执行结果" min-width="300" show-overflow-tooltip />
      </el-table>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'

// 模拟任务数据
const tasks = ref([
  {
    id: 1,
    name: '每日早报',
    description: '每天早上 9 点发送早报',
    type: 'text',
    scheduleType: 'day',
    schedule: '09:00',
    status: true,
    content: '大家早上好！这是今天的早报内容...',
    last_run: '2026-03-16 09:00:00',
    next_run: '2026-03-17 09:00:00',
    weekday: null,
    day: null,
    articles: [],
    cardType: 'text_notice',
    mainTitle: '',
    mainDesc: ''
  },
  {
    id: 2,
    name: '每周总结',
    description: '每周五下午 5 点发送周报',
    type: 'markdown',
    scheduleType: 'week',
    schedule: '17:00',
    status: true,
    content: '# 本周工作总结\n\n## 完成工作\n- 项目 A\n- 项目 B',
    last_run: '2026-03-14 17:00:00',
    next_run: '2026-03-21 17:00:00',
    weekday: 5,
    day: null,
    articles: [],
    cardType: 'text_notice',
    mainTitle: '',
    mainDesc: ''
  },
  {
    id: 3,
    name: '每月报表',
    description: '每月 1 号发送月度报表',
    type: 'news',
    scheduleType: 'month',
    schedule: '10:00',
    status: false,
    content: '',
    last_run: '2026-03-01 10:00:00',
    next_run: null,
    weekday: null,
    day: 1,
    articles: [
      { title: '月度销售报告', description: '销售数据分析', url: 'https://example.com/report', picurl: '' }
    ],
    cardType: 'text_notice',
    mainTitle: '',
    mainDesc: ''
  }
])

const searchText = ref('')
const filterStatus = ref('')
const filterType = ref('')
const currentPage = ref(1)
const pageSize = ref(10)
const dialogVisible = ref(false)
const historyVisible = ref(false)
const isEdit = ref(false)
const saving = ref(false)

const taskForm = ref({
  id: null,
  name: '',
  description: '',
  type: 'text',
  scheduleType: 'day',
  schedule: '09:00',
  status: true,
  content: '',
  weekday: null,
  day: null,
  articles: [{ title: '', description: '', url: '', picurl: '' }],
  cardType: 'text_notice',
  mainTitle: '',
  mainDesc: ''
})

const rules = {
  name: [{ required: true, message: '请输入任务名称', trigger: 'blur' }],
  type: [{ required: true, message: '请选择消息类型', trigger: 'change' }],
  scheduleType: [{ required: true, message: '请选择执行类型', trigger: 'change' }],
  schedule: [{ required: true, message: '请设置执行时间', trigger: 'change' }],
  content: [{ required: true, message: '请输入消息内容', trigger: 'blur' }]
}

const executionHistory = ref([])

// 过滤后的任务列表
const filteredTasks = computed(() => {
  let result = [...tasks.value]

  // 搜索过滤
  if (searchText.value) {
    const text = searchText.value.toLowerCase()
    result = result.filter(task =>
      task.name.toLowerCase().includes(text) ||
      task.description.toLowerCase().includes(text)
    )
  }

  // 状态过滤
  if (filterStatus.value !== '') {
    result = result.filter(task => task.status === filterStatus.value)
  }

  // 类型过滤
  if (filterType.value) {
    result = result.filter(task => task.type === filterType.value)
  }

  return result
})

// 消息类型标签
const getMessageTypeLabel = (type) => {
  const labels = {
    text: '文本',
    markdown: 'Markdown',
    image: '图片',
    news: '图文',
    card: '卡片'
  }
  return labels[type] || type
}

const getMessageTypeTag = (type) => {
  const tags = {
    text: '',
    markdown: 'success',
    image: 'warning',
    news: 'primary',
    card: 'info'
  }
  return tags[type] || ''
}

// 执行计划类型
const getScheduleTypeLabel = (type) => {
  const labels = {
    once: '一次性',
    minute: '每分钟',
    hour: '每小时',
    day: '每天',
    week: '每周',
    month: '每月',
    cron: 'Cron'
  }
  return labels[type] || type
}

const getScheduleTypeTag = (type) => {
  const tags = {
    once: 'info',
    minute: 'success',
    hour: '',
    day: 'primary',
    week: 'warning',
    month: 'danger',
    cron: 'info'
  }
  return tags[type] || ''
}

// 搜索处理
const handleSearch = () => {
  currentPage.value = 1
}

// 消息类型变化
const onMessageTypeChange = (type) => {
  if (type === 'news' && taskForm.value.articles.length === 0) {
    taskForm.value.articles = [{ title: '', description: '', url: '', picurl: '' }]
  }
}

// 执行类型变化
const onScheduleTypeChange = (type) => {
  if (type === 'once') {
    taskForm.value.schedule = new Date().toISOString().slice(0, 19).replace('T', ' ')
  } else if (['minute', 'hour', 'day', 'week', 'month'].includes(type)) {
    taskForm.value.schedule = '09:00'
  } else if (type === 'cron') {
    taskForm.value.schedule = '0 9 * * *'
  }
}

// 添加文章
const addArticle = () => {
  taskForm.value.articles.push({ title: '', description: '', url: '', picurl: '' })
}

// 删除文章
const removeArticle = (index) => {
  taskForm.value.articles.splice(index, 1)
}

// 显示添加对话框
const showAddDialog = () => {
  isEdit.value = false
  taskForm.value = {
    id: null,
    name: '',
    description: '',
    type: 'text',
    scheduleType: 'day',
    schedule: '09:00',
    status: true,
    content: '',
    weekday: null,
    day: null,
    articles: [{ title: '', description: '', url: '', picurl: '' }],
    cardType: 'text_notice',
    mainTitle: '',
    mainDesc: ''
  }
  dialogVisible.value = true
}

// 显示编辑对话框
const showEditDialog = (task) => {
  isEdit.value = true
  taskForm.value = { ...task }
  dialogVisible.value = true
}

// 保存任务
const saveTask = async () => {
  saving.value = true
  
  setTimeout(() => {
    if (isEdit.value) {
      const index = tasks.value.findIndex(t => t.id === taskForm.value.id)
      if (index !== -1) {
        tasks.value[index] = { ...tasks.value[index], ...taskForm.value }
        ElMessage.success('任务已更新')
      }
    } else {
      const newTask = {
        ...taskForm.value,
        id: tasks.value.length + 1,
        last_run: null,
        next_run: calculateNextRun(taskForm.value)
      }
      tasks.value.unshift(newTask)
      ElMessage.success('任务已创建')
    }
    
    dialogVisible.value = false
    saving.value = false
  }, 500)
}

// 计算下次执行时间
const calculateNextRun = (task) => {
  if (task.scheduleType === 'once') {
    return task.schedule
  }
  // 简化计算，实际应该根据类型计算
  return '2026-03-17 09:00:00'
}

// 切换任务状态
const toggleTaskStatus = (task) => {
  ElMessageBox.confirm(
    `确定要${task.status ? '禁用' : '启用'}任务 "${task.name}" 吗？`,
    '提示',
    {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    }
  ).then(() => {
    task.status = !task.status
    ElMessage.success('操作成功')
  }).catch(() => {})
}

// 立即执行
const runNow = (task) => {
  ElMessageBox.confirm(
    `确定要立即执行任务 "${task.name}" 吗？`,
    '提示',
    {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'info'
    }
  ).then(() => {
    ElMessage.info('任务执行中...')
    setTimeout(() => {
      task.last_run = new Date().toLocaleString('zh-CN')
      ElMessage.success('任务执行成功')
    }, 1000)
  }).catch(() => {})
}

// 删除任务
const deleteTask = (task) => {
  ElMessageBox.confirm(
    `确定要删除任务 "${task.name}" 吗？此操作不可恢复。`,
    '警告',
    {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    }
  ).then(() => {
    const index = tasks.value.findIndex(t => t.id === task.id)
    if (index !== -1) {
      tasks.value.splice(index, 1)
      ElMessage.success('删除成功')
    }
  }).catch(() => {})
}

// 查看执行历史
const viewHistory = (task) => {
  executionHistory.value = [
    { time: '2026-03-16 09:00:00', status: true, message: '发送成功' },
    { time: '2026-03-15 09:00:00', status: true, message: '发送成功' },
    { time: '2026-03-14 09:00:00', status: false, message: '发送失败：网络错误' }
  ]
  historyVisible.value = true
}
</script>

<style scoped>
.scheduler {
  padding: 0;
}

.header-actions {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.search-bar {
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

.form-section-title {
  font-size: 16px;
  font-weight: bold;
  color: #303133;
  margin: 20px 0 15px 0;
  padding-bottom: 10px;
  border-bottom: 1px solid #e6e6e6;
}

.form-tip {
  font-size: 12px;
  color: #909399;
  margin-top: 5px;
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

.schedule-info {
  display: flex;
  flex-direction: column;
  gap: 5px;
}

.schedule-text {
  font-size: 12px;
  color: #606266;
}
</style>
