import {createRouter, createWebHistory} from 'vue-router'
import axios from 'axios'
import LoginPage from '../components/LoginPage.vue'
import AppLayout from '../components/AppLayout.vue'
import Dashboard from '../components/Dashboard.vue'
import PatentsPage from '../components/PatentsPage.vue'
import AnalysisPage from '../components/AnalysisPage.vue'
import UserManagement from '../components/UserManagement.vue'
import DebugPage from '../components/DebugPage.vue'
import authStore from '../stores/auth'

const routes = [
    {path: '/login', component: LoginPage},
    {path: '/debug', component: DebugPage},  // 添加调试页面
    {
        path: '/', component: AppLayout, children: [
            {path: '', redirect: 'patents'},
            {path: 'patents', component: PatentsPage},
            {path: 'analysis', component: AnalysisPage},
            {path: 'admin', component: Dashboard},
            {path: 'users', component: UserManagement}
        ]
    }
]

const router = createRouter({
    history: createWebHistory(),
    routes
})

router.beforeEach(async (to, from, next) => {
    console.log('路由守卫检查:', to.path, '来自:', from.path)

    if (to.path === '/login' || to.path === '/debug') {
        console.log('访问登录或调试页面，允许通过')
        return next()
    }

    // 检查authStore是否有最近的认证状态（避免频繁API调用）
    const now = new Date()
    const timeSinceLastCheck = authStore.lastCheck ? (now - authStore.lastCheck) / 1000 : Infinity

    let authData
    if (timeSinceLastCheck < 2 && authStore.isAuthenticated) {
        // 如果最近2秒内检查过且已认证，直接使用缓存状态
        console.log('使用缓存的认证状态，避免频繁检查')
        authData = {
            authenticated: authStore.isAuthenticated,
            login_type: authStore.loginType,
            user: authStore.user
        }
    } else {
        // 否则重新检查认证状态
        try {
            console.log('重新检查认证状态...')
            authData = await authStore.checkAuth()
        } catch (error) {
            console.error('认证检查失败:', error)
            return next('/login')
        }
    }

    if (!authData.authenticated) {
        console.log('用户未认证，重定向到登录页面')
        return next('/login')
    }

    const loginType = authData.login_type || 'user'
    console.log('用户类型:', loginType)

    // 检查管理员权限
    if ((to.path === '/admin' || to.path === '/users') && loginType !== 'admin') {
        console.log('普通用户尝试访问管理员页面，重定向到专利页面')
        return next('/patents')
    }

    // 检查分析页面权限
    if (to.path === '/analysis' && loginType === 'admin') {
        console.log('管理员尝试访问分析页面，重定向到专利页面')
        return next('/patents')
    }

    console.log('认证通过，允许访问:', to.path)
    next()
})

export default router
