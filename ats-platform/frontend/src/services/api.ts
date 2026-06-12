/**
 * src/services/api.ts
 * Centralized Axios configuration. All API calls go through this client.
 */
import axios from 'axios'

const API_BASE_URL: string =
  (import.meta.env as Record<string, string>)['VITE_API_BASE_URL'] ??
  'http://localhost:8000'

export const apiClient = axios.create({
  baseURL: `${API_BASE_URL}/api/v1`,
  headers: { 'Content-Type': 'application/json' },
  timeout: 30000,
})

// Attach auth token when present
apiClient.interceptors.request.use((config) => {
  const token = localStorage.getItem('auth_token')
  if (token) config.headers.Authorization = `Bearer ${token}`
  return config
})

// Global error handling
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('auth_token')
    }
    return Promise.reject(error)
  },
)

export default apiClient
