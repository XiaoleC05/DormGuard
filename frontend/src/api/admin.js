import api from './index'

export const getSettings = () => api.get('/admin/settings')
export const updateSettings = (settings) => api.put('/admin/settings', { settings })
