<template>
  <div class="hr-integration">
    <!-- HR 系统配置 -->
    <el-card class="config-card">
      <template #header>
        <div class="card-header">
          <span>HR 系统配置</span>
          <el-button type="primary" @click="testConnection" :loading="testing">
            <el-icon><Connection /></el-icon>
            测试连接
          </el-button>
        </div>
      </template>

      <el-form :model="hrConfig" label-width="140px" size="large">
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="HR 系统名称">
              <el-select v-model="hrConfig.systemType" placeholder="选择 HR 系统" style="width: 100%">
                <el-option label="钉钉" value="dingtalk" />
                <el-option label="企业微信" value="wecom" />
                <el-option label="飞书" value="feishu" />
                <el-option label="北森" value="beisen" />
                <el-option label="肯耐珂萨" value="knx" />
                <el-option label="自定义 API" value="custom" />
              </el-select>
            </el-form-item>
          </el-col>
          
          <el-col :span="12">
            <el-form-item label="数据同步方式">
              <el-select v-model="hrConfig.syncMode" placeholder="选择同步方式" style="width: 100%">
                <el-option label="API 自动同步" value="api" />
                <el-option label="CSV 文件导入" value="csv" />
                <el-option label="Excel 文件导入" value="excel" />
                <el-option label="数据库直连" value="database" />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>

        <el-row :gutter="20" v-if="hrConfig.syncMode === 'api'">
          <el-col :span="12">
            <el-form-item label="API 地址">
              <el-input v-model="hrConfig.apiUrl" placeholder="https://api.example.com/v1/employees" />
            </el-form-item>
          </el-col>
          
          <el-col :span="12">
            <el-form-item label="API Token">
              <el-input v-model="hrConfig.apiToken" type="password" show-password placeholder="YOUR_PASSWORD" />
            </el-form-item>
          </el-col>
        </el-row>

        <el-row :gutter="20" v-if="hrConfig.syncMode === 'database'">
          <el-col :span="8">
            <el-form-item label="数据库类型">
              <el-select v-model="hrConfig.dbType" placeholder="选择数据库" style="width: 100%">
                <el-option label="MySQL" value="mysql" />
                <el-option label="PostgreSQL" value="postgresql" />
                <el-option label="SQL Server" value="sqlserver" />
                <el-option label="Oracle" value="oracle" />
              </el-select>
            </el-form-item>
          </el-col>
          
          <el-col :span="8">
            <el-form-item label="主机地址">
              <el-input v-model="hrConfig.dbHost" placeholder="localhost" />
            </el-form-item>
          </el-col>
          
          <el-col :span="8">
            <el-form-item label="端口">
              <el-input v-model="hrConfig.dbPort" :placeholder="getDefaultPort(hrConfig.dbType)" />
            </el-form-item>
          </el-col>
          
          <el-col :span="8">
            <el-form-item label="数据库名">
              <el-input v-model="hrConfig.dbName" placeholder="hr_database" />
            </el-form-item>
          </el-col>
          
          <el-col :span="8">
            <el-form-item label="用户名">
              <el-input v-model="hrConfig.dbUser" placeholder="root" />
            </el-form-item>
          </el-col>
          
          <el-col :span="8">
            <el-form-item label="密码">
              <el-input v-model="hrConfig.dbPassword" type="YOUR_PASSWORD" show-password placeholder="YOUR_PASSWORD" />
            </el-form-item>
          </el-col>
          
          <el-col :span="24">
            <el-form-item label="员工表名">
              <el-input v-model="hrConfig.tableName" placeholder="employees" />
            </el-form-item>
          </el-col>
        </el-row>

        <el-row :gutter="20">
          <el-col :span="24">
            <el-form-item label="同步频率">
              <el-select v-model="hrConfig.syncFrequency" placeholder="选择同步频率" style="width: 200px">
                <el-option label="每小时" value="hourly" />
                <el-option label="每天" value="daily" />
                <el-option label="每周" value="weekly" />
                <el-option label="每月" value="monthly" />
                <el-option label="手动同步" value="manual" />
              </el-select>
              <span class="form-tip">自动从 HR 系统同步员工数据</span>
            </el-form-item>
          </el-col>
        </el-row>

        <el-form-item>
          <el-button type="primary" @click="saveConfig" :loading="saving">保存配置</el-button>
          <el-button @click="syncNow" :loading="syncing">立即同步</el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <!-- 员工列表 -->
    <el-card class="employee-card">
      <template #header>
        <div class="card-header">
          <span>员工信息管理</span>
          <div class="header-actions">
            <el-button type="success" @click="importData">
              <el-icon><Upload /></el-icon>
              导入数据
            </el-button>
            <el-button type="primary" @click="showAddEmployee">
              <el-icon><Plus /></el-icon>
              添加员工
            </el-button>
          </div>
        </div>
      </template>

      <!-- 搜索栏 -->
      <div class="search-bar">
        <el-input
          v-model="searchText"
          placeholder="搜索姓名、工号、部门..."
          style="width: 300px"
          clearable
          @input="handleSearch"
        >
          <template #prefix>
            <el-icon><Search /></el-icon>
          </template>
        </el-input>

        <el-select v-model="filterDepartment" placeholder="选择部门" clearable style="width: 150px" @change="handleSearch">
          <el-option
            v-for="dept in departments"
            :key="dept"
            :label="dept"
            :value="dept"
          />
        </el-select>

        <el-select v-model="filterStatus" placeholder="员工状态" clearable style="width: 120px" @change="handleSearch">
          <el-option label="在职" :value="true" />
          <el-option label="离职" :value="false" />
        </el-select>

        <el-date-picker
          v-model="birthdayRange"
          type="daterange"
          range-separator="至"
          start-placeholder="生日开始"
          end-placeholder="生日结束"
          format="YYYY-MM-DD"
          value-format="YYYY-MM-DD"
          style="width: 240px"
          @change="handleSearch"
        />
      </div>

      <!-- 员工表格 -->
      <el-table :data="filteredEmployees" style="width: 100%" stripe border height="600">
        <el-table-column prop="id" label="ID" width="70" />
        <el-table-column prop="employee_id" label="工号" width="100" />
        <el-table-column prop="name" label="姓名" width="100" />
        
        <el-table-column prop="gender" label="性别" width="60">
          <template #default="{ row }">
            <el-tag :type="row.gender === '男' ? 'primary' : 'danger'" size="small">
              {{ row.gender }}
            </el-tag>
          </template>
        </el-table-column>
        
        <el-table-column prop="birthday" label="生日" width="110">
          <template #default="{ row }">
            <div class="birthday-cell">
              <span>{{ row.birthday }}</span>
              <span v-if="isBirthdayToday(row.birthday)" class="birthday-badge">🎂 今天生日</span>
            </div>
          </template>
        </el-table-column>
        
        <el-table-column prop="department" label="部门" width="120" />
        <el-table-column prop="position" label="职位" width="120" />
        
        <el-table-column prop="hire_date" label="入职日期" width="110">
          <template #default="{ row }">
            <div class="hire-date-cell">
              <span>{{ row.hire_date }}</span>
              <span v-if="getWorkAnniversary(row.hire_date)" class="anniversary-badge">
                🎉 {{ getWorkAnniversary(row.hire_date) }}周年
              </span>
            </div>
          </template>
        </el-table-column>
        
        <el-table-column prop="email" label="邮箱" min-width="180" show-overflow-tooltip />
        
        <el-table-column prop="phone" label="手机号" width="130" />
        
        <el-table-column prop="wecom_userid" label="企微 ID" width="120">
          <template #default="{ row }">
            <el-tag v-if="row.wecom_userid" type="success" size="small">已绑定</el-tag>
            <el-tag v-else type="info" size="small">未绑定</el-tag>
          </template>
        </el-table-column>
        
        <el-table-column prop="status" label="状态" width="70">
          <template #default="{ row }">
            <el-tag :type="row.status ? 'success' : 'info'" size="small">
              {{ row.status ? '在职' : '离职' }}
            </el-tag>
          </template>
        </el-table-column>
        
        <el-table-column label="操作" width="220" fixed="right">
          <template #default="{ row }">
            <el-button type="primary" text size="small" @click="editEmployee(row)">编辑</el-button>
            <el-button type="warning" text size="small" @click="sendBirthdayMsg(row)">生日祝福</el-button>
            <el-button type="success" text size="small" @click="sendAnniversaryMsg(row)">周年祝福</el-button>
          </template>
        </el-table-column>
      </el-table>

      <!-- 分页 -->
      <div class="pagination-bar">
        <el-pagination
          v-model:current-page="currentPage"
          v-model:page-size="pageSize"
          :total="filteredEmployees.length"
          :page-sizes="[20, 50, 100, 200]"
          layout="total, sizes, prev, pager, next, jumper"
        />
      </div>
    </el-card>

    <!-- 数据统计 -->
    <el-row :gutter="20" class="stats-row">
      <el-col :span="6">
        <el-card class="stat-card">
          <el-statistic title="总员工数" :value="totalEmployees">
            <template #suffix>人</template>
          </el-statistic>
        </el-card>
      </el-col>
      
      <el-col :span="6">
        <el-card class="stat-card">
          <el-statistic title="今日生日" :value="todayBirthdayCount" class="birthday-stat">
            <template #suffix>人 🎂</template>
          </el-statistic>
        </el-card>
      </el-col>
      
      <el-col :span="6">
        <el-card class="stat-card">
          <el-statistic title="本周生日" :value="weekBirthdayCount">
            <template #suffix>人 🎂</template>
          </el-statistic>
        </el-card>
      </el-col>
      
      <el-col :span="6">
        <el-card class="stat-card">
          <el-statistic title="本月生日" :value="monthBirthdayCount">
            <template #suffix>人 🎂</template>
          </el-statistic>
        </el-card>
      </el-col>
    </el-row>

    <!-- 添加/编辑员工对话框 -->
    <el-dialog
      v-model="employeeDialogVisible"
      :title="isEdit ? '编辑员工' : '添加员工'"
      width="700px"
    >
      <el-form :model="employeeForm" label-width="120px" :rules="employeeRules" ref="employeeFormRef">
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="工号" prop="employee_id">
              <el-input v-model="employeeForm.employee_id" placeholder="请输入工号" />
            </el-form-item>
          </el-col>
          
          <el-col :span="12">
            <el-form-item label="姓名" prop="name">
              <el-input v-model="employeeForm.name" placeholder="请输入姓名" />
            </el-form-item>
          </el-col>
          
          <el-col :span="12">
            <el-form-item label="性别" prop="gender">
              <el-select v-model="employeeForm.gender" placeholder="选择性别" style="width: 100%">
                <el-option label="男" value="男" />
                <el-option label="女" value="女" />
              </el-select>
            </el-form-item>
          </el-col>
          
          <el-col :span="12">
            <el-form-item label="生日" prop="birthday">
              <el-date-picker
                v-model="employeeForm.birthday"
                type="date"
                placeholder="选择生日"
                format="YYYY-MM-DD"
                value-format="YYYY-MM-DD"
                style="width: 100%"
              />
            </el-form-item>
          </el-col>
          
          <el-col :span="12">
            <el-form-item label="部门" prop="department">
              <el-select v-model="employeeForm.department" placeholder="选择部门" style="width: 100%" allow-create filterable>
                <el-option
                  v-for="dept in departments"
                  :key="dept"
                  :label="dept"
                  :value="dept"
                />
              </el-select>
            </el-form-item>
          </el-col>
          
          <el-col :span="12">
            <el-form-item label="职位" prop="position">
              <el-input v-model="employeeForm.position" placeholder="请输入职位" />
            </el-form-item>
          </el-col>
          
          <el-col :span="12">
            <el-form-item label="入职日期" prop="hire_date">
              <el-date-picker
                v-model="employeeForm.hire_date"
                type="date"
                placeholder="选择入职日期"
                format="YYYY-MM-DD"
                value-format="YYYY-MM-DD"
                style="width: 100%"
              />
            </el-form-item>
          </el-col>
          
          <el-col :span="12">
            <el-form-item label="状态">
              <el-switch v-model="employeeForm.status" active-text="在职" inactive-text="离职" />
            </el-form-item>
          </el-col>
          
          <el-col :span="24">
            <el-form-item label="邮箱" prop="email">
              <el-input v-model="employeeForm.email" placeholder="请输入邮箱" />
            </el-form-item>
          </el-col>
          
          <el-col :span="24">
            <el-form-item label="手机号" prop="phone">
              <el-input v-model="employeeForm.phone" placeholder="请输入手机号" />
            </el-form-item>
          </el-col>
          
          <el-col :span="24">
            <el-form-item label="企业微信 ID">
              <el-input v-model="employeeForm.wecom_userid" placeholder="企业微信用户 ID（用于发送消息）" />
              <div class="form-tip">
                绑定企业微信 ID 后可自动发送生日祝福和周年纪念
              </div>
            </el-form-item>
          </el-col>
        </el-row>
      </el-form>
      
      <template #footer>
        <el-button @click="employeeDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="saveEmployee" :loading="saving">保存</el-button>
      </template>
    </el-dialog>

    <!-- 同步历史 -->
    <el-dialog v-model="syncHistoryVisible" title="同步历史" width="800px">
      <el-table :data="syncHistory" style="width: 100%" stripe border>
        <el-table-column prop="time" label="同步时间" width="180" />
        <el-table-column prop="source" label="数据源" width="120" />
        <el-table-column prop="added" label="新增" width="80">
          <template #default="{ row }">
            <el-tag type="success" size="small">+{{ row.added }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="updated" label="更新" width="80">
          <template #default="{ row }">
            <el-tag type="warning" size="small">{{ row.updated }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="status" label="状态" width="80">
          <template #default="{ row }">
            <el-tag :type="row.status ? 'success' : 'danger'" size="small">
              {{ row.status ? '成功' : '失败' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="message" label="详情" min-width="200" show-overflow-tooltip />
      </el-table>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'

// HR 配置
const hrConfig = ref({
  systemType: 'wecom',
  syncMode: 'api',
  apiUrl: '',
  apiToken: '',
  dbType: 'mysql',
  dbHost: '',
  dbPort: '',
  dbName: '',
  dbUser: '',
  dbPassword: '',
  tableName: 'employees',
  syncFrequency: 'daily'
})

const testing = ref(false)
const saving = ref(false)
const syncing = ref(false)
const syncHistoryVisible = ref(false)

// 模拟员工数据
const employees = ref([
  {
    id: 1,
    employee_id: 'E001',
    name: '张三',
    gender: '男',
    birthday: '1990-03-16',
    department: '技术部',
    position: '高级工程师',
    hire_date: '2020-03-16',
    email: 'zhangsan@example.com',
    phone: '13800138001',
    wecom_userid: 'zhangsan',
    status: true
  },
  {
    id: 2,
    employee_id: 'E002',
    name: '李四',
    gender: '女',
    birthday: '1992-05-20',
    department: '产品部',
    position: '产品经理',
    hire_date: '2019-05-20',
    email: 'lisi@example.com',
    phone: '13800138002',
    wecom_userid: 'lisi',
    status: true
  },
  {
    id: 3,
    employee_id: 'E003',
    name: '王五',
    gender: '男',
    birthday: '1988-08-15',
    department: '销售部',
    position: '销售总监',
    hire_date: '2018-08-15',
    email: 'wangwu@example.com',
    phone: '13800138003',
    wecom_userid: 'wangwu',
    status: true
  }
])

const searchText = ref('')
const filterDepartment = ref('')
const filterStatus = ref('')
const birthdayRange = ref([])
const currentPage = ref(1)
const pageSize = ref(20)
const employeeDialogVisible = ref(false)
const isEdit = ref(false)

const employeeForm = ref({
  id: null,
  employee_id: '',
  name: '',
  gender: '男',
  birthday: '',
  department: '',
  position: '',
  hire_date: '',
  email: '',
  phone: '',
  wecom_userid: '',
  status: true
})

const employeeRules = {
  employee_id: [{ required: true, message: '请输入工号', trigger: 'blur' }],
  name: [{ required: true, message: '请输入姓名', trigger: 'blur' }],
  gender: [{ required: true, message: '请选择性别', trigger: 'change' }],
  birthday: [{ required: true, message: '请选择生日', trigger: 'change' }],
  department: [{ required: true, message: '请选择部门', trigger: 'change' }],
  hire_date: [{ required: true, message: '请选择入职日期', trigger: 'change' }],
  email: [
    { required: true, message: '请输入邮箱', trigger: 'blur' },
    { type: 'email', message: '请输入正确的邮箱格式', trigger: 'blur' }
  ]
}

// 部门列表
const departments = computed(() => {
  const depts = new Set(employees.value.map(e => e.department))
  return Array.from(depts)
})

// 过滤后的员工列表
const filteredEmployees = computed(() => {
  let result = [...employees.value]

  // 搜索过滤
  if (searchText.value) {
    const text = searchText.value.toLowerCase()
    result = result.filter(emp =>
      emp.name.toLowerCase().includes(text) ||
      emp.employee_id.toLowerCase().includes(text) ||
      emp.department.toLowerCase().includes(text)
    )
  }

  // 部门过滤
  if (filterDepartment.value) {
    result = result.filter(emp => emp.department === filterDepartment.value)
  }

  // 状态过滤
  if (filterStatus.value !== '') {
    result = result.filter(emp => emp.status === filterStatus.value)
  }

  // 生日范围过滤
  if (birthdayRange.value && birthdayRange.value.length === 2) {
    const [start, end] = birthdayRange.value
    result = result.filter(emp => {
      const birthday = emp.birthday
      return birthday >= start && birthday <= end
    })
  }

  return result
})

// 统计数据
const totalEmployees = computed(() => employees.value.filter(e => e.status).length)

const todayBirthdayCount = computed(() => {
  const today = new Date().toISOString().slice(5, 10) // MM-DD
  return employees.value.filter(e => {
    const birthday = e.birthday.slice(5, 10)
    return birthday === today && e.status
  }).length
})

const weekBirthdayCount = computed(() => {
  // 简化计算，实际应该计算本周范围
  return Math.floor(Math.random() * 5)
})

const monthBirthdayCount = computed(() => {
  const currentMonth = new Date().getMonth() + 1
  return employees.value.filter(e => {
    const month = parseInt(e.birthday.split('-')[1])
    return month === currentMonth && e.status
  }).length
})

// 获取默认端口
const getDefaultPort = (dbType) => {
  const ports = {
    mysql: '3306',
    postgresql: '5432',
    sqlserver: '1433',
    oracle: '1521'
  }
  return ports[dbType] || ''
}

// 判断是否今天生日
const isBirthdayToday = (birthday) => {
  const today = new Date().toISOString().slice(5, 10)
  return birthday.slice(5, 10) === today
}

// 计算入职周年
const getWorkAnniversary = (hireDate) => {
  const hire = new Date(hireDate)
  const now = new Date()
  const years = now.getFullYear() - hire.getFullYear()
  
  // 检查是否已经过了今年的入职纪念日
  const anniversary = new Date(now.getFullYear(), hire.getMonth(), hire.getDate())
  if (now >= anniversary) {
    return years
  }
  return years > 0 ? years - 1 : 0
}

// 搜索处理
const handleSearch = () => {
  currentPage.value = 1
}

// 测试连接
const testConnection = async () => {
  testing.value = true
  setTimeout(() => {
    ElMessage.success('连接测试成功！')
    testing.value = false
  }, 1000)
}

// 保存配置
const saveConfig = async () => {
  saving.value = true
  setTimeout(() => {
    ElMessage.success('配置已保存')
    saving.value = false
  }, 500)
}

// 立即同步
const syncNow = async () => {
  syncing.value = true
  setTimeout(() => {
    ElMessage.success('数据同步成功！新增 3 人，更新 5 人')
    syncing.value = false
  }, 2000)
}

// 导入数据
const importData = () => {
  ElMessageBox.confirm(
    '支持 CSV、Excel 文件格式导入员工数据',
    '导入数据',
    {
      confirmButtonText: '选择文件',
      cancelButtonText: '取消',
      type: 'info'
    }
  ).then(() => {
    ElMessage.info('请选择要导入的文件')
  }).catch(() => {})
}

// 显示添加员工
const showAddEmployee = () => {
  isEdit.value = false
  employeeForm.value = {
    id: null,
    employee_id: '',
    name: '',
    gender: '男',
    birthday: '',
    department: '',
    position: '',
    hire_date: '',
    email: '',
    phone: '',
    wecom_userid: '',
    status: true
  }
  employeeDialogVisible.value = true
}

// 编辑员工
const editEmployee = (employee) => {
  isEdit.value = true
  employeeForm.value = { ...employee }
  employeeDialogVisible.value = true
}

// 保存员工
const saveEmployee = async () => {
  saving.value = true
  setTimeout(() => {
    if (isEdit.value) {
      const index = employees.value.findIndex(e => e.id === employeeForm.value.id)
      if (index !== -1) {
        employees.value[index] = { ...employees.value[index], ...employeeForm.value }
        ElMessage.success('员工信息已更新')
      }
    } else {
      const newEmployee = {
        ...employeeForm.value,
        id: employees.value.length + 1
      }
      employees.value.unshift(newEmployee)
      ElMessage.success('员工已添加')
    }
    employeeDialogVisible.value = false
    saving.value = false
  }, 500)
}

// 发送生日祝福
const sendBirthdayMsg = (employee) => {
  ElMessageBox.confirm(
    `确定要给 ${employee.name} 发送生日祝福吗？`,
    '发送生日祝福',
    {
      confirmButtonText: '发送',
      cancelButtonText: '取消',
      type: 'info'
    }
  ).then(() => {
    ElMessage.success(`已向 ${employee.name} 发送生日祝福！`)
  }).catch(() => {})
}

// 发送周年祝福
const sendAnniversaryMsg = (employee) => {
  const years = getWorkAnniversary(employee.hire_date)
  ElMessageBox.confirm(
    `确定要给 ${employee.name} 发送入职${years}周年祝福吗？`,
    '发送周年祝福',
    {
      confirmButtonText: '发送',
      cancelButtonText: '取消',
      type: 'info'
    }
  ).then(() => {
    ElMessage.success(`已向 ${employee.name} 发送入职${years}周年祝福！`)
  }).catch(() => {})
}

// 查看同步历史
const viewSyncHistory = () => {
  syncHistory.value = [
    { time: '2026-03-16 09:00:00', source: 'API', added: 3, updated: 5, status: true, message: '同步成功' },
    { time: '2026-03-15 09:00:00', source: 'API', added: 1, updated: 2, status: true, message: '同步成功' },
    { time: '2026-03-14 09:00:00', source: 'API', added: 0, updated: 1, status: false, message: '连接超时' }
  ]
  syncHistoryVisible.value = true
}

onMounted(() => {
  // 加载配置
})
</script>

<style scoped>
.hr-integration {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.header-actions {
  display: flex;
  gap: 10px;
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

.form-tip {
  font-size: 12px;
  color: #909399;
  margin-top: 5px;
}

.stats-row {
  margin-top: 20px;
}

.stat-card {
  text-align: center;
}

.birthday-stat {
  color: #f56c6c;
}

.birthday-cell,
.hire-date-cell {
  display: flex;
  flex-direction: column;
  gap: 5px;
}

.birthday-badge,
.anniversary-badge {
  font-size: 12px;
  padding: 2px 6px;
  border-radius: 3px;
  background-color: #f0f9ff;
  color: #409EFF;
  font-weight: bold;
}

.anniversary-badge {
  background-color: #fef0f0;
  color: #f56c6c;
}
</style>
