<template>
  <div id="app" class="app">
    <!-- 배경 패턴 -->
    <div class="background-pattern">
      <div class="leaves leaves-1">🍂</div>
      <div class="leaves leaves-2">🍁</div>
      <div class="leaves leaves-3">🍃</div>
      <div class="leaves leaves-4">🍂</div>
      <div class="leaves leaves-5">🍁</div>
    </div>
    
    <header class="header">
      <div class="header-content">
        <div class="logo">
          <div class="logo-text">LDB</div>
          <div class="logo-subtitle">롤다방 내전프로그램</div>
        </div>
        <div class="header-decoration">🎮</div>
      </div>
    </header>
    
    <nav class="nav">
      <router-link to="/" class="nav-item">
        <div class="nav-icon">🏠</div>
        <div class="nav-text">내전 종류</div>
      </router-link>
      <router-link to="/create" class="nav-item">
        <div class="nav-icon">➕</div>
        <div class="nav-text">내전 생성</div>
      </router-link>
      <router-link to="/balance" class="nav-item">
        <div class="nav-icon">⚖️</div>
        <div class="nav-text">밸런스 조율</div>
      </router-link>
      <router-link to="/riot-balance" class="nav-item">
        <div class="nav-icon">🔍</div>
        <div class="nav-text">라이엇 밸런싱</div>
      </router-link>
    </nav>
    
    <main class="main">
      <router-view />
    </main>
    
    <!-- 실시간 알림 컴포넌트 -->
    <RealtimeNotification />
  </div>
</template>

<script setup lang="ts">
import { RouterView } from 'vue-router'
import RealtimeNotification from './components/RealtimeNotification.vue'
</script>

<style scoped>
.app {
  min-height: 100vh;
  background: linear-gradient(135deg, #f5f1e8 0%, #e8dcc0 100%);
  position: relative;
  overflow-x: hidden;
}

.background-pattern {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  pointer-events: none;
  z-index: 0;
}

.leaves {
  position: absolute;
  font-size: 1.5rem;
  opacity: 0.3;
  animation: float 6s ease-in-out infinite;
}

.leaves-1 { top: 10%; left: 10%; animation-delay: 0s; }
.leaves-2 { top: 20%; right: 15%; animation-delay: 1s; }
.leaves-3 { top: 60%; left: 5%; animation-delay: 2s; }
.leaves-4 { top: 80%; right: 10%; animation-delay: 3s; }
.leaves-5 { top: 40%; left: 50%; animation-delay: 4s; }

@keyframes float {
  0%, 100% { transform: translateY(0px) rotate(0deg); }
  50% { transform: translateY(-10px) rotate(5deg); }
}

.header {
  background: linear-gradient(135deg, #8B4513 0%, #A0522D 50%, #8B4513 100%);
  color: #f5f1e8;
  padding: 1.5rem 1rem;
  text-align: center;
  position: relative;
  z-index: 10;
  box-shadow: 0 4px 12px rgba(139, 69, 19, 0.3);
}

.header-content {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 1rem;
}

.logo {
  text-align: center;
}

.logo-text {
  font-size: 2.5rem;
  font-weight: bold;
  text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.3);
  letter-spacing: 0.2em;
  color: #f5f1e8;
  font-family: 'Courier New', monospace;
}

.logo-subtitle {
  font-size: 0.9rem;
  margin-top: 0.2rem;
  opacity: 0.9;
  color: #d4c4a8;
}

.header-decoration {
  font-size: 2rem;
  animation: bounce 2s infinite;
}

@keyframes bounce {
  0%, 20%, 50%, 80%, 100% { transform: translateY(0); }
  40% { transform: translateY(-5px); }
  60% { transform: translateY(-3px); }
}

.nav {
  display: flex;
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(10px);
  border-bottom: 2px solid #d4c4a8;
  position: relative;
  z-index: 10;
  box-shadow: 0 2px 8px rgba(139, 69, 19, 0.1);
}

.nav-item {
  flex: 1;
  padding: 1.2rem 0.5rem;
  text-align: center;
  text-decoration: none;
  color: #8B4513;
  border-bottom: 3px solid transparent;
  transition: all 0.3s ease;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.3rem;
  position: relative;
}

.nav-item:hover {
  background: rgba(139, 69, 19, 0.05);
  transform: translateY(-2px);
}

.nav-item.router-link-active {
  color: #8B4513;
  border-bottom-color: #8B4513;
  font-weight: bold;
  background: rgba(139, 69, 19, 0.1);
}

.nav-icon {
  font-size: 1.2rem;
  margin-bottom: 0.2rem;
}

.nav-text {
  font-size: 0.85rem;
  font-weight: 500;
}

.main {
  padding: 2rem 1rem;
  background: transparent;
  min-height: calc(100vh - 140px);
  position: relative;
  z-index: 5;
}

/* 반응형 디자인 */
@media (max-width: 768px) {
  .header-content {
    flex-direction: column;
    gap: 0.5rem;
  }
  
  .logo-text {
    font-size: 2rem;
  }
  
  .nav-item {
    padding: 1rem 0.3rem;
  }
  
  .nav-text {
    font-size: 0.75rem;
  }
  
  .main {
    padding: 1rem 0.5rem;
  }
}
</style>
