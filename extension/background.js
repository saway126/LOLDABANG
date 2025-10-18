// background.js
console.log('롤다방 Extension Background Script 시작');

chrome.runtime.onInstalled.addListener(() => {
  console.log('Extension installed');
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
