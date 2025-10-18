// background.js
console.log('롤다방 Extension Background Script 시작');

chrome.runtime.onInstalled.addListener(() => {
  console.log('Extension installed');
});

// 안전한 포트 연결 관리
let port = null;

function createPort() {
  if (port) {
    try {
      port.disconnect();
    } catch (e) {
      console.log('Port already disconnected');
    }
  }
  
  port = chrome.runtime.connect({ name: 'loldabang-extension' });
  
  port.onDisconnect.addListener(() => {
    console.log('Port disconnected, recreating...');
    setTimeout(createPort, 1000);
  });
  
  port.onMessage.addListener((message) => {
    console.log('Message received:', message);
  });
}

// 페이지 로드 시 포트 생성
chrome.tabs.onUpdated.addListener((tabId, changeInfo, tab) => {
  if (changeInfo.status === 'complete' && tab.url) {
    createPort();
  }
});

// API 호출 함수
async function callAPI(endpoint) {
  const API_BASE_URL = 'https://loldabang-production.up.railway.app/api';
  
  try {
    const response = await fetch(`${API_BASE_URL}${endpoint}`, {
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
    console.error('API call failed:', error);
    throw error;
  }
}

// 메시지 리스너
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
  if (request.action === 'fetchMatches') {
    callAPI(`/matches/by-type/${request.matchType}`)
      .then(data => sendResponse({ success: true, data }))
      .catch(error => sendResponse({ success: false, error: error.message }));
    
    return true; // 비동기 응답을 위해 필요
  }
  
  if (request.action === 'getMatchCount') {
    callAPI(`/matches/by-type/${request.matchType}`)
      .then(data => {
        const count = Array.isArray(data) ? data.length : 0;
        sendResponse({ success: true, count });
      })
      .catch(error => sendResponse({ success: false, error: error.message }));
    
    return true;
  }
});
