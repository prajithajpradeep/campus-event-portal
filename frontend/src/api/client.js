import axios from 'axios'

// One shared connection to the backend. baseURL '/api' works because the Vite
// dev server proxies /api to the backend (see vite.config.js).
const client = axios.create({ baseURL: '/api' })

// Before every request, attach the saved login token (our "hand stamp").
client.interceptors.request.use((config) => {
  const token = localStorage.getItem('token')
  if (token) config.headers.Authorization = `Bearer ${token}`
  return config
})

export default client
