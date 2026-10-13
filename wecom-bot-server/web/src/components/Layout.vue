<template>
  <el-container class="layout-container">
    <!-- 侧边栏 -->
    <el-aside width="220px" class="sidebar">
      <div class="logo">
        <el-icon :size="24"><ChatDotRound /></el-icon>
        <span>WeCom Bot</span>
      </div>
      
      <el-menu
        :default-active="activeMenu"
        router
        background-color="#304156"
        text-color="#bfcbd9"
        active-text-color="#409EFF"
        @select="handleMenuSelect"
      >
        <el-menu-item index="/">
          <el-icon><DataAnalysis /></el-icon>
          <span>控制台</span>
        </el-menu-item>
        
        <el-menu-item index="/send-message">
          <el-icon><EditPen /></el-icon>
          <span>发送消息</span>
        </el-menu-item>
        
        <el-menu-item index="/history">
          <el-icon><Document /></el-icon>
          <span>发送历史</span>
        </el-menu-item>
        
        <el-sub-menu index="automation">
          <template #title>
            <el-icon><Timer /></el-icon>
            <span>自动化</span>
          </template>
          <el-menu-item index="/scheduler">
            <el-icon><Clock /></el-icon>
            <span>定时任务</span>
          </el-menu-item>
          <el-menu-item index="/hr-integration">
            <el-icon><UserFilled /></el-icon>
            <span>HR 数据集成</span>
          </el-menu-item>
        </el-sub-menu>
        
        <el-sub-menu index="manage">
          <template #title>
            <el-icon><User /></el-icon>
            <span>管理中心</span>
          </template>
          <el-menu-item index="/users">
            <el-icon><UserFilled /></el-icon>
            <span>用户管理</span>
          </el-menu-item>
          <el-menu-item index="/wecom-config">
            <el-icon><ChatDotSquare /></el-icon>
            <span>企业微信配置</span>
          </el-menu-item>
          <el-menu-item index="/resource-manager">
            <el-icon><Folder /></el-icon>
            <span>资源管理</span>
          </el-menu-item>
        </el-sub-menu>
        
        <el-menu-item index="/settings">
          <el-icon><Setting /></el-icon>
          <span>系统设置</span>
        </el-menu-item>
      </el-menu>
    </el-aside>

    <!-- 主内容区 -->
    <el-container>
      <!-- 顶部导航 -->
      <el-header class="header">
        <div class="header-left">
          <el-breadcrumb separator="/">
            <el-breadcrumb-item @click="navigateTo('/')">首页</el-breadcrumb-item>
            <el-breadcrumb-item>{{ currentTitle }}</el-breadcrumb-item>
          </el-breadcrumb>
        </div>
        
        <div class="header-right">
          <el-tag :type="connectionStatus ? 'success' : 'danger'" size="small">
            <el-icon><Connection /></el-icon>
            {{ connectionStatus ? '已连接' : '未连接' }}
          </el-tag>
          
          <el-dropdown>
            <span class="user-info">
              <el-avatar :size="32" icon="User" />
              <span class="username">{{ username }}</span>
            </span>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item>
                  <el-icon><User /></el-icon>
                  个人信息
                </el-dropdown-item>
                <el-dropdown-item>
                  <el-icon><Setting /></el-icon>
                  系统设置
                </el-dropdown-item>
                <el-dropdown-item divided @click="handleLogout">
                  <el-icon><SwitchButton /></el-icon>
                  退出登录
                </el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </div>
      </el-header>

      <!-- 内容区 -->
      <el-main class="main-content">
        <router-view v-slot="{ Component }">
          <transition name="fade" mode="out-in">
            <component :is="Component" />
          </transition>
        </router-view>
      </el-main>
    </el-container>
  </el-container>
</template>

<script setup>
import { computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAppStore } from '@/stores/app'
import { useUserStore } from '@/stores/user'
import { getWebSocketClient } from '@/utils/websocket'

const route = useRoute()
const router = useRouter()
const appStore = useAppStore()
const userStore = useUserStore()

const activeMenu = computed(() => route.path)
const currentTitle = computed(() => route.meta.title || '页面')
const connectionStatus = computed(() => appStore.isConnected)
const username = computed(() => userStore.username || '管理员')

// 导航到指定页面
const navigateTo = (path) => {
  router.push(path)
}

// 处理菜单选择
const handleMenuSelect = (index) => {
  router.push(index)
}

// 退出登录
const handleLogout = () => {
  // 清除用户信息
  userStore.logout()
  
  // 关闭 WebSocket 连接
  appStore.isConnected = false
  
  // 跳转到登录页
  router.push('/login')
}

// 连接 WebSocket
const connectWebSocket = async () => {
  try {
    const wsClient = getWebSocketClient(appStore.wsUrl)
    
    wsClient.addStatusHandler((isConnected) => {
      appStore.isConnected = isConnected
    })
    
    await wsClient.connect()
  } catch (error) {
    console.error('WebSocket connection failed:', error)
  }
}

// 页面加载时连接 WebSocket
connectWebSocket()
</script>

<style scoped>
.layout-container {
  height: 100vh;
}

.sidebar {
  background-color: #304156;
  color: #fff;
}

.logo {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 60px;
  font-size: 20px;
  font-weight: bold;
  color: #fff;
  gap: 10px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.el-menu {
  border-right: none;
}

.header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  background-color: #fff;
  border-bottom: 1px solid #e6e6e6;
  padding: 0 20px;
}

.header-left {
  flex: 1;
}

.header-right {
  display: flex;
  align-items: center;
  gap: 20px;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
}

.username {
  font-size: 14px;
}

.main-content {
  background-color: #f5f7fa;
  padding: 20px;
}

/* 过渡动画 */
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.2s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style>
