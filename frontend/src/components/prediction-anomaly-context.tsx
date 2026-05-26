"use client";

import {
  ArrowUpRight,
  CircleAlert,
  Newspaper,
  Sparkles
} from "lucide-react";

import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { formatCurrency, formatDateLabel, formatDateTimeLabel, formatSignedCurrency } from "@/lib/format";
import type { PredictionAnomaly, PredictionMetadata } from "@/lib/types";

type PredictionAnomalyContextProps = {
  anomalies: PredictionAnomaly[];
  newsStatus: PredictionMetadata["news_status"];
  symbol: string;
};

function getStatusCopy(
  newsStatus: PredictionMetadata["news_status"]
): string {
  if (newsStatus === "disabled") {
    return "Add a Tavily API key to surface same-day market context for each major miss.";
  }

  if (newsStatus === "unavailable") {
    return "Prediction anomalies were detected, but the news lookup was temporarily unavailable.";
  }

  return "The cards below connect the biggest misses to same-day market coverage.";
}

export function PredictionAnomalyContext({
  anomalies,
  newsStatus,
  symbol
}: PredictionAnomalyContextProps) {
  if (!anomalies.length) {
    return (
      <Card className="bg-card/90">
        <CardHeader className="pb-4">
          <div className="flex items-center gap-3">
            <div className="flex h-11 w-11 items-center justify-center rounded-2xl bg-primary/10 text-primary">
              <Sparkles className="h-5 w-5" />
            </div>
            <div>
              <CardTitle>No major misses detected</CardTitle>
              <CardDescription>
                The validation window did not produce large residuals worth a separate news review.
              </CardDescription>
            </div>
          </div>
        </CardHeader>
        <CardContent>
          <div className="rounded-[1.4rem] border border-border/70 bg-background/55 p-4 text-sm leading-6 text-muted-foreground">
            {newsStatus === "disabled"
              ? "The anomaly workflow is ready. Add your Tavily API key later if you want automatic same-day market context."
              : "This run stayed within a tighter error band, so the UI is keeping the focus on charts and metrics."}
          </div>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card className="bg-card/92">
      <CardHeader className="gap-4 border-b border-border/60 pb-5">
        <div className="flex flex-wrap items-start justify-between gap-4">
          <div className="flex items-start gap-3">
            <div className="flex h-11 w-11 items-center justify-center rounded-2xl bg-accent/12 text-accent">
              <Newspaper className="h-5 w-5" />
            </div>
            <div className="space-y-1">
              <CardTitle>What may have moved {symbol}?</CardTitle>
              <CardDescription>{getStatusCopy(newsStatus)}</CardDescription>
            </div>
          </div>
          <div className="flex flex-wrap gap-2">
            <Badge variant="destructive">
              {anomalies.length} anomaly {anomalies.length === 1 ? "day" : "days"}
            </Badge>
            <Badge variant={newsStatus === "ready" ? "accent" : "outline"}>
              {newsStatus === "ready"
                ? "News context linked"
                : newsStatus === "unavailable"
                  ? "News unavailable"
                  : "News disabled"}
            </Badge>
          </div>
        </div>
      </CardHeader>
      <CardContent className="grid gap-4">
        {anomalies.map((anomaly) => {
          const movedHigherThanModel = anomaly.residual > 0;

          return (
            <article
              key={anomaly.date}
              className="rounded-[1.5rem] border border-border/70 bg-background/50 p-4"
            >
              <div className="flex flex-wrap items-start justify-between gap-3">
                <div>
                  <p className="text-[11px] font-semibold uppercase tracking-[0.24em] text-muted-foreground">
                    {formatDateLabel(anomaly.date)}
                  </p>
                  <h3 className="mt-2 text-lg font-semibold text-foreground">
                    {movedHigherThanModel ? "Closed above model expectations" : "Closed below model expectations"}
                  </h3>
                  <p className="mt-1 text-sm leading-6 text-muted-foreground">
                    Missed by {formatSignedCurrency(anomaly.residual)} against an anomaly threshold of{" "}
                    {formatCurrency(anomaly.anomaly_threshold)}.
                  </p>
                </div>
                <div className="grid min-w-[200px] gap-2 rounded-[1.25rem] border border-border/60 bg-card/70 p-3 text-sm">
                  <div className="flex items-center justify-between gap-3">
                    <span className="text-muted-foreground">Actual close</span>
                    <span className="font-medium text-foreground">
                      {formatCurrency(anomaly.actual)}
                    </span>
                  </div>
                  <div className="flex items-center justify-between gap-3">
                    <span className="text-muted-foreground">Predicted close</span>
                    <span className="font-medium text-foreground">
                      {formatCurrency(anomaly.predicted)}
                    </span>
                  </div>
                  <div className="flex items-center justify-between gap-3">
                    <span className="text-muted-foreground">Absolute miss</span>
                    <span className="font-medium text-foreground">
                      {formatCurrency(anomaly.absolute_residual)}
                    </span>
                  </div>
                </div>
              </div>

              {anomaly.news.length ? (
                <div className="mt-4 grid gap-3">
                  {anomaly.news.map((article) => (
                    <a
                      key={`${anomaly.date}-${article.url}`}
                      className="group rounded-[1.25rem] border border-border/70 bg-card/72 p-4 transition hover:border-primary/30 hover:bg-card"
                      href={article.url}
                      rel="noreferrer"
                      target="_blank"
                    >
                      <div className="flex items-start justify-between gap-3">
                        <div>
                          <p className="text-[11px] font-semibold uppercase tracking-[0.22em] text-muted-foreground">
                            {article.source}
                            {article.published_at
                              ? ` • ${formatDateTimeLabel(article.published_at)}`
                              : ""}
                          </p>
                          <h4 className="mt-2 text-base font-semibold text-foreground transition group-hover:text-primary">
                            {article.title}
                          </h4>
                        </div>
                        <ArrowUpRight className="mt-0.5 h-4 w-4 shrink-0 text-muted-foreground transition group-hover:text-primary" />
                      </div>
                      {article.summary ? (
                        <p className="mt-2 text-sm leading-6 text-muted-foreground">
                          {article.summary}
                        </p>
                      ) : null}
                    </a>
                  ))}
                </div>
              ) : (
                <div className="mt-4 flex items-start gap-3 rounded-[1.25rem] border border-dashed border-border/70 bg-card/55 p-4 text-sm leading-6 text-muted-foreground">
                  <CircleAlert className="mt-0.5 h-4 w-4 shrink-0 text-muted-foreground" />
                  <p>
                    {newsStatus === "ready"
                      ? "No same-day news articles were returned for this anomaly date."
                      : newsStatus === "unavailable"
                        ? "News lookup failed for this run, so the anomaly is shown without external context."
                        : "Enable Tavily in the backend environment to attach same-day news to this anomaly."}
                  </p>
                </div>
              )}
            </article>
          );
        })}
      </CardContent>
    </Card>
  );
}
