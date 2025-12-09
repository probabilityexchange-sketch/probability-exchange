/// <reference types="vite/client" />

interface ImportMetaEnv {
  readonly VITE_API_URL?: string
  readonly VITE_WS_URL?: string
  readonly VITE_GA_ID?: string
  readonly VITE_ENABLE_ANALYTICS?: string
  readonly VITE_ENABLE_DEBUG?: string
  readonly VITE_API_RATE_LIMIT?: string
  readonly VITE_API_RATE_WINDOW?: string
}

interface ImportMeta {
  readonly env: ImportMetaEnv
}
