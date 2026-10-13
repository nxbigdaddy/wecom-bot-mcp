<template>
  <div class="users">
    <el-card>
      <template #header>
        <div class="header-actions">
          <span>用户管理</span>
          <el-button type="primary" @click="showAddDialog">
            <el-icon><Plus /></el-icon>
            添加用户
          </el-button>
        </div>
      </template>

      <!-- 搜索栏 -->
      <div class="search-bar">
        <el-input
          v-model="searchText"
          placeholder="搜索用户名、邮箱、手机号..."
          style="width: 300px"
          clearable
          @input="handleSearch"
        >
          <template #prefix>
            <el-icon><Search /></el-icon>
          </template>
        </el-input>

        <el-select v-model="filterStatus" placeholder="用户状态" clearable style="width: 150px">
          <el-option label="启用" :value="true" />
          <el-option label="禁用" :value="false" />
        </el-select>

        <el-select v-model="filterRole" placeholder="角色" clearable style="width: 150px">
          <el-option label="管理员" value="admin" />
          <el-option label="普通用户" value="user" />
          <el-option label="访客" value="guest" />
        </el-select>
      </div>

      <!-- 用户表格 -->
      <el-table :data="filteredUsers" style="width: 100%" stripe border>
        <el-table-column prop="id" label="ID" width="80" />
        
        <el-table-column prop="username" label="用户名" width="150" />
        
        <el-table-column prop="email" label="邮箱" min-width="180" />
        
        <el-table-column prop="phone" label="手机号" width="130" />
        
        <el-table-column prop="role" label="角色" width="100">
          <template #default="{ row }">
            <el-tag :type="getRoleTag(row.role)" size="small">
              {{ getRoleLabel(row.role) }}
            </el-tag>
          </template>
        </el-table-column>
        
        <el-table-column prop="status" label="状态" width="80">
          <template #default="{ row }">
            <el-tag :type="row.status ? 'success' : 'danger'" size="small">
              {{ row.status ? '启用' : '禁用' }}
            </el-tag>
          </template>
        </el-table-column>
        
        <el-table-column prop="created_at" label="创建时间" width="180">
          <template #default="{ row }">
            {{ formatTime(row.created_at) }}
          </template>
        </el-table-column>
        
        <el-table-column label="操作" width="220" fixed="right">
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
              @click="toggleUserStatus(row)"
            >
              {{ row.status ? '禁用' : '启用' }}
            </el-button>
            <el-button
              v-if="row.id !== currentUserId"
              type="danger"
              text
              size="small"
              @click="deleteUser(row)"
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
          :total="filteredUsers.length"
          :page-sizes="[10, 20, 50, 100]"
          layout="total, sizes, prev, pager, next, jumper"
        />
      </div>
    </el-card>

    <!-- 添加/编辑用户对话框 -->
    <el-dialog
      v-model="dialogVisible"
      :title="isEdit ? '编辑用户' : '添加用户'"
      width="500px"
    >
      <el-form :model="userForm" label-width="100px" :rules="rules" ref="userFormRef">
        <el-form-item label="用户名" prop="username">
          <el-input v-model="userForm.username" placeholder="请输入用户名" />
        </el-form-item>
        
        <el-form-item label="邮箱" prop="email">
          <el-input v-model="userForm.email" placeholder="请输入邮箱" />
        </el-form-item>
        
        <el-form-item label="手机号" prop="phone">
          <el-input v-model="userForm.phone" placeholder="请输入手机号" />
        </el-form-item>
        
        <el-form-item label="密码" :prop="isEdit ? '' : 'password'">
          <el-input
            v-model="userForm.password"
            type="password"
            :placeholder="isEdit ? '不修改请留空' : '请输入密码'"
            show-password
          />
        </el-form-item>
        
        <el-form-item label="角色">
          <el-select v-model="userForm.role" placeholder="选择角色" style="width: 100%">
            <el-option label="管理员" value="admin" />
            <el-option label="普通用户" value="user" />
            <el-option label="访客" value="guest" />
          </el-select>
        </el-form-item>
        
        <el-form-item label="状态">
          <el-switch v-model="userForm.status" active-text="启用" inactive-text="禁用" />
        </el-form-item>
      </el-form>
      
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="saveUser" :loading="saving">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'

