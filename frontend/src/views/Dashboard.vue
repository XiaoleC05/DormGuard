<template>
  <div class="dashboard">
    <!-- 页面标题 -->
    <div class="page-header">
      <h2 class="page-title">
        <el-icon class="title-icon"><Monitor /></el-icon>
        监控面板
      </h2>
      <div class="page-actions">
        <el-button type="primary" plain size="default" @click="handleSendReport" :loading="reportSending">
          发送QQ报告
        </el-button>
        <el-button type="success" size="default" @click="reloadData" :loading="reloading" :icon="Refresh">
          重新获取
        </el-button>
      </div>
    </div>

    <el-alert
      v-if="configMissing"
      title="未配置宿舍号，请前往「系统配置」填写宿舍号（CRAWLER_DORM_NUMBER）"
      type="warning"
      show-icon
      :closable="false"
      class="config-tip"
    />

    <!-- 宿舍信息卡片 -->
    <el-card class="dorm-card" shadow="hover" v-loading="loading">
      <template #header>
        <div class="dorm-header">
          <div class="header-left">
            <div class="dorm-number">
              <el-icon class="dorm-icon"><HomeFilled /></el-icon>
              <span class="dorm-number-text">{{ dormNumber || '未配置' }}</span>
            </div>
            <el-tag 
              :type="getDormStatusType(latestRecord)" 
              size="default"
              class="status-tag"
            >
              {{ getDormStatusText(latestRecord) }}
            </el-tag>
          </div>
        </div>
      </template>
      <div class="dorm-content">
        <!-- 有数据时显示 -->
        <template v-if="latestRecord && latestRecord.record_time">
          <el-row :gutter="20">
            <el-col :xs="24" :sm="12" v-if="latestRecord.kbalance !== null && latestRecord.kbalance !== undefined">
              <div class="balance-card balance-card-ac">
                <div class="balance-card-header">
                  <el-icon class="balance-icon"><WindPower /></el-icon>
                  <span class="balance-label">空调余量</span>
                </div>
                <div :class="['balance-value', getBalanceClass(latestRecord.kbalance, alertRule?.kthreshold)]">
                  {{ latestRecord.kbalance.toFixed(2) }}
                  <span class="balance-unit">度</span>
                </div>
              </div>
            </el-col>
            <el-col :xs="24" :sm="12" v-if="latestRecord.zbalance !== null && latestRecord.zbalance !== undefined">
              <div class="balance-card balance-card-light">
                <div class="balance-card-header">
                  <el-icon class="balance-icon"><Sunny /></el-icon>
                  <span class="balance-label">照明余量</span>
                </div>
                <div :class="['balance-value', getBalanceClass(latestRecord.zbalance, alertRule?.zthreshold)]">
                  {{ latestRecord.zbalance.toFixed(2) }}
                  <span class="balance-unit">度</span>
                </div>
              </div>
            </el-col>
            <el-col :xs="24" :sm="12" v-if="latestRecord.kbalance === null && latestRecord.kbalance === undefined && latestRecord.balance !== null">
              <div class="balance-card balance-card-ac">
                <div class="balance-card-header">
                  <el-icon class="balance-icon"><WindPower /></el-icon>
                  <span class="balance-label">电费余量</span>
                </div>
                <div :class="['balance-value', getBalanceClass(latestRecord.balance, alertRule?.threshold || alertRule?.kthreshold || alertRule?.zthreshold)]">
                  {{ latestRecord.balance.toFixed(2) }}
                  <span class="balance-unit">度</span>
                </div>
              </div>
            </el-col>
          </el-row>
          <div class="dorm-time">
            <el-icon><Clock /></el-icon>
            <span>最后更新：{{ formatTime(latestRecord.record_time) }}</span>
          </div>
        </template>
        <!-- 无数据时显示提示 -->
        <template v-else>
          <div class="dorm-no-data">
            <el-empty 
              :description="!alertRule || !alertRule.room_id ? '需配置room_id' : '暂无数据'" 
              :image-size="80"
            />
          </div>
        </template>
      </div>
    </el-card>

    <!-- 告警规则配置 -->
    <el-card class="alert-rule-card" shadow="hover">
      <template #header>
        <div class="card-header">
          <div class="header-title">
            <el-icon class="title-icon"><Setting /></el-icon>
            <span>告警规则配置</span>
          </div>
          <el-button 
            v-if="!alertRule" 
            type="primary" 
            size="default" 
            @click="showRuleDialog = true"
            :icon="Plus"
          >
            创建规则
          </el-button>
        </div>
      </template>
      <div v-if="alertRule" class="alert-rule-content">
        <el-descriptions :column="descColumns" border>
          <el-descriptions-item label="房间ID（room_id）">
            {{ alertRule.room_id || '未配置' }}
          </el-descriptions-item>
          <el-descriptions-item label="启用状态">
            <el-tag :type="alertRule.enabled ? 'success' : 'info'">
              {{ alertRule.enabled ? '启用' : '禁用' }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="空调告警阈值（度）">
            {{ alertRule.kthreshold !== null && alertRule.kthreshold !== undefined ? alertRule.kthreshold.toFixed(2) : '未设置' }}
          </el-descriptions-item>
          <el-descriptions-item label="照明告警阈值（度）">
            {{ alertRule.zthreshold !== null && alertRule.zthreshold !== undefined ? alertRule.zthreshold.toFixed(2) : '未设置' }}
          </el-descriptions-item>
          <el-descriptions-item label="QQ告警">
            <el-tag :type="alertRule.qq_enabled ? 'success' : 'info'">
              {{ alertRule.qq_enabled ? '启用' : '禁用' }}
            </el-tag>
            <span v-if="alertRule.qq_enabled && qqGroupId" style="margin-left: 8px; font-size: 12px; color: #909399;">
              群 {{ qqGroupId }}
            </span>
          </el-descriptions-item>
          <el-descriptions-item label="机器人QQ">
            <span>1270667498</span>
          </el-descriptions-item>
          <el-descriptions-item label="QQ机器人状态" :span="descColumns">
            <el-tag :type="qqStatusTagType">{{ qqStatusText }}</el-tag>
            <el-button link type="primary" style="margin-left: 8px" :loading="qqStatusLoading" @click="loadQQStatus">
              刷新
            </el-button>
          </el-descriptions-item>
        </el-descriptions>
        <div class="rule-actions">
          <el-button type="primary" @click="editRule">编辑规则</el-button>
        </div>
      </div>
      <div v-else class="alert-rule-empty">
        <el-empty description="未配置告警规则" :image-size="80">
          <el-button type="primary" @click="showRuleDialog = true">创建规则</el-button>
        </el-empty>
      </div>
    </el-card>

    <!-- 趋势图表 -->
    <el-card class="chart-card" shadow="hover">
      <template #header>
        <div class="card-header">
          <div class="header-title">
            <el-icon class="title-icon"><TrendCharts /></el-icon>
            <span>电费趋势</span>
          </div>
          <div class="chart-controls">
            <el-radio-group v-model="chartViewMode" size="small" @change="onChartViewModeChange">
              <el-radio-button value="monthly">按月</el-radio-button>
              <el-radio-button value="daily">按日</el-radio-button>
            </el-radio-group>
            <el-date-picker
              v-if="chartViewMode === 'daily'"
              v-model="selectedMonth"
              type="month"
              placeholder="选择月份"
              format="YYYY年MM月"
              value-format="YYYY-MM"
              size="small"
              style="margin-left: 10px;"
              @change="onSelectedMonthChange"
            />
          </div>
        </div>
      </template>
      <div v-if="chartLoading" class="loading-container">
        <el-skeleton :rows="5" animated />
      </div>
      <div v-show="!chartLoading && hasChartData" ref="chartContainer" class="chart-container"></div>
      <el-empty v-if="!chartLoading && !hasChartData" description="暂无图表数据" :image-size="100" />
    </el-card>

    <!-- 告警规则编辑对话框 -->
    <el-dialog
      v-model="showRuleDialog"
      :title="alertRule ? '编辑告警规则' : '创建告警规则'"
      width="600px"
    >
      <el-form :model="ruleForm" label-width="140px" :rules="formRules" ref="formRef">
        <el-form-item label="宿舍号">
          <el-input v-model="ruleForm.dorm_number" disabled />
        </el-form-item>
        <el-form-item label="房间ID（room_id）">
          <el-input 
            v-model="ruleForm.room_id" 
            placeholder="请输入房间ID（通过抓包获取，如：5699）"
          />
          <div style="font-size: 12px; color: #909399; margin-top: 5px;">
            用于查询电费数据，需要通过抓包工具获取
          </div>
        </el-form-item>
        <el-form-item label="空调告警阈值（度）">
          <el-input-number v-model="ruleForm.kthreshold" :min="0" :precision="2" style="width: 100%" />
          <div style="font-size: 12px; color: #909399; margin-top: 5px;">
            当空调余量低于此值时触发告警
          </div>
        </el-form-item>
        <el-form-item label="照明告警阈值（度）">
          <el-input-number v-model="ruleForm.zthreshold" :min="0" :precision="2" style="width: 100%" />
          <div style="font-size: 12px; color: #909399; margin-top: 5px;">
            当照明余量低于此值时触发告警
          </div>
        </el-form-item>
        <el-form-item label="启用状态">
          <el-switch v-model="ruleForm.enabled" />
        </el-form-item>
        <el-form-item label="QQ告警">
          <el-switch v-model="ruleForm.qq_enabled" />
          <div v-if="ruleForm.qq_enabled" style="font-size: 12px; color: #909399; margin-top: 5px;">
            启用后消息发送至系统配置中的告警群（当前：{{ qqGroupId || '未配置' }}）
          </div>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showRuleDialog = false">取消</el-button>
        <el-button type="primary" @click="saveRule">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted, nextTick, onUnmounted } from 'vue'
