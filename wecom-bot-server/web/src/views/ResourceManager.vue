<template>
  <div class="resource-manager">
    <div class="page-header">
      <h2>企业微信上传资源管理</h2>
      <p>管理已上传到企业微信的图片、文件、视频等资源</p>
    </div>

    <!-- 上传区域 -->
    <el-card class="upload-section">
      <template #header>
        <div class="card-header">
          <span>上传新资源</span>
          <el-button type="primary" size="small" @click="showUploadDialog = true">
            <el-icon><Upload /></el-icon>
            上传文件
          </el-button>
        </div>
      </template>

      <div class="upload-types">
        <el-row :gutter="20">
          <el-col :span="6">
            <div class="upload-type-card" @click="uploadType = 'image'">
              <div class="type-icon" :class="{ active: uploadType === 'image' }">
                <el-icon :size="32"><Picture /></el-icon>
              </div>
              <div class="type-info">
                <div class="type-title">图片</div>
                <div class="type-desc">支持 JPG、PNG、GIF</div>
                <div class="type-limit">最大 10MB</div>
              </div>
            </div>
          </el-col>

          <el-col :span="6">
            <div class="upload-type-card" @click="uploadType = 'file'">
              <div class="type-icon" :class="{ active: uploadType === 'file' }">
                <el-icon :size="32"><Document /></el-icon>
              </div>
              <div class="type-info">
                <div class="type-title">文件</div>
                <div class="type-desc">支持 TXT、PDF、DOC、XLS</div>
                <div class="type-limit">最大 20MB</div>
              </div>
            </div>
          </el-col>

          <el-col :span="6">
            <div class="upload-type-card" @click="uploadType = 'video'">
              <div class="type-icon" :class="{ active: uploadType === 'video' }">
                <el-icon :size="32"><VideoPlay /></el-icon>
              </div>
              <div class="type-info">
                <div class="type-title">视频</div>
                <div class="type-desc">支持 MP4、AVI、MOV</div>
                <div class="type-limit">最大 10MB</div>
              </div>
            </div>
          </el-col>

          <el-col :span="6">
            <div class="upload-type-card" @click="uploadType = 'voice'">
              <div class="type-icon" :class="{ active: uploadType === 'voice' }">
                <el-icon :size="32"><Microphone /></el-icon>
              </div>
              <div class="type-info">
                <div class="type-title">语音</div>
                <div class="type-desc">支持 AMR、MP3</div>
                <div class="type-limit">最大 2MB</div>
              </div>
            </div>
          </el-col>
        </el-row>
      </div>
    </el-card>

    <!-- 资源列表 -->
    <el-card class="resource-list">
      <template #header>
        <div class="card-header">
          <span>已上传资源</span>
          <div class="header-actions">
            <el-input
              v-model="searchKeyword"
              placeholder="搜索资源名称"
              style="width: 200px; margin-right: 10px;"
              clearable
            />
            <el-select v-model="filterType" placeholder="全部类型" style="width: 120px; margin-right: 10px;">
              <el-option label="全部类型" value="" />
              <el-option label="图片" value="image" />
              <el-option label="文件" value="file" />
              <el-option label="视频" value="video" />
              <el-option label="语音" value="voice" />
            </el-select>
            <el-button type="primary" @click="refreshList">
              <el-icon><Refresh /></el-icon>
              刷新
            </el-button>
          </div>
        </div>
      </template>

      <el-table :data="filteredResources" v-loading="loading">
        <el-table-column prop="name" label="资源名称" width="200">
          <template #default="{ row }">
            <div class="resource-name">
              <el-icon v-if="row.type === 'image'"><Picture /></el-icon>
              <el-icon v-else-if="row.type === 'file'"><Document /></el-icon>
              <el-icon v-else-if="row.type === 'video'"><VideoPlay /></el-icon>
              <el-icon v-else-if="row.type === 'voice'"><Microphone /></el-icon>
              <span>{{ row.name }}</span>
            </div>
          </template>
        </el-table-column>
        
        <el-table-column prop="type" label="类型" width="100">
          <template #default="{ row }">
            <el-tag :type="getTypeTag(row.type)">{{ getTypeText(row.type) }}</el-tag>
          </template>
        </el-table-column>
        
        <el-table-column prop="mediaId" label="Media ID" width="280">
          <template #default="{ row }">
            <el-tooltip :content="row.mediaId" placement="top">
              <span class="media-id">{{ row.mediaId }}</span>
            </el-tooltip>
            <el-button size="small" type="text" @click="copyMediaId(row.mediaId)">
              <el-icon><CopyDocument /></el-icon>
            </el-button>
          </template>
        </el-table-column>
        
        <el-table-column prop="size" label="大小" width="100">
          <template #default="{ row }">{{ formatSize(row.size) }}</template>
        </el-table-column>
        
        <el-table-column prop="uploadTime" label="上传时间" width="180" />
        
        <el-table-column label="操作" width="200">
          <template #default="{ row }">
            <el-button size="small" type="primary" @click="previewResource(row)">
              <el-icon><View /></el-icon>
              预览
            </el-button>
            <el-button size="small" type="danger" @click="deleteResource(row)">
              <el-icon><Delete /></el-icon>
              删除
            </el-button>
          </template>
        </el-table-column>
      </el-table>

      <div class="pagination">
        <el-pagination
          v-model:current-page="currentPage"
          v-model:page-size="pageSize"
          :total="total"
          :page-sizes="[10, 20, 50, 100]"
          layout="total, sizes, prev, pager, next, jumper"
          @size-change="handleSizeChange"
          @current-change="handleCurrentChange"
        />
      </div>
    </el-card>

    <!-- 上传对话框 -->
    <el-dialog
      v-model="showUploadDialog"
      title="上传文件"
      width="500px"
      :before-close="handleClose"
    >
      <el-form :model="uploadForm" label-width="80px">
        <el-form-item label="文件类型">
          <el-select v-model="uploadForm.type" placeholder="请选择文件类型">
            <el-option label="图片" value="image" />
            <el-option label="文件" value="file" />
            <el-option label="视频" value="video" />
            <el-option label="语音" value="voice" />
          </el-select>
        </el-form-item>

        <el-form-item label="选择文件">
          <el-upload
            class="upload-demo"
            drag
            :action="uploadUrl"
            :headers="uploadHeaders"
            :on-success="handleUploadSuccess"
            :on-error="handleUploadError"
            :before-upload="beforeUpload"
            :show-file-list="false"
          >
            <el-icon class="el-icon--upload"><upload-filled /></el-icon>
            <div class="el-upload__text">
              拖拽文件到此处或<em>点击上传</em>
            </div>
            <template #tip>
              <div class="el-upload__tip">
                支持 {{ getAcceptType() }} 格式，大小不超过 {{ getMaxSize() }}MB
              </div>
            </template>
          </el-upload>
        </el-form-item>

        <el-form-item v-if="uploadForm.file" label="文件信息">
          <div class="file-info">
            <div>文件名：{{ uploadForm.file.name }}</div>
            <div>文件大小：{{ formatSize(uploadForm.file.size) }}</div>
            <div>文件类型：{{ uploadForm.file.type }}</div>
          </div>
        </el-form-item>
      </el-form>

      <template #footer>
        <span class="dialog-footer">
          <el-button @click="showUploadDialog = false">取消</el-button>
          <el-button type="primary" @click="submitUpload" :loading="uploading">
            上传
          </el-button>
        </span>
      </template>
    </el-dialog>

    <!-- 预览对话框 -->
    <el-dialog
      v-model="showPreviewDialog"
      :title="previewTitle"
      width="80%"
      top="5vh"
    >
      <div class="preview-content">
        <div v-if="previewResourceType === 'image'" class="image-preview">
          <el-image :src="previewUrl" fit="contain" style="max-height: 60vh;" />
        </div>
        
        <div v-else-if="previewResourceType === 'video'" class="video-preview">
          <video :src="previewUrl" controls style="max-height: 60vh; max-width: 100%;" />
        </div>
        
        <div v-else-if="previewResourceType === 'voice'" class="audio-preview">
          <audio :src="previewUrl" controls style="width: 100%;" />
        </div>
        
        <div v-else class="file-preview">
          <el-empty description="该文件类型不支持在线预览" />
          <div class="file-info">
            <p>文件名：{{ previewResourceName }}</p>
            <p>文件大小：{{ formatSize(previewResourceSize) }}</p>
            <p>Media ID：{{ previewMediaId }}</p>
          </div>
        </div>
      </div>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { useClipboard } from '@vueuse/core'
