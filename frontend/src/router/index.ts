import { createRouter, createWebHistory } from 'vue-router'
import Home from '../views/Home.vue'
import Create from '../views/Create.vue'
import Balance from '../views/Balance.vue'
import MatchDetail from '../views/MatchDetail.vue'
import Realtime from '../views/Realtime.vue'
import RealtimeBanPick from '../views/RealtimeBanPick.vue'
import RealtimeBalance from '../views/RealtimeBalance.vue'

const routes = [
  { path: '/', name: 'Home', component: Home },
  { path: '/create', name: 'Create', component: Create },
  { path: '/balance', name: 'Balance', component: Balance },
  { path: '/match/:id', name: 'MatchDetail', component: MatchDetail },
  { path: '/realtime', name: 'Realtime', component: Realtime },
  { path: '/banpick', name: 'RealtimeBanPick', component: RealtimeBanPick },
  { path: '/realtime-balance', name: 'RealtimeBalance', component: RealtimeBalance }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router
