import {createRouter, createWebHistory} from 'vue-router'
import axios from 'axios'
import LoginPage from '../components/LoginPage.vue'
import Dashboard from '../components/Dashboard.vue'
import PatentsPage from '../components/PatentsPage.vue'
import AnalysisPage from '../components/AnalysisPage.vue'

const routes = [
    {path: '/', redirect: '/dashboard'},
    {path: '/login', component: LoginPage},
    {path: '/dashboard', component: Dashboard},
    {path: '/patents', component: PatentsPage},
    {path: '/analysis', component: AnalysisPage}
]

const router = createRouter({
    history: createWebHistory(),
    routes
})

router.beforeEach(async (to, from, next) => {
    if (to.path === '/login') return next()
    try {
        const res = await axios.get('/api/status')
        if (res.data.user) {
            next()
        } else {
            next('/login')
        }
    } catch (e) {
        next('/login')
    }
})

export default router