import {
  Upload,
  Picture,
  Document,
  VideoPlay,
  Microphone,
  Refresh,
  CopyDocument,
  View,
  Delete
} from '@element-plus/icons-vue'

// 状态
const uploadType = ref('image')
const searchKeyword = ref('')
const filterType = ref('')
const loading = ref(false)
const currentPage = ref(1)
const pageSize = ref(10)
const total = ref(0)
const showUploadDialog = ref(false)
const showPreviewDialog = ref(false)
const uploading = ref(false)

// 上传表单
const uploadForm = ref({
  type: 'image',
  file: null
})

// 预览数据
const previewUrl = ref('')
const previewTitle = ref('')
const previewResourceType = ref('')
const previewResourceName = ref('')
const previewResourceSize = ref(0)
const previewMediaId = ref('')

// 模拟数据
const resources = ref([
  {
    id: 1,
    name: '产品介绍.png',
    type: 'image',
    mediaId: '3rJDFDrvTZUvz0f',
    size: 1024 * 1024 * 2, // 2MB
    uploadTime: '2026-03-15 10:30:00'
  },
  {
    id: 2,
    name: '会议纪要.pdf',
    type: 'file',
    mediaId: '4sKEFEsvUZAvz1g',
    size: 1024 * 1024 * 5, // 5MB
    uploadTime: '2026-03-15 14:20:00'
  },
  {
    id: 3,
    name: '产品演示.mp4',
    type: 'video',
    mediaId: '5tLGFGtwVABwz2h',
    size: 1024 * 1024 * 8, // 8MB
    uploadTime: '2026-03-16 09:15:00'
  },
  {
    id: 4,
    name: '语音通知.amr',
    type: 'voice',
    mediaId: '6uMGHGuxWBCxz3i',
    size: 1024 * 1024, // 1MB
    uploadTime: '2026-03-16 11:45:00'
  }
])

