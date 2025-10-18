// background.js
console.log('롤다방 Extension Background Script 시작');

chrome.runtime.onInstalled.addListener(() => {
  console.log('Extension installed');
});

// API 호출 함수 (재시도 로직 포함)
async function callAPI(endpoint, retries = 3) {
  const API_BASE_URL = 'https://loldabang-production.up.railway.app/api';
  
  for (let i = 0; i < retries; i++) {
    try {
      const response = await fetch(`${API_BASE_URL}${endpoint}`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        },
        mode: 'cors',
        cache: 'no-cache' // BFCache 문제 방지
      });
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      return await response.json();
    } catch (error) {
      console.error(`API call failed (attempt ${i + 1}/${retries}):`, error);
      
      if (i === retries - 1) {
        throw error; // 마지막 시도에서 실패하면 에러 던지기
      }
      
      // 재시도 전 잠시 대기
      await new Promise(resolve => setTimeout(resolve, 1000 * (i + 1)));
    }
  }
}

// BFCache 안전한 메시지 리스너
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
  // sender.tab이 없으면 (background에서 호출) 무시
  if (!sender.tab) {
    return false;
  }

  // 탭이 활성화되어 있는지 확인
  chrome.tabs.query({ active: true, currentWindow: true }, (tabs) => {
    const isActiveTab = tabs.some(tab => tab.id === sender.tab.id);
    
    if (!isActiveTab) {
      console.log('비활성 탭에서의 요청 무시:', request.action);
      sendResponse({ success: false, error: 'Tab not active' });
      return;
    }

    if (request.action === 'fetchMatches') {
      callAPI(`/matches/by-type/${request.matchType}`)
        .then(data => sendResponse({ success: true, data }))
        .catch(error => sendResponse({ success: false, error: error.message }));
    }
    
    if (request.action === 'getMatchCount') {
      callAPI(`/matches/by-type/${request.matchType}`)
        .then(data => {
          const count = Array.isArray(data) ? data.length : 0;
          sendResponse({ success: true, count });
        })
        .catch(error => sendResponse({ success: false, error: error.message }));
    }
  });
  
  return true; // 비동기 응답을 위해 필요
});
