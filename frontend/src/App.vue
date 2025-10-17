<template>
  <div id="app">
    <header class="header">
      <h1>LoL 내전 도구</h1>
    </header>
    
    <nav class="nav">
      <router-link to="/" class="nav-item">내전 종류</router-link>
      <router-link to="/create" class="nav-item">내전 생성</router-link>
      <router-link to="/balance" class="nav-item">밸런스 조율</router-link>
    </nav>
    
    <main class="main">
      <router-view />
    </main>
  </div>
</template>

<script setup lang="ts">
import { RouterView } from 'vue-router'
</script>

<style scoped>
.header {
  background: #2196F3;
  color: white;
  padding: 1rem;
  text-align: center;
}

.header h1 {
  margin: 0;
  font-size: 1.5rem;
}

.nav {
  display: flex;
  background: white;
  border-bottom: 1px solid #e0e0e0;
}

.nav-item {
  flex: 1;
  padding: 1rem;
  text-align: center;
  text-decoration: none;
  color: #666;
  border-bottom: 2px solid transparent;
  transition: all 0.3s;
}

.nav-item:hover,
.nav-item.router-link-active {
  color: #2196F3;
  border-bottom-color: #2196F3;
  font-weight: bold;
}

.main {
  padding: 1rem;
  background: #f5f5f5;
  min-height: calc(100vh - 120px);
}
</style>
