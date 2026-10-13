<template>
  <div class="settings">
    <el-row :gutter="20">
      <!-- 系统配置 -->
      <el-col :span="12">
        <el-card>
          <template #header>
            <div class="card-header">
              <span>系统配置</span>
            </div>
          </template>

          <el-form :model="configForm" label-width="120px" size="large">
            <el-form-item label="API 地址">
              <el-input v-model="configForm.apiBaseUrl" placeholder="http://localhost:8000" />
            </el-form-item>

            <el-form-item label="WebSocket 地址">
              <el-input v-model="configForm.wsUrl" placeholder="ws://localhost:8000/ws" />
            </el-form-item>

            <el-form-item label="日志级别">
              <el-select v-model="configForm.logLevel" placeholder="选择日志级别" style="width: 100%">
                <el-option label="DEBUG" value="DEBUG" />
                <el-option label="INFO" value="INFO" />
                <el-option label="WARNING" value="WARNING" />
                <el-option label="ERROR" value="ERROR" />
              </el-select>
            </el-form-item>

            <el-form-item>
              <el-button type="primary" @click="saveConfig">保存配置</el-button>
              <el-button @click="resetConfig">重置</el-button>
            </el-form-item>
          </el-form>
        </el-card>
      </el-col>

      <!-- 机器人配置 -->
      <el-col :span="12">
        <el-card>
          <template #header>
            <div class="card-header">
              <span>机器人信息</span>
              <el-button type="primary" text size="small" @click="showWebhookDialog">
                <el-icon><Edit /></el-icon>
                配置
              </el-button>
            </div>
          </template>

          <el-descriptions :column="1" border>
            <el-descriptions-item label="Webhook Key">
              <el-tag>{{ botInfo?.webhook_key || '未配置' }}</el-tag>
            </el-descriptions-item>
            <el-descriptions-item label="状态">
              <el-tag :type="botInfo?.status === 'active' ? 'success' : 'warning'">
                {{ botInfo?.status || '未知' }}
              </el-tag>
            </el-descriptions-item>
            <el-descriptions-item label="发送地址">
              <el-text type="info" size="small" truncated>
                {{ botInfo?.send_url || '-' }}
              </el-text>
            </el-descriptions-item>
            <el-descriptions-item label="上传地址">
              <el-text type="info" size="small" truncated>
                {{ botInfo?.upload_url || '-' }}
              </el-text>
            </el-descriptions-item>
          </el-descriptions>

          <el-alert
            title="如何获取 Webhook Key？"
            type="info"
            :closable="false"
            style="margin-top: 15px;"
          >
            <template #default>
              <div>
                1. 打开企业微信 → 进入群聊 → 点击右上角「...」<br>
                2. 选择「群机器人」→ 「添加机器人」<br>
                3. 复制 Webhook 地址中的 key 参数<br>
                <el-link type="primary" href="#" @click.prevent="showWebhookDialog" style="margin-top: 5px;">
                  点击这里配置 Webhook Key
                </el-link>
              </div>
            </template>
          </el-alert>

          <el-button type="primary" plain style="margin-top: 15px" @click="refreshBotInfo">
            <el-icon><Refresh /></el-icon>
            刷新信息
          </el-button>
        </el-card>
      </el-col>
    </el-row>

    <!-- 系统状态 -->
    <el-card style="margin-top: 20px">
      <template #header>
        <div class="card-header">
          <span>系统状态</span>
        </div>
      </template>

      <el-row :gutter="20">
        <el-col :span="8">
          <div class="status-item">
            <div class="status-label">服务状态</div>
            <div class="status-value">
              <el-tag :type="healthStatus ? 'success' : 'danger'">
                {{ healthStatus ? '正常运行' : '异常' }}
              </el-tag>
            </div>
          </div>
        </el-col>

        <el-col :span="8">
          <div class="status-item">
            <div class="status-label">WebSocket 连接</div>
            <div class="status-value">
              <el-tag :type="isConnected ? 'success' : 'danger'">
                {{ isConnected ? '已连接' : '未连接' }}
              </el-tag>
            </div>
          </div>
        </el-col>

        <el-col :span="8">
          <div class="status-item">
            <div class="status-label">发送记录数</div>
            <div class="status-value">{{ sendHistoryCount }}</div>
          </div>
        </el-col>
      </el-row>

      <el-button type="primary" plain style="margin-top: 15px" @click="checkHealth">
        <el-icon><Refresh /></el-icon>
        刷新状态
      </el-button>
    </el-card>

    <!-- 关于 -->
    <el-card style="margin-top: 20px">
      <template #header>
        <div class="card-header">
          <span>关于</span>
        </div>
      </template>

      <div class="about-content">
        <p><strong>WeCom Bot Server</strong> - 企业微信机器人管理后台</p>
        <p>版本：v1.0.0</p>
        <p>技术栈：Vue 3 + Element Plus + FastAPI</p>
        <p>
          <el-link type="primary" href="https://github.com/yourusername/wecom-bot-server" target="_blank">
            GitHub 仓库
          </el-link>
        </p>
      </div>
    </el-card>

    <!-- Webhook 配置对话框 -->
    <el-dialog
      v-model="webhookDialogVisible"
      title="配置 Webhook Key"
      width="500px"
    >
      <el-form label-width="120px">
        <el-form-item label="Webhook Key">
          <el-input
            v-model="webhookKey"
            placeholder="请输入企业微信机器人 Webhook Key"
            type="password"
            show-password
          />
        </el-form-item>
      </el-form>

      <template #footer>
        <el-button @click="webhookDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="saveWebhookKey">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox, ElDialog } from 'element-plus'
