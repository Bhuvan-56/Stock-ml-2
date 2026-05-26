"use client";

import {
  Activity,
  AlertTriangle,
  Database,
  Gauge,
  Layers3,
  LoaderCircle,
  Newspaper
} from "lucide-react";

import { MetricCard } from "@/components/metric-card";
import { PredictionAnomalyContext } from "@/components/prediction-anomaly-context";
import { PredictionComparisonChart } from "@/components/charts/prediction-comparison-chart";
import { PriceHistoryChart } from "@/components/charts/price-history-chart";
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import {
  formatCurrency,
  formatDateRange,
  formatInteger,
  formatMetric,
  formatSignedCurrency
} from "@/lib/format";
import type { PredictionResponse } from "@/lib/types";

type PredictionResultsProps = {
  result: PredictionResponse | undefined;
  isPending: boolean;
  errorMessage: string | null;
  focusSymbol: string | null;
};

function getNewsBadgeVariant(
  newsStatus: PredictionResponse["metadata"]["news_status"]
): "accent" | "destructive" | "outline" {
  if (newsStatus === "ready") {
    return "accent";
  }

  if (newsStatus === "unavailable") {
    return "destructive";
  }

  return "outline";
}

function getNewsBadgeLabel(newsStatus: PredictionResponse["metadata"]["news_status"]): string {
  if (newsStatus === "ready") {
    return "News context on";
  }

  if (newsStatus === "unavailable") {
    return "News context unavailable";
  }

  return "News context off";
}

