/// <reference types="vite/client" />

interface ImportMetaEnv {
  readonly VITE_API_URL: string
  readonly VITE_WS_URL: string
  readonly DEV: boolean
  readonly PROD: boolean
  readonly SSR: boolean
  // 다른 환경 변수들...
}

interface ImportMeta {
  readonly env: ImportMetaEnv
}
