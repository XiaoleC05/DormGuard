<template>
  <div class="dashboard">
    <el-row :gutter="20">
      <el-col :span="24">
        <el-card class="dashboard-card">
          <template #header>
            <div class="card-header">
              <span>当前电费状态</span>
              <el-button type="primary" size="small" @click="refreshData">
                <el-icon><Refresh /></el-icon>
                刷新
              </el-button>
            </div>
          </template>
          <div v-if="loading" class="loading-container">
            <el-skeleton :rows="3" animated />
          </div>
          <div v-else-if="latestRecord" class="status-content">
            <el-descriptions :column="2" border>
              <el-descriptions-item label="宿舍号">{{ latestRecord.dorm_number }}</el-descriptions-item>
              <el-descriptions-item label="当前余额">
                <span :class="balanceClass">{{ latestRecord.balance }} 元</span>
              </el-descriptions-item>
              <el-descriptions-item label="记录时间">
                {{ formatTime(latestRecord.record_time) }}
              </el-descriptions-item>
              <el-descriptions-item label="用电量" v-if="latestRecord.power_consumption">
                {{ latestRecord.power_consumption }} 度
              </el-descriptions-item>
            </el-descriptions>
          </div>
          <el-empty v-else description="暂无数据" />
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="20" style="margin-top: 20px">
      <el-col :span="24">
        <el-card class="dashboard-card">
          <template #header>
            <span>电费趋势</span>
          </template>
          <div v-if="chartLoading" class="loading-container">
            <el-skeleton :rows="5" animated />
          </div>
          <div v-else ref="chartContainer" style="height: 400px"></div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, onMounted, computed, nextTick } from 'vue'
import { ElMessage } from 'element-plus'
import { Refresh } from '@element-plus/icons-vue'
import { getLatestRecord, getRecords } from '../api/power'
import { usePowerStore } from '../stores/power'
import * as echarts from 'echarts'
import dayjs from 'dayjs'

const powerStore = usePowerStore()
const loading = ref(false)
const chartLoading = ref(false)
const latestRecord = ref(null)
const chartContainer = ref(null)
let chartInstance = null

const balanceClass = computed(() => {
  if (!latestRecord.value) return ''
  const balance = latestRecord.value.balance
  if (balance < 10) return 'balance-low'
  if (balance < 20) return 'balance-warning'
  return 'balance-normal'
})

const formatTime = (time) => {
  return dayjs(time).format('YYYY-MM-DD HH:mm:ss')
}

const refreshData = async () => {
  await loadLatestRecord()
  await loadChartData()
}

const loadLatestRecord = async () => {
  loading.value = true
  try {
    // 这里需要从配置或store获取宿舍号
    const dormNumber = powerStore.dormNumber || '101'
    const data = await getLatestRecord(dormNumber)
    latestRecord.value = data
  } catch (error) {
    // 如果是404错误（没有数据），不显示错误提示，只清空数据
    if (error.response?.status === 404) {
      latestRecord.value = null
      console.log('暂无电费记录数据')
    } else {
      ElMessage.error('获取数据失败：' + (error.response?.data?.detail || error.message))
    }
  } finally {
    loading.value = false
  }
}

const loadChartData = async () => {
  chartLoading.value = true
  try {
    const dormNumber = powerStore.dormNumber || '101'
    const records = await getRecords(dormNumber, 30)
    
    await nextTick()
    if (chartContainer.value && records.length > 0) {
      initChart(records)
    } else if (records.length === 0) {
      console.log('暂无图表数据')
    }
  } catch (error) {
    // 如果是404或其他错误，不显示错误提示
    if (error.response?.status !== 404) {
      ElMessage.error('加载图表数据失败：' + (error.response?.data?.detail || error.message))
    }
  } finally {
    chartLoading.value = false
  }
}

const initChart = (records) => {
  if (!chartContainer.value) return
  
  if (!chartInstance) {
    chartInstance = echarts.init(chartContainer.value)
  }
  
  const dates = records.map(r => dayjs(r.record_time).format('MM-DD HH:mm')).reverse()
  const balances = records.map(r => r.balance).reverse()
  
  const option = {
    tooltip: {
      trigger: 'axis',
      formatter: (params) => {
        const param = params[0]
        return `${param.name}<br/>余额: ${param.value} 元`
      }
    },
    xAxis: {
      type: 'category',
      data: dates,
      axisLabel: {
        rotate: 45
      }
    },
    yAxis: {
      type: 'value',
      name: '余额（元）'
    },
    series: [{
      data: balances,
      type: 'line',
      smooth: true,
      areaStyle: {
        color: {
          type: 'linear',
          x: 0,
          y: 0,
          x2: 0,
          y2: 1,
          colorStops: [
            { offset: 0, color: 'rgba(102, 126, 234, 0.3)' },
            { offset: 1, color: 'rgba(102, 126, 234, 0.1)' }
          ]
        }
      },
      lineStyle: {
        color: '#667eea'
      },
      itemStyle: {
        color: '#667eea'
      }
    }]
  }
  
  chartInstance.setOption(option)
  
  // 响应式调整
  window.addEventListener('resize', () => {
    chartInstance?.resize()
  })
}

onMounted(async () => {
  await refreshData()
})
</script>

<style scoped>
.dashboard {
  max-width: 1400px;
  margin: 0 auto;
}

.dashboard-card {
  margin-bottom: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.loading-container {
  padding: 20px;
}

.status-content {
  padding: 10px;
}

.balance-low {
  color: #f56c6c;
  font-weight: bold;
  font-size: 18px;
}

.balance-warning {
  color: #e6a23c;
  font-weight: bold;
  font-size: 18px;
}

.balance-normal {
  color: #67c23a;
  font-weight: bold;
  font-size: 18px;
}
</style>