export function PredictionResults({
  result,
  isPending,
  errorMessage,
  focusSymbol
}: PredictionResultsProps) {
  if (!result && isPending) {
    return (
      <Card className="glass-panel border-primary/10">
        <CardContent className="flex min-h-[440px] flex-col items-center justify-center gap-4 p-6 text-center">
          <div className="flex h-16 w-16 items-center justify-center rounded-full bg-primary/10 text-primary">
            <LoaderCircle className="h-7 w-7 animate-spin" />
          </div>
          <div className="space-y-2">
            <h2 className="text-2xl font-semibold">Building the prediction response</h2>
            <p className="max-w-md text-sm leading-6 text-muted-foreground">
              The backend is fetching market history, engineering features, scoring the
              validation window, and preparing anomaly-day context for{" "}
              {focusSymbol ?? "your ticker"}.
            </p>
          </div>
        </CardContent>
      </Card>
    );
  }

  if (!result) {
    return (
      <Card className="glass-panel border-primary/10">
        <CardContent className="grid min-h-[460px] gap-6 p-6 lg:grid-cols-[minmax(0,1fr)_minmax(260px,0.78fr)] lg:items-center">
          <div className="space-y-6 text-center lg:text-left">
            {errorMessage ? (
              <Alert className="max-w-xl text-left">
                <div className="flex items-start gap-3">
                  <AlertTriangle className="mt-0.5 h-5 w-5 shrink-0" />
                  <div>
                    <AlertTitle>Prediction request failed</AlertTitle>
                    <AlertDescription>{errorMessage}</AlertDescription>
                  </div>
                </div>
              </Alert>
            ) : null}
            <div className="flex justify-center lg:justify-start">
              <div className="flex h-16 w-16 items-center justify-center rounded-full bg-primary/10 text-primary">
                <Activity className="h-7 w-7" />
              </div>
            </div>
            <div className="space-y-2">
              <h2 className="text-2xl font-semibold">Ready when you are</h2>
              <p className="max-w-xl text-sm leading-6 text-muted-foreground">
                Submit a stock symbol to see the full response path: price history, validation
                predictions, model metrics, and anomaly-day market context.
              </p>
            </div>
          </div>

          <div className="grid gap-3">
            {[
              "Metrics arrive with MAE, RMSE, and split sizes.",
              "Price history and validation outputs render in chart cards.",
              "Large misses can trigger same-day news context in the results view."
            ].map((item) => (
              <div
                key={item}
                className="rounded-[1.4rem] border border-border/70 bg-card/75 p-4 text-sm leading-6 text-muted-foreground"
              >
                {item}
              </div>
            ))}
          </div>
        </CardContent>
      </Card>
    );
  }

  const largestAnomaly = result.anomalies[0];

  return (
    <div className="flex flex-col gap-5">
      {errorMessage ? (
        <Alert>
          <div className="flex items-start gap-3">
            <AlertTriangle className="mt-0.5 h-5 w-5 shrink-0" />
            <div>
              <AlertTitle>Latest request failed</AlertTitle>
              <AlertDescription>
                {errorMessage}. The last successful result is still displayed below.
              </AlertDescription>
            </div>
          </div>
        </Alert>
      ) : null}

      <Card className="glass-panel border-primary/10">
        <CardHeader className="gap-5 border-b border-border/60 pb-5 lg:grid lg:grid-cols-[minmax(0,1fr)_340px] lg:items-start">
          <div className="space-y-4">
            <div className="flex flex-wrap items-center gap-2">
              <Badge>{result.symbol}</Badge>
              <Badge variant="outline">{result.metadata.model_name}</Badge>
              <Badge variant="outline">{result.metadata.source}</Badge>
              {result.metadata.cached ? <Badge variant="accent">Cache hit</Badge> : null}
              {result.metadata.anomaly_count ? (
                <Badge variant="destructive">
                  {result.metadata.anomaly_count} anomaly {result.metadata.anomaly_count === 1 ? "day" : "days"}
                </Badge>
              ) : (
                <Badge variant="secondary">Stable validation window</Badge>
              )}
              <Badge variant={getNewsBadgeVariant(result.metadata.news_status)}>
                {getNewsBadgeLabel(result.metadata.news_status)}
              </Badge>
              {isPending ? <Badge variant="secondary">Refreshing</Badge> : null}
            </div>
            <div className="space-y-1">
              <CardTitle className="text-3xl">
                {formatDateRange(
                  result.stock_window.actual_start_date,
                  result.stock_window.actual_end_date
                )}
              </CardTitle>
              <CardDescription>
                {result.stock_window.row_count} rows of daily market history with{" "}
                {result.metadata.prediction_count} validation predictions returned.
              </CardDescription>
            </div>
          </div>
          <div className="grid gap-3 rounded-[1.5rem] border border-border/70 bg-card/76 p-4 text-sm">
            <div className="rounded-[1.2rem] border border-border/60 bg-background/55 p-3">
              <p className="font-medium text-foreground">Last close</p>
              <p className="mt-1 text-muted-foreground">
                {formatCurrency(result.price_history[result.price_history.length - 1]?.close ?? 0)}
              </p>
            </div>
            <div className="rounded-[1.2rem] border border-border/60 bg-background/55 p-3">
              <p className="font-medium text-foreground">Largest miss</p>
              <p className="mt-1 text-muted-foreground">
                {largestAnomaly
                  ? formatSignedCurrency(largestAnomaly.residual)
                  : "Within the normal validation band"}
              </p>
            </div>
            <div className="rounded-[1.2rem] border border-border/60 bg-background/55 p-3">
              <p className="font-medium text-foreground">News context</p>
              <p className="mt-1 text-muted-foreground">
                {result.metadata.news_status === "ready"
                  ? "Attached to anomaly days"
                  : result.metadata.news_status === "unavailable"
                    ? "Unavailable for this run"
                    : "Disabled until a Tavily key is configured"}
              </p>
            </div>
          </div>
        </CardHeader>
      </Card>

      <section className="grid gap-4 md:grid-cols-2 xl:grid-cols-3 2xl:grid-cols-5">
        <MetricCard
          label="MAE"
          value={formatMetric(result.metrics.mae)}
          hint="Average absolute prediction error on the validation window."
        />
        <MetricCard
          label="RMSE"
          value={formatMetric(result.metrics.rmse)}
          hint="Root mean squared error across validation predictions."
        />
        <MetricCard
          label="Training rows"
          value={formatInteger(result.metrics.training_rows)}
          hint="Rows used for model fitting after feature engineering."
        />
        <MetricCard
          label="Validation rows"
          value={formatInteger(result.metrics.validation_rows)}
          hint="Rows reserved for the response chart and metrics."
        />
        <MetricCard
          label="Feature count"
          value={formatInteger(result.metrics.feature_count)}
          hint="Engineered inputs passed into the model trainer."
        />
      </section>

      <section className="grid gap-5">
        <PriceHistoryChart
          data={result.price_history}
          predictions={result.predictions}
        />
        <PredictionComparisonChart data={result.predictions} />
      </section>

      <section className="grid gap-5 2xl:grid-cols-[minmax(0,1.16fr)_minmax(320px,0.84fr)]">
        <PredictionAnomalyContext
          anomalies={result.anomalies}
          newsStatus={result.metadata.news_status}
          symbol={result.symbol}
        />

        <div className="grid gap-5">
          <Card className="bg-card/90">
            <CardHeader className="pb-4">
              <div className="flex items-start gap-3">
                <div className="flex h-10 w-10 items-center justify-center rounded-2xl bg-primary/10 text-primary">
                  <Database className="h-5 w-5" />
                </div>
                <div>
                  <CardTitle>Request summary</CardTitle>
                  <CardDescription>Useful backend metadata for debugging and review.</CardDescription>
                </div>
              </div>
            </CardHeader>
            <CardContent className="space-y-4 text-sm">
              <div className="flex items-start gap-3">
                <Database className="mt-0.5 h-4 w-4 text-muted-foreground" />
                <div>
                  <p className="font-medium text-foreground">Requested window</p>
                  <p className="text-muted-foreground">
                    {formatDateRange(
                      result.stock_window.requested_start_date,
                      result.stock_window.requested_end_date
                    )}
                  </p>
                </div>
              </div>
              <div className="flex items-start gap-3">
                <Gauge className="mt-0.5 h-4 w-4 text-muted-foreground" />
                <div>
                  <p className="font-medium text-foreground">Generated at</p>
                  <p className="text-muted-foreground">
                    {new Date(result.metadata.generated_at).toLocaleString()}
                  </p>
                </div>
              </div>
              <div className="flex items-start gap-3">
                <Layers3 className="mt-0.5 h-4 w-4 text-muted-foreground" />
                <div>
                  <p className="font-medium text-foreground">Interval</p>
                  <p className="text-muted-foreground">{result.stock_window.interval}</p>
                </div>
              </div>
              <div className="flex items-start gap-3">
                <Newspaper className="mt-0.5 h-4 w-4 text-muted-foreground" />
                <div>
                  <p className="font-medium text-foreground">News provider</p>
                  <p className="text-muted-foreground">
                    {result.metadata.news_provider ?? "Not configured"}
                  </p>
                </div>
              </div>
            </CardContent>
          </Card>

          <Card className="bg-card/90">
            <CardHeader className="pb-4">
              <CardTitle>Feature columns</CardTitle>
              <CardDescription>
                These engineered fields were used by the backend training pipeline.
              </CardDescription>
            </CardHeader>
            <CardContent className="flex flex-wrap gap-2">
              {result.feature_columns.map((feature) => (
                <Badge key={feature} variant="outline">
                  {feature}
                </Badge>
              ))}
            </CardContent>
          </Card>
        </div>
      </section>
    </div>
  );
}
