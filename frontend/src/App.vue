<template>
  <el-config-provider :locale="zhCn">
  <router-view v-if="isLoginPage" />
  <el-container v-else class="app-container">
    <el-header class="app-header">
      <div class="header-content">
        <div class="header-brand">
          <el-button
            v-if="isMobile"
            class="menu-toggle"
            link
            @click="drawerVisible = true"
          >
            <el-icon :size="22"><Menu /></el-icon>
          </el-button>
          <h1 class="brand-title">奥泽莉亚工具箱</h1>
        </div>

        <el-menu
          v-if="!isMobile"
          mode="horizontal"
          :default-active="activeMenu"
          router
          class="header-menu"
        >
          <el-menu-item v-for="item in navItems" :key="item.index" :index="item.index">
            <el-icon><component :is="item.icon" /></el-icon>
            <span>{{ item.label }}</span>
          </el-menu-item>
        </el-menu>

        <el-button link class="logout-btn" @click="handleLogout">退出</el-button>
      </div>
    </el-header>

    <el-drawer
      v-model="drawerVisible"
      direction="ltr"
      size="78%"
      title="导航菜单"
      class="mobile-nav-drawer"
    >
      <el-menu
        :default-active="activeMenu"
        router
        @select="drawerVisible = false"
      >
        <el-menu-item v-for="item in navItems" :key="item.index" :index="item.index">
          <el-icon><component :is="item.icon" /></el-icon>
          <span>{{ item.label }}</span>
        </el-menu-item>
      </el-menu>
    </el-drawer>

    <el-main class="app-main">
      <router-view />
    </el-main>
  </el-container>
  </el-config-provider>
</template>

<script setup>
import { computed, onMounted, onUnmounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import zhCn from 'element-plus/dist/locale/zh-cn.mjs'
import { Monitor, Document, Bell, Setting, Menu } from '@element-plus/icons-vue'
import { clearAuth } from './api/auth'

const route = useRoute()
const router = useRouter()
const activeMenu = computed(() => route.path)
const isLoginPage = computed(() => route.path === '/login')
const drawerVisible = ref(false)
const isMobile = ref(false)

const navItems = [
  { index: '/', label: '监控面板', icon: Monitor },
  { index: '/records', label: '电费记录', icon: Document },
  { index: '/alert-logs', label: '告警日志', icon: Bell },
  { index: '/settings', label: '系统配置', icon: Setting },
]

const updateLayout = () => {
  isMobile.value = window.innerWidth < 768
  if (!isMobile.value) {
    drawerVisible.value = false
  }
}

onMounted(() => {
  updateLayout()
  window.addEventListener('resize', updateLayout)
})

onUnmounted(() => {
  window.removeEventListener('resize', updateLayout)
})

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
  height: auto !important;
  min-height: 56px;
}

.header-content {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 16px;
  min-height: 56px;
  gap: 8px;
}

.header-brand {
  display: flex;
  align-items: center;
  gap: 4px;
  min-width: 0;
  flex-shrink: 0;
}

.brand-title {
  font-size: 18px;
  font-weight: 600;
  margin: 0;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.menu-toggle {
  color: white !important;
  padding: 4px;
}

.header-menu {
  background: transparent;
  border: none;
  flex: 1;
  min-width: 0;
  justify-content: center;
}

.header-menu .el-menu-item {
  color: rgba(255, 255, 255, 0.85);
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
  flex-shrink: 0;
  padding: 8px 4px;
}

.app-main {
  padding: 24px;
  background: #f5f7fa;
  min-height: calc(100vh - 56px);
}

.mobile-nav-drawer .el-drawer__header {
  margin-bottom: 0;
  padding-bottom: 12px;
}

@media (max-width: 768px) {
  .header-content {
    padding: 0 12px;
  }

  .brand-title {
    font-size: 16px;
    max-width: 42vw;
  }
}

@media (max-width: 380px) {
  .brand-title {
    font-size: 15px;
    max-width: 38vw;
  }
}
</style>