// 计算属性
const filteredResources = computed(() => {
  let result = resources.value
  
  // 按类型过滤
  if (filterType.value) {
    result = result.filter(item => item.type === filterType.value)
  }
  
  // 按关键词搜索
  if (searchKeyword.value) {
    const keyword = searchKeyword.value.toLowerCase()
    result = result.filter(item => 
      item.name.toLowerCase().includes(keyword) ||
      item.mediaId.toLowerCase().includes(keyword)
    )
  }
  
  // 分页
  total.value = result.length
  const start = (currentPage.value - 1) * pageSize.value
  const end = start + pageSize.value
  return result.slice(start, end)
})

// 上传配置
const uploadUrl = computed(() => {
  return '/api/v1/upload-file'
})

const uploadHeaders = computed(() => {
  const token = YOUR_SECRET'token')
  return {
    'Authorization': `Bearer ${token}`
  }
})

// 方法
const getTypeTag = (type) => {
  const map = {
    image: 'success',
    file: 'info',
    video: 'warning',
    voice: 'danger'
  }
  return map[type] || 'info'
}

const getTypeText = (type) => {
  const map = {
    image: '图片',
    file: '文件',
    video: '视频',
    voice: '语音'
  }
  return map[type] || '未知'
}

const formatSize = (bytes) => {
  if (bytes === 0) return '0 B'
  const k = 1024
  const sizes = ['B', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
}

const copyMediaId = async (mediaId) => {
  const { copy } = useClipboard()
  await copy(mediaId)
  ElMessage.success('Media ID 已复制到剪贴板')
}

const refreshList = async () => {
  loading.value = true
  try {
    // 这里应该调用 API 获取资源列表
    // const response = await fetch('/api/v1/resources')
    // resources.value = await response.json()
    await new Promise(resolve => setTimeout(resolve, 500)) // 模拟延迟
    ElMessage.success('资源列表已刷新')
  } catch (error) {
    ElMessage.error('刷新失败：' + error.message)
  } finally {
    loading.value = false
  }
}

const previewResource = (resource) => {
  previewResourceType.value = resource.type
  previewResourceName.value = resource.name
  previewResourceSize.value = resource.size
  previewMediaId.value = resource.mediaId
  previewTitle.value = `预览 - ${resource.name}`
  
  // 根据类型设置预览 URL
  if (resource.type === 'image') {
    previewUrl.value = `https://example.com/images/${resource.name}`
  } else if (resource.type === 'video') {
    previewUrl.value = `https://example.com/videos/${resource.name}`
  } else if (resource.type === 'voice') {
    previewUrl.value = `https://example.com/audio/${resource.name}`
  }
  
  showPreviewDialog.value = true
}

const deleteResource = async (resource) => {
  try {
    await ElMessageBox.confirm(
      `确定要删除资源 "${resource.name}" 吗？`,
      '删除确认',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    
    // 这里应该调用 API 删除资源
    // await fetch(`/api/v1/resources/${resource.id}`, { method: 'DELETE' })
    
    resources.value = resources.value.filter(item => item.id !== resource.id)
    ElMessage.success('资源删除成功')
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('删除失败：' + error.message)
    }
  }
}

const getAcceptType = () => {
  const map = {
    image: 'JPG、PNG、GIF',
    file: 'TXT、PDF、DOC、XLS',
    video: 'MP4、AVI、MOV',
    voice: 'AMR、MP3'
  }
  return map[uploadForm.value.type] || '所有文件'
}

const getMaxSize = () => {
  const map = {
    image: 10,
    file: 20,
    video: 10,
    voice: 2
  }
  return map[uploadForm.value.type] || 20
}

const beforeUpload = (file) => {
  uploadForm.value.file = file
  
  // 检查文件大小
  const maxSize = getMaxSize() * 1024 * 1024
  if (file.size > maxSize) {
    ElMessage.error(`文件大小不能超过 ${getMaxSize()}MB`)
    return false
  }
  
  return true
}

const handleUploadSuccess = (response) => {
  uploading.value = false
  if (response.success) {
    ElMessage.success('文件上传成功')
    showUploadDialog.value = false
    refreshList()
  } else {
    ElMessage.error('上传失败：' + response.message)
  }
}

const handleUploadError = (error) => {
  uploading.value = false
  ElMessage.error('上传失败：' + error.message)
}

const submitUpload = () => {
  if (!uploadForm.value.file) {
    ElMessage.warning('请先选择文件')
    return
  }
  
  uploading.value = true
  // 这里应该触发上传组件的上传
  // 实际由 el-upload 组件处理
}

const handleClose = (done) => {
  ElMessageBox.confirm('确定要关闭吗？上传中的文件将不会被保存。')
    .then(() => {
      done()
    })
    .catch(() => {
      // 取消关闭
    })
}

const handleSizeChange = (val) => {
  pageSize.value = val
  currentPage.value = 1
}

const handleCurrentChange = (val) => {
  currentPage.value = val
}

// 生命周期
onMounted(() => {
  refreshList()
})
</script>

<style scoped>
.resource-manager {
  padding: 20px;
}

.page-header {
  margin-bottom: 20px;
}

.page-header h2 {
  margin: 0;
  font-size: 24px;
  color: #303133;
}

.page-header p {
  margin: 8px 0 0;
  color: #606266;
  font-size: 14px;
}

.upload-section {
  margin-bottom: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.upload-types {
  margin-top: 10px;
}

.upload-type-card {
  border: 1px solid #e4e7ed;
  border-radius: 8px;
  padding: 20px;
  cursor: pointer;
  transition: all 0.3s;
  display: flex;
  align-items: center;
}

.upload-type-card:hover {
  border-color: #409EFF;
  box-shadow: 0 2px 12px rgba(64, 158, 255, 0.1);
}

.upload-type-card.active {
  border-color: #409EFF;
  background-color: #f0f7ff;
}

.type-icon {
  width: 60px;
  height: 60px;
  border-radius: 8px;
  background-color: #f5f7fa;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-right: 15px;
  color: #909399;
}

.type-icon.active {
  background-color: #409EFF;
  color: white;
}

.type-info {
  flex: 1;
}

.type-title {
  font-size: 16px;
  font-weight: 600;
  color: #303133;
  margin-bottom: 4px;
}

.type-desc {
  font-size: 12px;
  color: #909399;
  margin-bottom: 4px;
}

.type-limit {
  font-size: 12px;
  color: #67C23A;
}

.resource-list {
  margin-top: 20px;
}

.header-actions {
  display: flex;
  align-items: center;
}

.resource-name {
  display: flex;
  align-items: center;
  gap: 8px;
}

.media-id {
  display: inline-block;
  max-width: 200px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  font-family: monospace;
  background-color: #f5f7fa;
  padding: 2px 6px;
  border-radius: 4px;
  font-size: 12px;
}

.pagination {
  margin-top: 20px;
  display: flex;
  justify-content: flex-end;
}

.file-info {
  font-size: 12px;
  color: #606266;
  line-height: 1.5;
}

.preview-content {
  text-align: center;
}

.file-preview {
  padding: 40px 0;
}

.file-info p {
  margin: 8px 0;
  font-size: 14px;
  color: #606266;
}
</style>