import { ElMessage } from 'element-plus'
import { 
  Refresh, 
  WindPower, 
  Sunny, 
  Clock, 
  TrendCharts,
  Setting,
  Monitor,
  HomeFilled,
  Plus
} from '@element-plus/icons-vue'
import { getLatestRecord, getRecords, getRecordsByRange } from '../api/power'
import { manualCrawl, getConfig, checkQQStatus, sendPowerReport, getQQConfig } from '../api/system'
import { getCurrentAlertRule, createAlertRule, updateCurrentAlertRule } from '../api/alert'
import { formatApiError } from '../utils/apiError'
import * as echarts from 'echarts/core'
import { LineChart } from 'echarts/charts'
import { GridComponent, TooltipComponent, LegendComponent } from 'echarts/components'
import { CanvasRenderer } from 'echarts/renderers'

echarts.use([LineChart, GridComponent, TooltipComponent, LegendComponent, CanvasRenderer])
import dayjs from 'dayjs'

const loading = ref(false)
const chartLoading = ref(false)
const reloading = ref(false)
const reportSending = ref(false)
const qqStatusLoading = ref(false)
const configMissing = ref(false)
const qqStatusText = ref('未检查')
const qqStatusTagType = ref('info')
const qqGroupId = ref('')
const latestRecord = ref(null)
const alertRule = ref(null)
const dormNumber = ref(null)
const chartContainer = ref(null)
const chartViewMode = ref('monthly') // 'monthly' 或 'daily'
const selectedMonth = ref(dayjs().format('YYYY-MM'))
let chartInstance = null
let resizeHandler = null
const descColumns = ref(typeof window !== 'undefined' && window.innerWidth < 768 ? 1 : 2)

