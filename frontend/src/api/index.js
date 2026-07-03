import axios from 'axios'
import { clearAuth, getToken } from './auth'

const api = axios.create({
  baseURL: '/api',
  timeout: 15000
})

api.interceptors.request.use(
  config => {
    const token = getToken()
    if (token && !config.headers.Authorization) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  error => Promise.reject(error)
)

api.interceptors.response.use(
  response => {
    if (response.status === 204) {
      return null
    }
    return response.data
  },
  error => {
    if (error.response?.status === 401) {
      clearAuth()
      if (!window.location.pathname.startsWith('/login')) {
        window.location.href = '/login'
      }
    }
    if (error.response?.status === 404 || error.response?.status === 204) {
      return Promise.reject(error)
    }
    if (!error.response) {
      console.error('Network Error:', error.message)
    } else if (error.response?.status === 500) {
      const message = error.response?.data?.detail || error.message || '请求失败'
      console.error('API Error:', message)
    }
    return Promise.reject(error)
  }
)

export default api
