import api from './index'

export const login = (username, password) =>
  api.post('/auth/login', { username, password })

export const getToken = () => sessionStorage.getItem('dp_token')
export const getUsername = () => sessionStorage.getItem('dp_user')
export const setAuth = (token, username) => {
  sessionStorage.setItem('dp_token', token)
  sessionStorage.setItem('dp_user', username)
}
export const clearAuth = () => {
  sessionStorage.removeItem('dp_token')
  sessionStorage.removeItem('dp_user')
}
export const isLoggedIn = () => Boolean(getToken())
