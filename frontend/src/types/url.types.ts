export interface URLStatsResponse {
  shortCode: string,
  originalUrl: string,
  clicks: number,
  created_at: string
}

export interface CreateURLRequest {
  url: string
  customCode?: string
}

export interface CreateURLResponse {
  shortCode: string,
  shortUrl: string
}

export interface APIError {
  error: string,
  details?: any
}