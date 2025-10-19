import { createRouter, createWebHistory } from 'vue-router'
import Home from '../views/Home.vue'
import Create from '../views/Create.vue'
import Balance from '../views/Balance.vue'
import MatchDetail from '../views/MatchDetail.vue'
import RealtimeBanPick from '../views/RealtimeBanPick.vue'
import RiotBalance from '../views/RiotBalance.vue'

const routes = [
  { path: '/', name: 'Home', component: Home },
  { path: '/create', name: 'Create', component: Create },
  { path: '/balance', name: 'Balance', component: Balance },
  { path: '/match/:id', name: 'MatchDetail', component: MatchDetail },
  { path: '/banpick', name: 'RealtimeBanPick', component: RealtimeBanPick },
  { path: '/riot-balance', name: 'RiotBalance', component: RiotBalance }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router