const DEFAULT_THRESHOLD = 20

const resolveThreshold = (category) => {
  if (!alertRule.value) return DEFAULT_THRESHOLD
  if (category === 'ac') {
    return alertRule.value.kthreshold ?? DEFAULT_THRESHOLD
  }
  return alertRule.value.zthreshold ?? DEFAULT_THRESHOLD
}

const getBalanceClass = (balance, threshold = null) => {
  if (balance === null || balance === undefined) return ''
  
  // 如果提供了阈值，使用阈值来判断
  if (threshold !== null && threshold !== undefined) {
    if (balance < threshold) return 'balance-low'
    if (balance < threshold * 1.5) return 'balance-warning' // 阈值到1.5倍阈值之间显示警告
    return 'balance-normal'
  }
  
  // 如果没有阈值，使用规则默认值
  if (balance < DEFAULT_THRESHOLD) return 'balance-low'
  if (balance < DEFAULT_THRESHOLD * 1.5) return 'balance-warning'
  return 'balance-normal'
}

const formatTime = (time) => {
  return dayjs(time).format('YYYY-MM-DD HH:mm:ss')
}

const reloadData = async () => {
  reloading.value = true
  try {
    const response = await manualCrawl()
    if (response.success) {
      ElMessage.success(response.message || '数据获取成功')
      setTimeout(async () => {
        await loadDormRecord()
        await loadAlertRule()
        await loadChartData()
      }, 1000)
    } else {
      ElMessage.error(response.message || '数据获取失败')
    }
  } catch (error) {
    ElMessage.error('重新获取数据失败：' + formatApiError(error, '请求失败'))
  } finally {
    reloading.value = false
  }
}

