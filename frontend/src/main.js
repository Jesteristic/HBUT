import { createApp } from 'vue'
import App from './App.vue'
import ElementPlus from 'element-plus'
import zhCn from 'element-plus/dist/locale/zh-cn'
import 'element-plus/dist/index.css'
import * as ElementPlusIconsVue from '@element-plus/icons-vue'
import axios from 'axios'
import router from './router'
import authStore from './stores/auth'

zhCn.el.pagination.itemsPerPage = '/page'

axios.defaults.withCredentials = true
axios.defaults.baseURL = 'http://localhost:5000'

// 添加请求拦截器
axios.interceptors.request.use(
    config => {
        console.log('发送请求:', config.method?.toUpperCase(), config.url)
        return config
    },
    error => {
        console.error('请求错误:', error)
        return Promise.reject(error)
    }
)

// 添加响应拦截器
axios.interceptors.response.use(
    response => {
        console.log('收到响应:', response.status, response.config.url)
        return response
    },
    error => {
        console.error('响应错误:', error.response?.status, error.response?.data || error.message)

        // 处理401认证错误
        if (error.response?.status === 401) {
            console.log('检测到401错误，清除登录状态')
            // 清除本地存储
            localStorage.removeItem('savedUsername')
            localStorage.removeItem('savedPassword')
            localStorage.removeItem('loginType')

            // 重定向到登录页面
            if (router.currentRoute.value.path !== '/login') {
                router.push('/login')
            }
        }

        return Promise.reject(error)
  }
)
//     }
//     return Promise.reject(err)
//   }
// )

const app = createApp(App)
app.use(ElementPlus, {locale: zhCn})
for (const [key, component] of Object.entries(ElementPlusIconsVue)) {
  app.component(key, component)
}
app.use(router)

// 全局提供auth store
app.provide('authStore', authStore)

app.mount('#app')
