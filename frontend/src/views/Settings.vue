<template>
  <div class="settings-page">
    <div class="page-header">
      <h2>系统配置</h2>
      <el-button type="primary" :loading="saving" @click="saveSettings">保存配置</el-button>
    </div>

    <el-alert
      title="保存后系统将尝试自动重启相关服务；若重启失败会提示手动处理"
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
          <div class="field-hint">西华一卡通微信 OpenID，用于获取会话</div>
        </el-form-item>
        <el-form-item label="JSESSIONID">
          <el-input v-model="form.CRAWLER_JSESSIONID" type="password" show-password />
          <div class="field-hint">爬虫登录凭证，过期后系统会尝试用 OpenID 自动刷新</div>
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
          <el-date-picker
            v-model="qqAlertPauseUntil"
            type="date"
            placeholder="选择日期，留空表示不暂停"
            format="YYYY-MM-DD"
            value-format="YYYY-MM-DD"
            clearable
            style="width: 100%"
          />
          <div class="field-hint">所选日期之前不发送 QQ 自动告警，到达当日恢复</div>
        </el-form-item>
      </el-form>
    </el-card>

    <el-card shadow="hover" class="section">
      <template #header>QQ 机器人</template>
      <el-form label-width="160px">
        <el-form-item label="机器人 QQ">
          <el-input model-value="1270667498" disabled />
        </el-form-item>
        <el-form-item label="启用 QQ 机器人">
          <el-switch v-model="qqBotEnabled" />
        </el-form-item>
        <el-form-item label="API 地址">
          <el-input v-model="form.QQ_BOT_API_URL" disabled />
          <div class="field-hint">
            本机 NoneBot HTTP 服务，后端通过此地址调用
            <code>/api/send_group_msg</code> 与 <code>/api/get_status</code>
          </div>
        </el-form-item>
        <el-form-item label="告警群号">
          <el-input v-model="form.QQ_BOT_GROUP_ID" placeholder="消息仅发送到此群" />
        </el-form-item>
      </el-form>
    </el-card>
  </div>
</template>

<script setup>
import { onMounted, reactive, ref } from 'vue'
import { ElMessage } from 'element-plus'
import { getSettings, updateSettings } from '../api/admin'
import { formatApiError } from '../utils/apiError'

const saving = ref(false)
const form = reactive({
  CRAWLER_DORM_NUMBER: '',
  CRAWLER_ROOM_ID: '',
  CRAWLER_OPENID: '',
  CRAWLER_JSESSIONID: '',
  SCHEDULER_INTERVAL_HOURS: '2',
  ALERT_COOLDOWN_HOURS: '2',
  QQ_ALERT_PAUSE_UNTIL: '',
  QQ_BOT_ENABLED: 'false',
  QQ_BOT_API_URL: 'http://127.0.0.1:8080',
  QQ_BOT_GROUP_ID: '6011223303'
})

const schedulerHours = ref(2)
const alertCooldownHours = ref(2)
const qqAlertPauseUntil = ref('')
const qqBotEnabled = ref(false)

const loadSettings = async () => {
  const data = await getSettings()
  Object.assign(form, data.settings)
  schedulerHours.value = Number(form.SCHEDULER_INTERVAL_HOURS || 2)
  alertCooldownHours.value = Number(form.ALERT_COOLDOWN_HOURS || 2)
  qqAlertPauseUntil.value = form.QQ_ALERT_PAUSE_UNTIL || ''
  qqBotEnabled.value = String(form.QQ_BOT_ENABLED).toLowerCase() === 'true'
  if (!form.QQ_BOT_API_URL) {
    form.QQ_BOT_API_URL = 'http://127.0.0.1:8080'
  }
}

const saveSettings = async () => {
  saving.value = true
  try {
    const data = await updateSettings({
      ...form,
      SCHEDULER_INTERVAL_HOURS: String(schedulerHours.value),
      ALERT_COOLDOWN_HOURS: String(alertCooldownHours.value),
      QQ_ALERT_PAUSE_UNTIL: qqAlertPauseUntil.value || '',
      QQ_BOT_ENABLED: qqBotEnabled.value ? 'true' : 'false'
    })
    if (data.restart_required) {
      ElMessage.warning('配置已保存，但服务重启失败，请手动执行 systemctl restart dorm-backend')
    } else {
      ElMessage.success('配置已保存，相关服务已重启')
    }
    await loadSettings()
  } catch (error) {
    ElMessage.error(formatApiError(error, '保存失败'))
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

.field-hint {
  font-size: 12px;
  color: #909399;
  margin-top: 5px;
  line-height: 1.5;
}

.field-hint code {
  font-size: 11px;
  background: #f4f4f5;
  padding: 1px 4px;
  border-radius: 3px;
}
</style>
