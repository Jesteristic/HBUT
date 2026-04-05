import { createApp } from 'vue'
import App from './App.vue'
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'
import * as ElementPlusIconsVue from '@element-plus/icons-vue'
import axios from 'axios'
import router from './router'

axios.defaults.withCredentials = true

// redirect to login when server returns 401
axios.interceptors.response.use(
  res => res,
  err => {
    if (err.response && err.response.status === 401) {
      router.push('/login')
    }
    return Promise.reject(err)
  }
)

const app = createApp(App)
app.use(ElementPlus)
for (const [key, component] of Object.entries(ElementPlusIconsVue)) {
  app.component(key, component)
}
app.use(router)
app.mount('#app')
