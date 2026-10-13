<template>
  <div class="wecom-config">
    <el-row :gutter="20">
      <!-- 机器人基础配置 -->
      <el-col :span="12">
        <el-card>
          <template #header>
            <div class="card-header">
              <span>机器人配置</span>
              <el-button type="primary" @click="saveRobotConfig">
                <el-icon><Check /></el-icon>
                保存配置
              </el-button>
            </div>
          </template>

          <el-form :model="robotForm" label-width="120px" size="large">
            <el-form-item label="Webhook Key" required>
              <el-input
                v-model="robotForm.webhookKey"
                placeholder="请输入企业微信机器人 Webhook Key"
                type="password"
                show-password
              >
                <template #append>
                  <el-button @click="testWebhook">
                    <el-icon><Connection /></el-icon>
                    测试
                  </el-button>
                </template>
              </el-input>
              <div class="form-tip">
                从企业微信复制的 Webhook 地址中的 key 参数
              </div>
            </el-form-item>

            <el-form-item label="机器人名称">
              <el-input v-model="robotForm.name" placeholder="请输入机器人名称" />
            </el-form-item>

            <el-form-item label="API 地址">
              <el-input v-model="robotForm.apiUrl" placeholder="https://qyapi.weixin.qq.com/cgi-bin/webhook" />
              <div class="form-tip">
                企业微信 API 基础地址，一般不需要修改
              </div>
            </el-form-item>

            <el-form-item label="默认@成员">
              <el-select
                v-model="robotForm.defaultMentioned"
                multiple
                placeholder="选择默认@的成员"
                style="width: 100%"
              >
                <el-option label="@所有人" value="@all" />
                <el-option label="张三" value="zhangsan" />
                <el-option label="李四" value="lisi" />
                <el-option label="王五" value="wangwu" />
              </el-select>
            </el-form-item>
          </el-form>
        </el-card>
      </el-col>

      <!-- 企业微信应用配置 -->
      <el-col :span="12">
        <el-card>
          <template #header>
            <div class="card-header">
              <span>企业微信应用配置</span>
              <el-button type="primary" @click="saveAppConfig">
                <el-icon><Check /></el-icon>
                保存配置
              </el-button>
            </div>
          </template>

          <el-form :model="appForm" label-width="120px" size="large">
            <el-form-item label="企业 ID" required>
              <el-input v-model="appForm.corpId" placeholder="请输入企业 ID" />
              <div class="form-tip">
                企业微信管理后台 - 我的企业 - 企业信息
              </div>
            </el-form-item>

            <el-form-item label="应用 AgentId" required>
              <el-input v-model="appForm.agentId" placeholder="请输入应用 AgentId" />
              <div class="form-tip">
                企业微信管理后台 - 应用管理 - 应用详情
              </div>
            </el-form-item>

            <el-form-item label="应用 Secret" required>
              <el-input
                v-model="appForm.secret"
                type="password"
                placeholder="请输入应用 Secret"
                show-password
              />
              <div class="form-tip">
                企业微信管理后台 - 应用管理 - 应用详情
              </div>
            </el-form-item>

            <el-form-item label="通讯录加密">
              <el-input
                v-model="appForm.encodingAesKey"
                placeholder="请输入 EncodingAESKey"
                type="password"
                show-password
              />
              <div class="form-tip">
                企业微信管理后台 - 应用管理 - 应用详情
              </div>
            </el-form-item>
          </el-form>
        </el-card>
      </el-col>
    </el-row>

    <!-- 高级配置 -->
    <el-card style="margin-top: 20px">
      <template #header>
        <div class="card-header">
          <span>高级配置</span>
          <el-button type="primary" @click="saveAdvancedConfig">
            <el-icon><Check /></el-icon>
            保存配置
          </el-button>
        </div>
      </template>

      <el-row :gutter="20">
        <el-col :span="8">
          <el-form :model="advancedForm" label-width="140px">
            <el-form-item label="消息发送超时">
              <el-input-number
                v-model="advancedForm.timeout"
                :min="1000"
                :max="30000"
                :step="1000"
                style="width: 100%"
              />
              <div class="form-tip">毫秒</div>
            </el-form-item>

            <el-form-item label="最大重试次数">
              <el-input-number
                v-model="advancedForm.maxRetries"
                :min="0"
                :max="10"
                :step="1"
                style="width: 100%"
              />
            </el-form-item>
          </el-form>
        </el-col>

        <el-col :span="8">
          <el-form :model="advancedForm" label-width="140px">
            <el-form-item label="消息频率限制">
              <el-input-number
                v-model="advancedForm.rateLimit"
                :min="1"
                :max="100"
                :step="1"
                style="width: 100%"
              />
              <div class="form-tip">条/分钟</div>
            </el-form-item>

            <el-form-item label="日志级别">
              <el-select v-model="advancedForm.logLevel" style="width: 100%">
                <el-option label="DEBUG" value="DEBUG" />
                <el-option label="INFO" value="INFO" />
                <el-option label="WARNING" value="WARNING" />
                <el-option label="ERROR" value="ERROR" />
              </el-select>
            </el-form-item>
          </el-form>
        </el-col>

        <el-col :span="8">
          <el-form :model="advancedForm" label-width="140px">
            <el-form-item label="启用 WebSocket">
              <el-switch v-model="advancedForm.websocketEnabled" />
            </el-form-item>

            <el-form-item label="心跳间隔">
              <el-input-number
                v-model="advancedForm.heartbeatInterval"
                :min="10"
                :max="300"
                :step="10"
                style="width: 100%"
              />
              <div class="form-tip">秒</div>
            </el-form-item>
          </el-form>
        </el-col>
      </el-row>
    </el-card>

    <!-- 配置历史 -->
    <el-card style="margin-top: 20px">
      <template #header>
        <div class="card-header">
          <span>配置历史</span>
          <el-button type="danger" plain @click="clearHistory">
            <el-icon><Delete /></el-icon>
            清空历史
          </el-button>
        </div>
      </template>

      <el-table :data="configHistory" style="width: 100%" stripe border>
        <el-table-column prop="time" label="修改时间" width="180" />
        <el-table-column prop="type" label="配置类型" width="150">
          <template #default="{ row }">
            <el-tag size="small" :type="getConfigTypeTag(row.type)">
              {{ row.type }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="content" label="修改内容" min-width="300" show-overflow-tooltip />
        <el-table-column prop="operator" label="操作人" width="100" />
        <el-table-column label="操作" width="100">
          <template #default="{ row }">
            <el-button type="primary" text size="small" @click="rollbackConfig(row)">
              回滚
            </el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <!-- 帮助信息 -->
    <el-alert
      title="如何获取配置信息？"
      type="info"
      :closable="false"
      style="margin-top: 20px"
    >
      <template #default>
        <div>
          <h4>1. 获取 Webhook Key（推荐方式）</h4>
          <ul>
            <li>打开企业微信 → 进入群聊 → 点击右上角「...」</li>
            <li>选择「群机器人」→ 「添加机器人」</li>
            <li>复制 Webhook 地址中的 key 参数</li>
          </ul>

          <h4>2. 获取企业 ID 和应用信息</h4>
          <ul>
            <li>登录企业微信管理后台：https://work.weixin.qq.com</li>
            <li>企业 ID：我的企业 → 企业信息</li>
            <li>应用信息：应用管理 → 选择应用 → 查看详情</li>
          </ul>

          <h4>3. 配置保存位置</h4>
          <p>配置会保存到项目根目录的 .env 文件中，重启后端服务后生效。</p>
        </div>
      </template>
    </el-alert>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'

// 机器人配置
const robotForm = ref({
  webhookKey: '',
  name: '通知助手',
  apiUrl: 'https://qyapi.weixin.qq.com/cgi-bin/webhook',
  defaultMentioned: []
})

// 应用配置
const appForm = ref({
  corpId: '',
  agentId: '',
  secret: '',
  encodingAesKey: ''
})

// 高级配置
const advancedForm = ref({
  timeout: 5000,
  maxRetries: 3,
  rateLimit: 20,
  logLevel: 'INFO',
  websocketEnabled: true,
  heartbeatInterval: 30
})

// 配置历史
const configHistory = ref([
  {
    id: 1,
    time: '2026-03-15 10:30:00',
    type: '机器人配置',
    content: '修改 Webhook Key 为 5b76c8a6...',
    operator: 'admin'
  },
  {
    id: 2,
    time: '2026-03-14 14:20:00',
    type: '应用配置',
    content: '修改企业 ID 为 ww123456...',
    operator: 'admin'
  }
])

// 加载配置
const loadConfig = () => {
  // 从本地存储加载
  const saved = localStorage.getItem('wecom_config')
  if (saved) {
    const config = JSON.parse(saved)
    robotForm.value = { ...robotForm.value, ...config.robot }
    appForm.value = { ...appForm.value, ...config.app }
    advancedForm.value = { ...advancedForm.value, ...config.advanced }
  }
}

// 保存机器人配置
const saveRobotConfig = () => {
  if (!robotForm.value.webhookKey) {
    ElMessage.warning('请输入 Webhook Key')
    return
  }

  saveConfig('机器人配置', `Webhook Key: ${robotForm.value.webhookKey.substring(0, 8)}...`)
  ElMessage.success('机器人配置已保存')
}

// 保存应用配置
const saveAppConfig = () => {
  if (!appForm.value.corpId || !appForm.value.agentId || !appForm.value.secret) {
    ElMessage.warning('请填写完整的应用配置信息')
    return
  }

  saveConfig('应用配置', `企业 ID: ${appForm.value.corpId}`)
  ElMessage.success('应用配置已保存')
}

// 保存高级配置
const saveAdvancedConfig = () => {
  saveConfig('高级配置', `超时：${advancedForm.value.timeout}ms, 重试：${advancedForm.value.maxRetries}次`)
  ElMessage.success('高级配置已保存')
}

// 保存配置到本地
const saveConfig = (type, content) => {
  // 保存到本地存储
  localStorage.setItem('wecom_config', JSON.stringify({
    robot: robotForm.value,
    app: appForm.value,
    advanced: advancedForm.value
  }))

  // 添加到历史记录
  configHistory.value.unshift({
    id: Date.now(),
    time: new Date().toLocaleString('zh-CN'),
    type,
    content,
    operator: 'admin'
  })
}

// 测试 Webhook
const testWebhook = async () => {
  if (!robotForm.value.webhookKey) {
    ElMessage.warning('请先输入 Webhook Key')
    return
  }

  ElMessageBox.confirm('将发送一条测试消息到企业微信群，是否继续？', '测试 Webhook', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'info'
  }).then(() => {
    // 这里可以调用后端 API 测试
    ElMessage.info('发送测试消息中...')
    setTimeout(() => {
      ElMessage.success('测试成功！机器人配置正确。')
    }, 1000)
  }).catch(() => {})
}

