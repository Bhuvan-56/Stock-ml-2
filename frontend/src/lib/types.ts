export type PredictionRequest = {
  symbol: string;
  start_date?: string;
  end_date?: string;
};

export type ApiErrorResponse = {
  error: {
    code: string;
    message: string;
    details?: unknown;
  };
};

export type PredictionStockWindow = {
  requested_start_date: string;
  requested_end_date: string;
  actual_start_date: string;
  actual_end_date: string;
  interval: string;
  row_count: number;
};

export type PredictionMetrics = {
  mae: number;
  rmse: number;
  training_rows: number;
  validation_rows: number;
  feature_count: number;
};

export type HistoricalPricePoint = {
  date: string;
  open: number;
  high: number;
  low: number;
  close: number;
  volume: number;
};

export type PredictionPoint = {
  label: string;
  date: string | null;
  actual: number;
  predicted: number;
  residual: number;
};

export type NewsArticle = {
  title: string;
  url: string;
  source: string;
  summary: string | null;
  published_at: string | null;
};

export type PredictionAnomaly = {
  date: string;
  actual: number;
  predicted: number;
  residual: number;
  absolute_residual: number;
  anomaly_threshold: number;
  news: NewsArticle[];
};

export type PredictionMetadata = {
  model_name: string;
  target_column: string;
  source: string;
  generated_at: string;
  cached: boolean;
  prediction_count: number;
  anomaly_count: number;
  news_status: "disabled" | "ready" | "unavailable";
  news_provider: string | null;
};

export type PredictionResponse = {
  symbol: string;
  stock_window: PredictionStockWindow;
  feature_columns: string[];
  metrics: PredictionMetrics;
  price_history: HistoricalPricePoint[];
  predictions: PredictionPoint[];
  anomalies: PredictionAnomaly[];
  metadata: PredictionMetadata;
};