import { useAppStore } from '@/stores/app'
import { messageApi, healthApi } from '@/utils/api'

const appStore = useAppStore()

const configForm = ref({
  apiBaseUrl: 'http://localhost:8000',
  wsUrl: 'ws://localhost:8000/ws',
  logLevel: 'INFO'
})

const botInfo = ref(null)
const healthStatus = ref(false)
const webhookDialogVisible = ref(false)
const webhookKey = ref('')

const isConnected = computed(() => appStore.isConnected)
const sendHistoryCount = computed(() => appStore.sendHistory.length)

// 显示 Webhook 配置对话框
const showWebhookDialog = () => {
  webhookKey.value = botInfo.value?.webhook_key || ''
  webhookDialogVisible.value = true
}

// 保存 Webhook Key
const saveWebhookKey = async () => {
  if (!webhookKey.value.trim()) {
    ElMessage.warning('请输入 Webhook Key')
    return
  }
  
  ElMessageBox.alert(
    '请在后端的 .env 文件中配置 Webhook Key，然后重启后端服务。<br><br>' +
    '1. 打开项目根目录的 .env 文件<br>' +
    '2. 修改 WECOM_BOT_WEBHOOK_KEY=your-key<br>' +
    '3. 重启后端服务<br>' +
    '4. 点击刷新按钮更新状态',
    '配置说明',
    {
      dangerouslyUseHTMLString: true,
      confirmButtonText: '知道了'
    }
  )
}

// 保存配置
const saveConfig = () => {
  localStorage.setItem('wecom_bot_config', JSON.stringify(configForm.value))
  ElMessage.success('配置已保存')
}

// 重置配置
const resetConfig = () => {
  configForm.value = {
    apiBaseUrl: 'http://localhost:8000',
    wsUrl: 'ws://localhost:8000/ws',
    logLevel: 'INFO'
  }
  ElMessage.info('配置已重置')
}

// 加载配置
const loadConfig = () => {
  const saved = localStorage.getItem('wecom_bot_config')
  if (saved) {
    configForm.value = JSON.parse(saved)
  }
}

// 刷新机器人信息
const refreshBotInfo = async () => {
  try {
    const res = await messageApi.getBotInfo()
    if (res.success) {
      botInfo.value = res.data
      appStore.botInfo = res.data
      ElMessage.success('刷新成功')
    }
  } catch (error) {
    ElMessage.error('获取机器人信息失败：' + error.message)
  }
}

// 检查健康状态
const checkHealth = async () => {
  try {
    const res = await healthApi.check()
    healthStatus.value = res.data?.status === 'healthy'
  } catch (error) {
    healthStatus.value = false
    ElMessage.error('健康检查失败：' + error.message)
  }
}

onMounted(() => {
  loadConfig()
  refreshBotInfo()
  checkHealth()
})
</script>

<style scoped>
.settings {
  padding: 0;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.status-item {
  text-align: center;
  padding: 20px;
  background-color: #f5f7fa;
  border-radius: 4px;
}

.status-label {
  font-size: 14px;
  color: #909399;
  margin-bottom: 10px;
}

.status-value {
  font-size: 18px;
  font-weight: bold;
}

.about-content {
  line-height: 2;
}
</style>
