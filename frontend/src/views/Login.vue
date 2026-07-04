<template>
  <div class="login-page">
    <el-card class="login-card" shadow="hover">
      <h2>奥泽莉亚工具箱</h2>
      <p class="subtitle">oxelia51.com · 宿舍电费监控</p>
      <el-form @submit.prevent="handleLogin">
        <el-form-item label="用户名">
          <el-input v-model="username" autocomplete="username" />
        </el-form-item>
        <el-form-item label="密码">
          <el-input
            v-model="password"
            type="password"
            show-password
            autocomplete="current-password"
            @keyup.enter="handleLogin"
          />
        </el-form-item>
        <el-button type="primary" class="login-btn" :loading="loading" @click="handleLogin">
          登录
        </el-button>
      </el-form>
    </el-card>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { login, setAuth } from '../api/auth'

const router = useRouter()
const username = ref('root')
const password = ref('')
const loading = ref(false)

const handleLogin = async () => {
  if (!username.value || !password.value) {
    ElMessage.warning('请输入用户名和密码')
    return
  }
  loading.value = true
  try {
    const data = await login(username.value, password.value)
    setAuth(data.access_token, data.username)
    ElMessage.success('登录成功')
    router.replace('/')
  } catch (error) {
    const msg = error.response?.data?.detail || '登录失败'
    ElMessage.error(msg)
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.login-page {
  min-height: 100vh;
  min-height: 100dvh;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 16px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.login-card {
  width: min(380px, 100%);
  padding: 8px;
}

h2 {
  margin: 0;
  text-align: center;
}

.subtitle {
  text-align: center;
  color: #909399;
  margin: 8px 0 20px;
}

.login-btn {
  width: 100%;
}
</style>