const loadDormRecord = async () => {
  if (!dormNumber.value) return
  
  loading.value = true
  try {
    const record = await getLatestRecord(dormNumber.value)
    latestRecord.value = record
  } catch (error) {
    if (error.response?.status === 404) {
      latestRecord.value = null
    } else {
      ElMessage.error('获取数据失败：' + (error.response?.data?.detail || error.message))
    }
  } finally {
    loading.value = false
  }
}

const loadAlertRule = async () => {
  try {
    const rule = await getCurrentAlertRule()
    alertRule.value = rule || null
  } catch (error) {
    if (error.response?.status === 404 || error.response?.status === 204) {
      alertRule.value = null
    } else if (error.response?.status === 400) {
      alertRule.value = null
      ElMessage.warning(formatApiError(error, '获取告警规则失败，请先在系统配置中填写宿舍号'))
    } else {
      console.error('获取告警规则失败：', error)
      alertRule.value = null
    }
  }
}

const loadQQStatus = async () => {
  qqStatusLoading.value = true
  try {
    const status = await checkQQStatus()
    if (status.success) {
      qqStatusText.value = `已连接${status.bot_id ? `（Bot ${status.bot_id}）` : ''}`
      qqStatusTagType.value = 'success'
    } else {
      qqStatusText.value = status.message || '未连接'
      qqStatusTagType.value = 'danger'
    }
  } catch (error) {
    qqStatusText.value = formatApiError(error, '检查失败')
    qqStatusTagType.value = 'danger'
  } finally {
    qqStatusLoading.value = false
  }
}

const handleSendReport = async () => {
  reportSending.value = true
  try {
    const result = await sendPowerReport()
    if (result.success) {
      ElMessage.success(result.message || '报告已发送')
    } else {
      ElMessage.error(result.message || '发送失败')
    }
  } catch (error) {
    ElMessage.error(formatApiError(error, '发送报告失败'))
  } finally {
    reportSending.value = false
  }
}

const getDormStatusType = (record) => {
  if (!record || !record.record_time) return 'info'
  const kbalance = record.kbalance !== null && record.kbalance !== undefined ? record.kbalance : record.balance
  const zbalance = record.zbalance
  const kTh = resolveThreshold('ac')
  const zTh = resolveThreshold('light')
  const values = []
  if (kbalance !== null && kbalance !== undefined) values.push({ balance: kbalance, threshold: kTh })
  if (zbalance !== null && zbalance !== undefined) values.push({ balance: zbalance, threshold: zTh })
  if (values.some(v => v.balance < v.threshold)) return 'danger'
  if (values.some(v => v.balance < v.threshold * 1.5)) return 'warning'
  return 'success'
}

const getDormStatusText = (record) => {
  if (!record || !record.record_time) {
    if (!alertRule.value || !alertRule.value.room_id) return '需配置room_id'
    return '无数据'
  }
  const kbalance = record.kbalance !== null && record.kbalance !== undefined ? record.kbalance : record.balance
  const zbalance = record.zbalance
  const kTh = resolveThreshold('ac')
  const zTh = resolveThreshold('light')
  const low = (kbalance !== null && kbalance !== undefined && kbalance < kTh)
    || (zbalance !== null && zbalance !== undefined && zbalance < zTh)
  const warn = !low && (
    (kbalance !== null && kbalance !== undefined && kbalance < kTh * 1.5)
    || (zbalance !== null && zbalance !== undefined && zbalance < zTh * 1.5)
  )
  if (low) return '低电量'
  if (warn) return '警告'
  return '正常'
}

// 告警规则编辑相关
const showRuleDialog = ref(false)
const formRef = ref(null)
const ruleForm = ref({
  dorm_number: '',
  room_id: '',
  kthreshold: 20.0,
  zthreshold: 20.0,
  enabled: true,
  qq_enabled: false
})

