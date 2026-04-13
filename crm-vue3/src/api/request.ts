import axios, { AxiosInstance, AxiosRequestConfig, AxiosResponse, InternalAxiosRequestConfig } from 'axios'
import { ElMessage, ElMessageBox } from 'element-plus'
import { useUserStore } from '@/store/user'
import router from '@/router'

// 防止重复弹出登录过期提示
let isShowingLoginDialog = false

// 创建axios实例
const service: AxiosInstance = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json'
  }
})

// 请求拦截器
service.interceptors.request.use(
  (config: InternalAxiosRequestConfig) => {
    const userStore = useUserStore()
    if (userStore.token) {
      config.headers.Authorization = `Bearer ${userStore.token}`
    }
    return config
  },
  (error) => {
    console.error('请求错误:', error)
    return Promise.reject(error)
  }
)

// 处理401登录过期
function handle401Error() {
  if (isShowingLoginDialog) {
    return
  }
  isShowingLoginDialog = true
  
  // 清除本地token，防止后续请求再次401
  const userStore = useUserStore()
  userStore.clearToken()
  
  ElMessageBox.close()
  ElMessageBox.confirm('登录已过期，请重新登录', '提示', {
    confirmButtonText: '重新登录',
    cancelButtonText: '取消',
    type: 'warning',
    showClose: false,
    closeOnClickModal: false,
    closeOnPressEscape: false
  }).then(() => {
    userStore.logout()
    router.push('/login')
  }).catch(() => {
    userStore.logout()
    router.push('/login')
  }).finally(() => {
    isShowingLoginDialog = false
  })
}

// 响应拦截器 - 详细错误提示
service.interceptors.response.use(
  (response: AxiosResponse) => {
    const resData = response.data
    const { code, message } = resData

    // 成功响应
    if (code === 200 || code === 0 || code === undefined) {
      return resData.data !== undefined ? resData.data : resData
    }

    // 登录接口的401是认证失败
    if (code === 401 && response.config.url?.includes('/auth/login')) {
      const msg = message || '用户名或密码错误'
      ElMessage.error(msg)
      return Promise.reject(new Error(msg))
    }

    // token过期
    if (code === 401) {
      handle401Error()
      return Promise.reject(new Error('登录已过期'))
    }

    // 其他业务错误
    const errorMsg = message || '操作失败'
    ElMessage.error(errorMsg)
    return Promise.reject(new Error(errorMsg))
  },
  (error) => {
    let message = '网络错误'
    let detail = ''

    if (error.response) {
      const { status, data } = error.response
      const apiMsg = data?.message || data?.msg || ''

      switch (status) {
        case 400:
          message = apiMsg || '请求参数错误'
          break
        case 401:
          if (error.config?.url?.includes('/auth/login')) {
            message = apiMsg || '用户名或密码错误'
          } else {
            handle401Error()
            return Promise.reject(error)
          }
          break
        case 403:
          message = apiMsg || '没有权限访问此资源'
          break
        case 404:
          message = apiMsg || '请求的资源不存在'
          break
        case 422:
          // 数据验证错误
          message = apiMsg || '数据验证失败'
          break
        case 500:
          // 服务器内部错误，显示更详细信息
          message = apiMsg || '服务器内部错误'
          detail = data?.detail || data?.error || ''
          if (detail) {
            console.error('服务器错误详情:', detail)
          }
          break
        default:
          message = apiMsg || `请求失败 (${status})`
      }
    } else if (error.message.includes('timeout')) {
      message = '请求超时，请检查网络连接或服务器状态'
    } else if (error.message.includes('Network Error')) {
      message = '网络连接失败，请检查网络'
    } else if (error.code === 'ECONNABORTED') {
      message = '请求超时，请稍后重试'
    }

    // 显示错误提示，包含详情
    if (detail && status === 500) {
      ElMessage.error(`${message}: ${detail.substring(0, 50)}`)
    } else {
      ElMessage.error(message)
    }

    return Promise.reject(error)
  }
)

// 封装请求方法
export const request = {
  get<T = any>(url: string, params?: any, config?: AxiosRequestConfig): Promise<T> {
    return service.get(url, { params, ...config })
  },

  post<T = any>(url: string, data?: any, config?: AxiosRequestConfig): Promise<T> {
    return service.post(url, data, config)
  },

  put<T = any>(url: string, data?: any, config?: AxiosRequestConfig): Promise<T> {
    return service.put(url, data, config)
  },

  delete<T = any>(url: string, params?: any, config?: AxiosRequestConfig): Promise<T> {
    return service.delete(url, { params, ...config })
  },

  upload<T = any>(url: string, formData: FormData, onUploadProgress?: (progressEvent: ProgressEvent) => void): Promise<T> {
    return service.post(url, formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
      onUploadProgress: (progressEvent) => {
        if (progressEvent.total && onUploadProgress) {
          const percent = Math.round((progressEvent.loaded * 100) / progressEvent.total)
          onUploadProgress(percent)
        }
      }
    })
  },

  download(url: string, filename: string) {
    return service.get(url, { responseType: 'blob' }).then((blob: any) => {
      const url = window.URL.createObjectURL(new Blob([blob]))
      const link = document.createElement('a')
      link.href = url
      link.download = filename
      document.body.appendChild(link)
      link.click()
      document.body.removeChild(link)
      window.URL.revokeObjectURL(url)
    })
  }
}

export default service
