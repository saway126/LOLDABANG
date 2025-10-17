import { createRouter, createWebHistory } from 'vue-router'
import Home from '../views/Home.vue'
import Create from '../views/Create.vue'
import Balance from '../views/Balance.vue'

const routes = [
  { path: '/', name: 'Home', component: Home },
  { path: '/create', name: 'Create', component: Create },
  { path: '/balance', name: 'Balance', component: Balance }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router
