# 롤다방 Chrome Extension

롤다방 내전프로그램을 위한 Chrome Extension입니다.

## 🚀 설치 방법

### 1. Extension 파일 다운로드
- `extension` 폴더의 모든 파일을 다운로드합니다.

### 2. Chrome에서 Extension 로드
1. Chrome 브라우저를 열고 `chrome://extensions/`로 이동
2. 우측 상단의 "개발자 모드" 토글을 활성화
3. "압축해제된 확장 프로그램을 로드합니다" 클릭
4. `extension` 폴더 선택

### 3. Extension 사용
- 브라우저 우측 상단의 Extension 아이콘 클릭
- 롤다방 사이트 상태 확인
- "사이트 열기" 버튼으로 롤다방 사이트 접속

## 🔧 기능

- **API 상태 확인**: 롤다방 백엔드 API 연결 상태 모니터링
- **내전 개수 표시**: 소프트/하드/하이퍼 내전 개수 실시간 확인
- **빠른 접속**: 원클릭으로 롤다방 사이트 접속

## 🛠️ 개발

### 파일 구조
```
extension/
├── manifest.json      # Extension 설정
├── background.js      # 백그라운드 스크립트
├── content.js         # 콘텐츠 스크립트
├── popup.html         # 팝업 UI
├── popup.js           # 팝업 로직
└── README.md          # 이 파일
```

### API 엔드포인트
- `GET /api/health` - API 상태 확인
- `GET /api/matches/by-type/{type}` - 내전 목록 조회

## 🐛 문제 해결

### Extension이 작동하지 않는 경우
1. Chrome 개발자 도구에서 콘솔 에러 확인
2. Extension 페이지에서 오류 메시지 확인
3. Extension 재로드 시도

### API 연결 실패
1. 롤다방 백엔드 서버 상태 확인
2. 네트워크 연결 상태 확인
3. CORS 설정 확인

## 📞 지원

문제가 발생하면 GitHub Issues에 문의해주세요.