const formRules = {}

const loadQQConfig = async () => {
  try {
    const cfg = await getQQConfig()
    qqGroupId.value = cfg.group_id || ''
  } catch {
    qqGroupId.value = ''
  }
}

const editRule = () => {
  if (!alertRule.value) {
    showRuleDialog.value = true
    return
  }
  
  ruleForm.value = {
    dorm_number: alertRule.value.dorm_number || dormNumber.value,
    room_id: alertRule.value.room_id || '',
    kthreshold: alertRule.value.kthreshold !== null && alertRule.value.kthreshold !== undefined ? alertRule.value.kthreshold : 20.0,
    zthreshold: alertRule.value.zthreshold !== null && alertRule.value.zthreshold !== undefined ? alertRule.value.zthreshold : 20.0,
    enabled: alertRule.value.enabled !== null && alertRule.value.enabled !== undefined ? alertRule.value.enabled : true,
    qq_enabled: alertRule.value.qq_enabled !== null && alertRule.value.qq_enabled !== undefined ? alertRule.value.qq_enabled : false
  }
  showRuleDialog.value = true
}

const saveRule = async () => {
  if (!formRef.value) return
  
  try {
    await formRef.value.validate()
    
    const submitData = {
      ...ruleForm.value,
      room_id: ruleForm.value.room_id && ruleForm.value.room_id.trim() ? ruleForm.value.room_id.trim() : null
    }
    
    if (alertRule.value) {
      await updateCurrentAlertRule(submitData)
      ElMessage.success('更新成功')
    } else {
      await createAlertRule(submitData)
      ElMessage.success('创建成功')
    }
    showRuleDialog.value = false
    await loadAlertRule()
    await loadDormRecord()
  } catch (error) {
    if (error !== false) {
      ElMessage.error('保存失败：' + formatApiError(error, '未知错误'))
    }
  }
}

// 图表相关
const hasChartData = ref(false)

const buildBalanceTrendPoints = (records, mode) => {
  const sorted = [...records].sort(
    (a, b) => new Date(a.record_time).getTime() - new Date(b.record_time).getTime()
  )
  const buckets = {}
  for (const record of sorted) {
    const monthKey = dayjs(record.record_time).format('YYYY-MM')
    const dayKey = dayjs(record.record_time).format('YYYY-MM-DD')
    if (mode === 'daily' && monthKey !== selectedMonth.value) continue
    const key = mode === 'monthly' ? monthKey : dayKey
    buckets[key] = record
  }
  return Object.keys(buckets)
    .sort()
    .map((key) => {
      const record = buckets[key]
      const kbalance = record.kbalance ?? record.balance
      return {
        label: mode === 'monthly' ? dayjs(key).format('YYYY-MM') : dayjs(key).format('MM-DD'),
        kbalance: kbalance ?? null,
        zbalance: record.zbalance ?? null,
      }
    })
    .filter((p) => p.kbalance !== null || p.zbalance !== null)
}

const renderBalanceChart = (points, mode) => {
  if (!chartContainer.value || points.length === 0) return false

  if (!chartInstance) {
    chartInstance = echarts.init(chartContainer.value)
  }

  const labels = points.map((p) => p.label)
  const kbalances = points.map((p) => p.kbalance)
  const zbalances = points.map((p) => p.zbalance)
  const hasZ = zbalances.some((v) => v !== null && v !== undefined)

  const option = {
    tooltip: {
      trigger: 'axis',
      formatter: (params) => {
        let html = `<div style="font-weight:bold;margin-bottom:4px">${params[0].axisValue}</div>`
        params.forEach((param) => {
          if (param.value === null || param.value === undefined) return
          html += `<div>${param.marker}${param.seriesName}: <b>${Number(param.value).toFixed(2)} 度</b></div>`
        })
        return html
      },
    },
    legend: {
      data: hasZ ? ['空调余量', '照明余量'] : ['空调余量'],
      top: 8,
    },
    grid: { left: '3%', right: '4%', bottom: mode === 'daily' ? '18%' : '10%', top: '15%', containLabel: true },
    xAxis: {
      type: 'category',
      data: labels,
      axisLabel: { rotate: mode === 'daily' ? 45 : 0, fontSize: 11 },
    },
    yAxis: {
      type: 'value',
      name: '余量（度）',
      scale: true,
    },
    series: [
      {
        name: '空调余量',
        type: 'line',
        smooth: true,
        showSymbol: points.length <= 31,
        data: kbalances,
        itemStyle: { color: '#667eea' },
        areaStyle: { color: 'rgba(102, 126, 234, 0.08)' },
      },
    ],
  }

  if (hasZ) {
    option.series.push({
      name: '照明余量',
      type: 'line',
      smooth: true,
      showSymbol: points.length <= 31,
      data: zbalances,
      itemStyle: { color: '#67c23a' },
      areaStyle: { color: 'rgba(103, 194, 58, 0.08)' },
    })
  }

  chartInstance.setOption(option, true)
  chartInstance.resize()
  return true
}

