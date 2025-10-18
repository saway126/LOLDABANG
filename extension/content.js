// content.js
console.log('롤다방 Extension Content Script 시작');

class LoldabangExtension {
  constructor() {
    this.port = null;
    this.init();
  }

  init() {
    this.createPort();
    this.setupMessageListener();
    this.injectAPIHelpers();
  }

  createPort() {
    try {
      this.port = chrome.runtime.connect({ name: 'loldabang-extension' });
      
      this.port.onDisconnect.addListener(() => {
        console.log('Port disconnected, attempting to reconnect...');
        setTimeout(() => this.createPort(), 1000);
      });
      
      this.port.onMessage.addListener((message) => {
        console.log('Message from background:', message);
      });
    } catch (error) {
      console.error('Failed to create port:', error);
      setTimeout(() => this.createPort(), 1000);
    }
  }

  setupMessageListener() {
    chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
      if (request.action === 'fetchMatches') {
        this.fetchMatches(request.matchType)
          .then(data => sendResponse({ success: true, data }))
          .catch(error => sendResponse({ success: false, error: error.message }));
        
        return true;
      }
    });
  }

  async fetchMatches(matchType) {
    const API_BASE_URL = 'https://loldabang-production.up.railway.app/api';
    
    try {
      const response = await fetch(`${API_BASE_URL}/matches/by-type/${matchType}`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        },
        mode: 'cors'
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      return await response.json();
    } catch (error) {
      console.error('Failed to fetch matches:', error);
      throw error;
    }
  }

  async getMatchCount(matchType) {
    try {
      const data = await this.fetchMatches(matchType);
      return Array.isArray(data) ? data.length : 0;
    } catch (error) {
      console.error(`Failed to get match count for ${matchType}:`, error);
      return 0;
    }
  }

  injectAPIHelpers() {
    // 전역 함수로 API 헬퍼 노출
    window.loldabangAPI = {
      getMatchCount: (matchType) => this.getMatchCount(matchType),
      fetchMatches: (matchType) => this.fetchMatches(matchType)
    };

    // 페이지 로드 시 API 테스트
    this.testAPI();
  }

  async testAPI() {
    try {
      console.log('롤다방 API 테스트 시작...');
      
      const healthResponse = await fetch('https://loldabang-production.up.railway.app/api/health');
      if (healthResponse.ok) {
        const healthData = await healthResponse.json();
        console.log('롤다방 API 연결 성공:', healthData);
      } else {
        console.error('롤다방 API 연결 실패:', healthResponse.status);
      }
    } catch (error) {
      console.error('롤다방 API 테스트 실패:', error);
    }
  }
}

// Extension 초기화
const loldabangExtension = new LoldabangExtension();

// 전역 함수로 노출
window.loldabangExtension = loldabangExtension;
