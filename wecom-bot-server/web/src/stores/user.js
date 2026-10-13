import { defineStore } from 'pinia'
import { ref } from 'vue'

export const useUserStore = defineStore('user', () => {
  const token = YOUR_SECRET'token') || '')
  const username = ref(localStorage.getItem('username') || '')
  const role = ref(localStorage.getItem('role') || 'user')
  const isLoggedIn = ref(!!token.value)

  const setToken = (newToken) => {
    token.value = newToken
    localStorage.setItem('token', newToken)
  }

  const setUsername = (name) => {
    username.value = name
    localStorage.setItem('username', name)
  }

  const setRole = (userRole) => {
    role.value = userRole
    localStorage.setItem('role', userRole)
  }

  const logout = () => {
    token.value = ''
    username.value = ''
    role.value = 'user'
    isLoggedIn.value = false
    localStorage.removeItem('token')
    localStorage.removeItem('username')
    localStorage.removeItem('role')
  }

  const initFromStorage = () => {
    if (token.value && username.value) {
      isLoggedIn.value = true
    }
  }

  return {
    token,
    username,
    role,
    isLoggedIn,
    setToken,
    setUsername,
    setRole,
    logout,
    initFromStorage
  }
})