const loadChartData = async () => {
  if (!dormNumber.value) return

  chartLoading.value = true
  hasChartData.value = false

  try {
    let records = []
    if (chartViewMode.value === 'monthly') {
      const endDate = dayjs().endOf('day')
      const startDate = endDate.subtract(11, 'month').startOf('month')
      records = await getRecordsByRange(dormNumber.value, startDate.toDate(), endDate.toDate())
    } else {
      const startDate = dayjs(selectedMonth.value).startOf('month')
      const endDate = dayjs(selectedMonth.value).endOf('month')
      records = await getRecordsByRange(dormNumber.value, startDate.toDate(), endDate.toDate())
    }

    const points = buildBalanceTrendPoints(records || [], chartViewMode.value)
    chartLoading.value = false
    if (points.length === 0) {
      hasChartData.value = false
      return
    }

    hasChartData.value = true
    await nextTick()
    if (!renderBalanceChart(points, chartViewMode.value)) {
      hasChartData.value = false
    }
  } catch (error) {
    hasChartData.value = false
    if (error.response?.status && error.response.status !== 404) {
      ElMessage.error('加载图表数据失败：' + (error.response?.data?.detail || error.message))
    }
  } finally {
    chartLoading.value = false
  }
}

const onChartViewModeChange = () => {
  loadChartData()
}

const onSelectedMonthChange = () => {
  if (chartViewMode.value === 'daily') {
    loadChartData()
  }
}

onMounted(async () => {
  try {
    const config = await getConfig()
    configMissing.value = !config.configured
    dormNumber.value = config.dorm_number || ''
    ruleForm.value.dorm_number = config.dorm_number || ''
    if (configMissing.value) {
      ElMessage.warning('请先在「系统配置」中填写宿舍号')
    }
  } catch (error) {
    configMissing.value = true
    ElMessage.error('获取配置失败：' + formatApiError(error))
  }
  
  await loadDormRecord()
  await loadAlertRule()
  await loadChartData()
  await loadQQConfig()
  await loadQQStatus()
  
  // 响应式调整图表
  resizeHandler = () => {
    descColumns.value = window.innerWidth < 768 ? 1 : 2
    chartInstance?.resize()
  }
  window.addEventListener('resize', resizeHandler)
})

onUnmounted(() => {
  if (resizeHandler) {
    window.removeEventListener('resize', resizeHandler)
  }
  if (chartInstance) {
    chartInstance.dispose()
    chartInstance = null
  }
})
</script>

<style scoped>
.dashboard {
  max-width: 1400px;
  margin: 0 auto;
  padding: 0;
}

/* 页面标题 */
.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
  padding: 0 4px;
}

.page-title {
  display: flex;
  align-items: center;
  font-size: 24px;
  font-weight: 600;
  color: #303133;
  margin: 0;
}

.title-icon {
  margin-right: 8px;
  font-size: 28px;
  color: #667eea;
}

.page-actions {
  display: flex;
  gap: 12px;
}

.config-tip {
  margin-bottom: 16px;
}

/* 卡片通用样式 */
.dorm-card,
.alert-rule-card,
.chart-card {
  margin-bottom: 24px;
  border-radius: 12px;
  border: none;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
  transition: all 0.3s ease;
}

.dorm-card:hover,
.alert-rule-card:hover,
.chart-card:hover {
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.12);
  transform: translateY(-2px);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 10px;
}