// 模拟用户数据
const users = ref([
  {
    id: 1,
    username: 'admin',
    email: 'admin@example.com',
    phone: '13800138000',
    role: 'admin',
    status: true,
    created_at: '2026-03-01 10:00:00'
  },
  {
    id: 2,
    username: 'user1',
    email: 'user1@example.com',
    phone: '13900139000',
    role: 'user',
    status: true,
    created_at: '2026-03-05 14:30:00'
  },
  {
    id: 3,
    username: 'guest1',
    email: 'guest1@example.com',
    phone: '13700137000',
    role: 'guest',
    status: false,
    created_at: '2026-03-10 09:15:00'
  }
])

const searchText = ref('')
const filterStatus = ref('')
const filterRole = ref('')
const currentPage = ref(1)
const pageSize = ref(10)
const dialogVisible = ref(false)
const isEdit = ref(false)
const saving = ref(false)
const currentUserId = ref(1)

const userForm = ref({
  id: null,
  username: '',
  email: '',
  phone: '',
  password: '',
  role: 'user',
  status: true
})

const rules = {
  username: [{ required: true, message: '请输入用户名', trigger: 'blur' }],
  email: [
    { required: true, message: '请输入邮箱', trigger: 'blur' },
    { type: 'email', message: '邮箱格式不正确', trigger: 'blur' }
  ],
  password: [{ required: true, message: '请输入密码', trigger: 'blur', min: 6 }]
}

// 过滤后的用户列表
const filteredUsers = computed(() => {
  let result = [...users.value]

  // 搜索过滤
  if (searchText.value) {
    const text = searchText.value.toLowerCase()
    result = result.filter(user =>
      user.username.toLowerCase().includes(text) ||
      user.email.toLowerCase().includes(text) ||
      user.phone.includes(text)
    )
  }

  // 状态过滤
  if (filterStatus.value !== '') {
    result = result.filter(user => user.status === filterStatus.value)
  }

  // 角色过滤
  if (filterRole.value) {
    result = result.filter(user => user.role === filterRole.value)
  }

  return result
})

// 角色标签
const getRoleLabel = (role) => {
  const labels = {
    admin: '管理员',
    user: '普通用户',
    guest: '访客'
  }
  return labels[role] || role
}

const getRoleTag = (role) => {
  const tags = {
    admin: 'danger',
    user: '',
    guest: 'info'
  }
  return tags[role] || ''
}

// 格式化时间
const formatTime = (time) => time

// 搜索处理
const handleSearch = () => {
  currentPage.value = 1
}

// 显示添加对话框
const showAddDialog = () => {
  isEdit.value = false
  userForm.value = {
    id: null,
    username: '',
    email: '',
    phone: '',
    password: '',
    role: 'user',
    status: true
  }
  dialogVisible.value = true
}

// 显示编辑对话框
const showEditDialog = (user) => {
  isEdit.value = true
  userForm.value = {
    id: user.id,
    username: user.username,
    email: user.email,
    phone: user.phone,
    password: '',
    role: user.role,
    status: user.status
  }
  dialogVisible.value = true
}

// 保存用户
const saveUser = async () => {
  saving.value = true
  
  // 模拟保存
  setTimeout(() => {
    if (isEdit.value) {
      const index = users.value.findIndex(u => u.id === userForm.value.id)
      if (index !== -1) {
        users.value[index] = {
          ...users.value[index],
          ...userForm.value
        }
        ElMessage.success('用户已更新')
      }
    } else {
      const newUser = {
        ...userForm.value,
        id: users.value.length + 1,
        created_at: new Date().toLocaleString('zh-CN')
      }
      users.value.unshift(newUser)
      ElMessage.success('用户已添加')
    }
    
    dialogVisible.value = false
    saving.value = false
  }, 500)
}

// 切换用户状态
const toggleUserStatus = (user) => {
  ElMessageBox.confirm(
    `确定要${user.status ? '禁用' : '启用'}用户 "${user.username}" 吗？`,
    '提示',
    {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    }
  ).then(() => {
    user.status = !user.status
    ElMessage.success('操作成功')
  }).catch(() => {})
}

// 删除用户
const deleteUser = (user) => {
  ElMessageBox.confirm(
    `确定要删除用户 "${user.username}" 吗？此操作不可恢复。`,
    '警告',
    {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    }
  ).then(() => {
    const index = users.value.findIndex(u => u.id === user.id)
    if (index !== -1) {
      users.value.splice(index, 1)
      ElMessage.success('删除成功')
    }
  }).catch(() => {})
}
</script>

<style scoped>
.users {
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
</style>
