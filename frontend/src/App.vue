<template>
  <router-view v-if="isLoginPage" />
  <el-container v-else class="app-container">
    <el-header class="app-header">
      <div class="header-content">
        <h1>宿舍电费监控</h1>
        <el-menu
          mode="horizontal"
          :default-active="activeMenu"
          router
          class="header-menu"
        >
          <el-menu-item index="/">
            <el-icon><Monitor /></el-icon>
            <span>监控面板</span>
          </el-menu-item>
          <el-menu-item index="/records">
            <el-icon><Document /></el-icon>
            <span>电费记录</span>
          </el-menu-item>
          <el-menu-item index="/alert-logs">
            <el-icon><Bell /></el-icon>
            <span>告警日志</span>
          </el-menu-item>
          <el-menu-item index="/settings">
            <el-icon><Setting /></el-icon>
            <span>系统配置</span>
          </el-menu-item>
        </el-menu>
        <el-button link class="logout-btn" @click="handleLogout">退出</el-button>
      </div>
    </el-header>
    <el-main class="app-main">
      <router-view />
    </el-main>
  </el-container>
</template>

<script setup>
import { computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { Monitor, Document, Bell, Setting } from '@element-plus/icons-vue'
import { clearAuth } from './api/auth'

const route = useRoute()
const router = useRouter()
const activeMenu = computed(() => route.path)
const isLoginPage = computed(() => route.path === '/login')

const handleLogout = () => {
  clearAuth()
  router.replace('/login')
}
</script>

<style>
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
}

.app-container {
  min-height: 100vh;
}

.app-header {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  padding: 0;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.header-content {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 20px;
  height: 100%;
  gap: 12px;
}

.header-content h1 {
  font-size: 20px;
  font-weight: 500;
  margin: 0;
  white-space: nowrap;
}

.header-menu {
  background: transparent;
  border: none;
  flex: 1;
}

.header-menu .el-menu-item {
  color: rgba(255, 255, 255, 0.8);
  border-bottom: 2px solid transparent;
}

.header-menu .el-menu-item:hover,
.header-menu .el-menu-item.is-active {
  color: white;
  background: rgba(255, 255, 255, 0.1);
  border-bottom-color: white;
}

.logout-btn {
  color: white !important;
}

.app-main {
  padding: 24px;
  background: #f5f7fa;
  min-height: calc(100vh - 60px);
}
</style>