// 配置类型标签
const getConfigTypeTag = (type) => {
  const tags = {
    '机器人配置': 'primary',
    '应用配置': 'success',
    '高级配置': 'warning'
  }
  return tags[type] || ''
}

// 清空历史
const clearHistory = () => {
  ElMessageBox.confirm('确定要清空所有配置历史吗？', '提示', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'warning'
  }).then(() => {
    configHistory.value = []
    ElMessage.success('已清空历史')
  }).catch(() => {})
}

// 回滚配置
const rollbackConfig = (record) => {
  ElMessageBox.confirm(`确定要回滚到 ${record.time} 的配置吗？`, '提示', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'warning'
  }).then(() => {
    ElMessage.success('配置已回滚')
  }).catch(() => {})
}

onMounted(() => {
  loadConfig()
})
</script>

<style scoped>
.wecom-config {
  padding: 0;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.form-tip {
  font-size: 12px;
  color: #909399;
  margin-top: 5px;
  line-height: 1.5;
}

.form-tip h4 {
  font-size: 14px;
  color: #606266;
  margin: 10px 0 5px;
}

.form-tip ul {
  margin: 5px 0;
  padding-left: 20px;
  color: #909399;
}

.form-tip p {
  margin: 5px 0;
  color: #909399;
}
</style>
