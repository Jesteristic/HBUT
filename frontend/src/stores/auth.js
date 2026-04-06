import {reactive} from 'vue'
import axios from 'axios'

const authStore = reactive({
    isAuthenticated: false,
    user: null,
    loginType: 'user',
    lastCheck: null,

    async checkAuth() {
        try {
            const response = await axios.get('/api/check-auth')
            const data = response.data

            this.isAuthenticated = data.authenticated
            this.user = data.user || null
            this.loginType = data.login_type || 'user'
            this.lastCheck = new Date()

            console.log('Auth store updated:', {
                isAuthenticated: this.isAuthenticated,
                loginType: this.loginType,
                lastCheck: this.lastCheck
            })

            return data
        } catch (error) {
            console.error('Auth check failed:', error)
            this.isAuthenticated = false
            this.user = null
            this.loginType = 'user'
            throw error
        }
    },

    async login(credentials) {
        try {
            const response = await axios.post('/api/login', credentials)
            const data = response.data

            if (data.ok) {
                // 登录成功后立即更新本地状态，然后异步检查以确保同步
                this.isAuthenticated = true
                this.loginType = credentials.loginType || 'user'
                this.lastCheck = new Date()

                console.log('Login successful, authStore updated:', {
                    isAuthenticated: this.isAuthenticated,
                    loginType: this.loginType,
                    lastCheck: this.lastCheck
                })

                // 异步检查以确保状态正确（不阻塞返回）
                this.checkAuth().catch(error => {
                    console.error('Background auth check failed:', error)
                })
            }

            return data
        } catch (error) {
            console.error('Login failed:', error)
            throw error
        }
    },

    async logout() {
        try {
            await axios.post('/api/logout')
            this.isAuthenticated = false
            this.user = null
            this.loginType = 'user'
            this.lastCheck = null
        } catch (error) {
            console.error('Logout failed:', error)
        }
    }
})

export default authStore