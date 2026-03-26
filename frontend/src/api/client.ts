import axios from 'axios'

const apiClient = axios.create({
  baseURL: '/api',
  headers: {
    'X-API-Key': import.meta.env.VITE_API_KEY || 'dev-api-key',
  },
})

apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      console.error('Authentication failed — check API key')
    }
    return Promise.reject(error)
  }
)

export default apiClient
