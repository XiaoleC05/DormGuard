<template>
  <div class="settings-page">
    <div class="page-header">
      <h2>系统配置</h2>
      <el-button type="primary" :loading="saving" @click="saveSettings">保存配置</el-button>
    </div>

    <el-alert
      title="保存后需重启后端服务才能完全生效（GitHub Actions 部署会自动重启）"
      type="info"
      show-icon
      :closable="false"
      class="tip"
    />

    <el-card shadow="hover">
      <template #header>爬虫与宿舍</template>
      <el-form label-width="160px">
        <el-form-item label="宿舍号">
          <el-input v-model="form.CRAWLER_DORM_NUMBER" />
        </el-form-item>
        <el-form-item label="房间 ID (room_id)">
          <el-input v-model="form.CRAWLER_ROOM_ID" />
        </el-form-item>
        <el-form-item label="OpenID">
          <el-input v-model="form.CRAWLER_OPENID" type="password" show-password />
        </el-form-item>
        <el-form-item label="JSESSIONID">
          <el-input v-model="form.CRAWLER_JSESSIONID" type="password" show-password />
        </el-form-item>
        <el-form-item label="Token">
          <el-input v-model="form.CRAWLER_TOKEN" type="password" show-password />
        </el-form-item>
      </el-form>
    </el-card>

    <el-card shadow="hover" class="section">
      <template #header>调度与告警</template>
      <el-form label-width="160px">
        <el-form-item label="爬虫间隔(小时)">
          <el-input-number v-model="schedulerHours" :min="1" :max="24" />
        </el-form-item>
        <el-form-item label="告警冷却(小时)">
          <el-input-number v-model="alertCooldownHours" :min="1" :max="24" />
        </el-form-item>
        <el-form-item label="QQ告警暂停至">
          <el-input v-model="form.QQ_ALERT_PAUSE_UNTIL" placeholder="YYYY-MM-DD，留空不暂停" />
        </el-form-item>
      </el-form>
    </el-card>

    <el-card shadow="hover" class="section">
      <template #header>邮件通知</template>
      <el-form label-width="160px">
        <el-form-item label="启用邮件">
          <el-switch v-model="emailEnabled" />
        </el-form-item>
        <el-form-item label="SMTP 主机">
          <el-input v-model="form.EMAIL_SMTP_HOST" />
        </el-form-item>
        <el-form-item label="SMTP 端口">
          <el-input v-model="form.EMAIL_SMTP_PORT" />
        </el-form-item>
        <el-form-item label="SMTP 用户">
          <el-input v-model="form.EMAIL_SMTP_USER" />
        </el-form-item>
        <el-form-item label="SMTP 密码">
          <el-input v-model="form.EMAIL_SMTP_PASSWORD" type="password" show-password />
        </el-form-item>
        <el-form-item label="发件人">
          <el-input v-model="form.EMAIL_FROM" />
        </el-form-item>
        <el-form-item label="收件人">
          <el-input v-model="form.EMAIL_TO" />
        </el-form-item>
      </el-form>
    </el-card>

    <el-card shadow="hover" class="section">
      <template #header>QQ 机器人</template>
      <el-form label-width="160px">
        <el-form-item label="启用 QQ 机器人">
          <el-switch v-model="qqBotEnabled" />
        </el-form-item>
        <el-form-item label="API 地址">
          <el-input v-model="form.QQ_BOT_API_URL" />
        </el-form-item>
        <el-form-item label="群号">
          <el-input v-model="form.QQ_BOT_GROUP_ID" />
        </el-form-item>
        <el-form-item label="用户 QQ">
          <el-input v-model="form.QQ_BOT_USER_ID" />
        </el-form-item>
        <el-form-item label="Access Token">
          <el-input v-model="form.QQ_BOT_ACCESS_TOKEN" type="password" show-password />
        </el-form-item>
      </el-form>
    </el-card>
  </div>
</template>

<script setup>
import { onMounted, reactive, ref } from 'vue'
import { ElMessage } from 'element-plus'
import { getSettings, updateSettings } from '../api/admin'

const saving = ref(false)
const form = reactive({
  CRAWLER_DORM_NUMBER: '',
  CRAWLER_ROOM_ID: '',
  CRAWLER_OPENID: '',
  CRAWLER_JSESSIONID: '',
  CRAWLER_TOKEN: '',
  SCHEDULER_INTERVAL_HOURS: '2',
  ALERT_COOLDOWN_HOURS: '2',
  QQ_ALERT_PAUSE_UNTIL: '',
  EMAIL_ENABLED: 'false',
  EMAIL_SMTP_HOST: '',
  EMAIL_SMTP_PORT: '587',
  EMAIL_SMTP_USER: '',
  EMAIL_SMTP_PASSWORD: '',
  EMAIL_FROM: '',
  EMAIL_TO: '',
  QQ_BOT_ENABLED: 'false',
  QQ_BOT_API_URL: 'http://127.0.0.1:8080',
  QQ_BOT_GROUP_ID: '',
  QQ_BOT_USER_ID: '',
  QQ_BOT_ACCESS_TOKEN: ''
})

const schedulerHours = ref(2)
const alertCooldownHours = ref(2)
const emailEnabled = ref(false)
const qqBotEnabled = ref(false)

const loadSettings = async () => {
  const data = await getSettings()
  Object.assign(form, data.settings)
  schedulerHours.value = Number(form.SCHEDULER_INTERVAL_HOURS || 2)
  alertCooldownHours.value = Number(form.ALERT_COOLDOWN_HOURS || 2)
  emailEnabled.value = String(form.EMAIL_ENABLED).toLowerCase() === 'true'
  qqBotEnabled.value = String(form.QQ_BOT_ENABLED).toLowerCase() === 'true'
}

const saveSettings = async () => {
  saving.value = true
  try {
    await updateSettings({
      ...form,
      SCHEDULER_INTERVAL_HOURS: String(schedulerHours.value),
      ALERT_COOLDOWN_HOURS: String(alertCooldownHours.value),
      EMAIL_ENABLED: emailEnabled.value ? 'true' : 'false',
      QQ_BOT_ENABLED: qqBotEnabled.value ? 'true' : 'false'
    })
    ElMessage.success('配置已保存，请等待后端重启后生效')
    await loadSettings()
  } catch (error) {
    ElMessage.error(error.response?.data?.detail || '保存失败')
  } finally {
    saving.value = false
  }
}

onMounted(loadSettings)
</script>

<style scoped>
.settings-page {
  max-width: 900px;
  margin: 0 auto;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.tip {
  margin-bottom: 16px;
}

.section {
  margin-top: 16px;
}
</style>