.header-title {
  display: flex;
  align-items: center;
  font-size: 16px;
  font-weight: 600;
  color: #303133;
}

.title-icon {
  margin-right: 8px;
  font-size: 18px;
  color: #667eea;
}

.header-actions {
  display: flex;
  gap: 10px;
}

.dorm-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 12px;
}

.dorm-number {
  display: flex;
  align-items: center;
  gap: 8px;
}

.dorm-icon {
  font-size: 20px;
  color: #667eea;
}

.dorm-number-text {
  font-size: 18px;
  font-weight: 600;
  color: #303133;
}

.status-tag {
  font-weight: 500;
}

.dorm-content {
  padding: 20px 0;
}

.dorm-no-data {
  padding: 20px 0;
  text-align: center;
}

/* 余额卡片样式 */
.balance-card {
  background: linear-gradient(135deg, #f5f7fa 0%, #ffffff 100%);
  border-radius: 12px;
  padding: 20px;
  margin-bottom: 16px;
  border: 1px solid #e4e7ed;
  transition: all 0.3s ease;
}

.balance-card:hover {
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  transform: translateY(-2px);
}

.balance-card-ac {
  border-left: 4px solid #667eea;
}

.balance-card-light {
  border-left: 4px solid #67c23a;
}

.balance-card-header {
  display: flex;
  align-items: center;
  margin-bottom: 12px;
}

.balance-icon {
  font-size: 24px;
  margin-right: 8px;
  color: #909399;
}

.balance-card-ac .balance-icon {
  color: #667eea;
}

.balance-card-light .balance-icon {
  color: #67c23a;
}

.balance-label {
  font-size: 14px;
  color: #909399;
  font-weight: 500;
}

.balance-value {
  font-size: 32px;
  font-weight: 700;
  line-height: 1.2;
  font-family: 'Arial', sans-serif;
}

.balance-unit {
  font-size: 18px;
  font-weight: 500;
  margin-left: 4px;
  opacity: 0.7;
}

.balance-low {
  color: #f56c6c;
}

.balance-warning {
  color: #e6a23c;
}

.balance-normal {
  color: #67c23a;
}

.dorm-time {
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 13px;
  color: #909399;
  margin-top: 20px;
  padding-top: 16px;
  border-top: 1px solid #f0f0f0;
}

.dorm-time .el-icon {
  margin-right: 6px;
  font-size: 14px;
}

.alert-rule-content {
  padding: 8px 0;
}

.alert-rule-content :deep(.el-descriptions) {
  margin-bottom: 16px;
}

.alert-rule-content :deep(.el-descriptions__label) {
  font-weight: 600;
  color: #606266;
  width: 160px;
}

.alert-rule-content :deep(.el-descriptions__content) {
  color: #303133;
}

.alert-rule-empty {
  padding: 60px 20px;
  text-align: center;
}

.rule-actions {
  margin-top: 15px;
  text-align: right;
}

.chart-container {
  height: 450px;
  width: 100%;
  min-height: 300px;
}

.chart-controls {
  display: flex;
  align-items: center;
}

.loading-container {
  padding: 40px 20px;
}

@media (max-width: 768px) {
  .dashboard {
    padding: 0 12px;
  }

  .page-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 16px;
  }

  .page-actions {
    width: 100%;
    flex-wrap: wrap;
  }

  .page-actions .el-button {
    flex: 1 1 calc(50% - 6px);
    min-width: 120px;
  }

  .card-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 12px;
  }

  .chart-controls {
    width: 100%;
    flex-direction: column;
    align-items: stretch;
    gap: 10px;
  }

  .chart-controls .el-date-editor {
    width: 100% !important;
    margin-left: 0 !important;
  }

  .alert-rule-content :deep(.el-descriptions__label) {
    width: 120px !important;
  }

  .rule-actions {
    text-align: center;
  }

  .rule-actions .el-button {
    width: 100%;
  }

  .balance-value {
    font-size: 28px;
  }

  .balance-unit {
    font-size: 16px;
  }

  .chart-container {
    height: 350px;
  }

  .dorm-number-text {
    font-size: 16px;
  }
}

@media (max-width: 480px) {
  .page-title {
    font-size: 20px;
  }

  .balance-value {
    font-size: 24px;
  }

  .chart-container {
    height: 300px;
  }
}
</style>
