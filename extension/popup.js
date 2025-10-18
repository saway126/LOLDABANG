// popup.js
console.log('롤다방 Extension Popup 시작');

class PopupManager {
  constructor() {
    this.init();
  }

  init() {
    this.setupEventListeners();
    this.loadData();
  }

  setupEventListeners() {
    document.getElementById('refreshBtn').addEventListener('click', () => {
      this.loadData();
    });

    document.getElementById('openSiteBtn').addEventListener('click', () => {
      chrome.tabs.create({ url: 'https://loldabang.vercel.app' });
    });
  }

  async loadData() {
    this.showLoading();
    
    try {
      // API 상태 확인
      await this.checkAPIStatus();
      
      // 각 내전 타입별 개수 가져오기
      await this.loadMatchCounts();
      
    } catch (error) {
      console.error('데이터 로드 실패:', error);
      this.showError();
    }
  }

  async checkAPIStatus() {
    try {
      const response = await fetch('https://loldabang-production.up.railway.app/api/health');
      
      if (response.ok) {
        const data = await response.json();
        document.getElementById('apiStatus').textContent = '✅ 연결됨';
        document.getElementById('apiStatus').style.color = '#4ade80';
        console.log('API 상태:', data);
      } else {
        throw new Error(`HTTP ${response.status}`);
      }
    } catch (error) {
      document.getElementById('apiStatus').textContent = '❌ 연결 실패';
      document.getElementById('apiStatus').style.color = '#f87171';
      console.error('API 상태 확인 실패:', error);
    }
  }

  async loadMatchCounts() {
    const matchTypes = ['soft', 'hard', 'hyper'];
    
    for (const type of matchTypes) {
      try {
        const count = await this.getMatchCount(type);
        const elementId = `${type}Count`;
        document.getElementById(elementId).textContent = `${count}개`;
        document.getElementById(elementId).style.color = '#4ade80';
      } catch (error) {
        console.error(`${type} 내전 개수 가져오기 실패:`, error);
        const elementId = `${type}Count`;
        document.getElementById(elementId).textContent = '오류';
        document.getElementById(elementId).style.color = '#f87171';
      }
    }
  }

  async getMatchCount(matchType) {
    try {
      const response = await fetch(`https://loldabang-production.up.railway.app/api/matches/by-type/${matchType}`);
      
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}`);
      }
      
      const data = await response.json();
      return Array.isArray(data) ? data.length : 0;
    } catch (error) {
      console.error(`getMatchCount 실패 (${matchType}):`, error);
      throw error;
    }
  }

  showLoading() {
    document.getElementById('apiStatus').textContent = '확인 중...';
    document.getElementById('apiStatus').style.color = '#fbbf24';
    
    ['soft', 'hard', 'hyper'].forEach(type => {
      document.getElementById(`${type}Count`).textContent = '...';
      document.getElementById(`${type}Count`).style.color = '#fbbf24';
    });
  }

  showError() {
    document.getElementById('apiStatus').textContent = '❌ 오류 발생';
    document.getElementById('apiStatus').style.color = '#f87171';
  }
}

// Popup 초기화
document.addEventListener('DOMContentLoaded', () => {
  new PopupManager();
});
