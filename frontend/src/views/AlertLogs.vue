<template>
  <div class="alert-logs-page">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>告警日志</span>
          <el-button type="primary" @click="loadLogs">
            <el-icon><Refresh /></el-icon>
            刷新
          </el-button>
        </div>
      </template>
      
      <div class="table-scroll">
      <el-table :data="logs" v-loading="loading" stripe>
        <el-table-column prop="dorm_number" label="宿舍号" width="100" />
        <el-table-column prop="alert_category" label="类别" width="100">
          <template #default="{ row }">
            <el-tag :type="row.alert_category === 'ac' ? 'warning' : 'success'" size="small">
              {{ row.alert_category === 'ac' ? '空调' : row.alert_category === 'light' ? '照明' : '-' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="balance" label="余量（度）" width="120">
          <template #default="{ row }">
            {{ row.balance.toFixed(2) }}
          </template>
        </el-table-column>
        <el-table-column prop="threshold" label="阈值（度）" width="120">
          <template #default="{ row }">
            {{ row.threshold.toFixed(2) }}
          </template>
        </el-table-column>
        <el-table-column prop="alert_type" label="告警类型" width="100">
          <template #default="{ row }">
            <el-tag type="success" size="small">
              {{ row.alert_type === 'email' ? '邮件(历史)' : 'QQ' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="alert_status" label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="row.alert_status === 'success' ? 'success' : 'danger'" size="small">
              {{ row.alert_status === 'success' ? '成功' : '失败' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="alert_message" label="消息" show-overflow-tooltip />
        <el-table-column prop="created_at" label="时间" width="180">
          <template #default="{ row }">
            {{ formatTime(row.created_at) }}
          </template>
        </el-table-column>
      </el-table>
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { Refresh } from '@element-plus/icons-vue'
import { getAlertLogs } from '../api/alert'
import { formatApiError } from '../utils/apiError'
import dayjs from 'dayjs'

const loading = ref(false)
const logs = ref([])

const formatTime = (time) => {
  return dayjs(time).format('YYYY-MM-DD HH:mm:ss')
}

const loadLogs = async () => {
  loading.value = true
  try {
    const data = await getAlertLogs(null, 100)
    logs.value = data
  } catch (error) {
    ElMessage.error('加载日志失败：' + formatApiError(error))
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  loadLogs()
})
</script>

<style scoped>
.alert-logs-page {
  max-width: 1400px;
  margin: 0 auto;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 12px;
  flex-wrap: wrap;
}

@media (max-width: 768px) {
  .alert-logs-page {
    max-width: none;
  }

  .card-header .el-button {
    width: 100%;
  }
}
</style>
