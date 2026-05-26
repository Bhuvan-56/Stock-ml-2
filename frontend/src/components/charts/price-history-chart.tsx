"use client";

import { TrendingUp } from "lucide-react";
import { useEffect, useMemo, useRef } from "react";
import type { IChartApi } from "lightweight-charts";

import {
  buildHistoricalCloseSeries,
  buildPredictionSeries,
  getDatedPredictionPoints,
  getValidationWindow
} from "@/components/charts/chart-utils";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { formatDateRange } from "@/lib/format";
import type { HistoricalPricePoint, PredictionPoint } from "@/lib/types";
import { useTheme } from "@/providers/theme-provider";

type PriceHistoryChartProps = {
  data: HistoricalPricePoint[];
  predictions: PredictionPoint[];
};

export function PriceHistoryChart({ data, predictions }: PriceHistoryChartProps) {
  const containerRef = useRef<HTMLDivElement | null>(null);
  const { mounted, theme } = useTheme();
  const historySeries = useMemo(() => buildHistoricalCloseSeries(data), [data]);
  const datedPredictions = useMemo(
    () => getDatedPredictionPoints(predictions),
    [predictions]
  );
  const predictionSeries = useMemo(
    () => buildPredictionSeries(datedPredictions),
    [datedPredictions]
  );
  const validationWindow = useMemo(
    () => getValidationWindow(datedPredictions),
    [datedPredictions]
  );

  const palette = useMemo(
    () =>
      mounted && theme === "dark"
        ? {
            background: "#111922",
            text: "#efe3cf",
            grid: "rgba(239, 227, 207, 0.08)",
            border: "rgba(239, 227, 207, 0.12)",
            historyLine: "#63c4cb",
            top: "rgba(99, 196, 203, 0.32)",
            bottom: "rgba(99, 196, 203, 0.04)",
            actual: "#efe3cf",
            predicted: "#f09a63"
          }
        : {
            background: "#fffdf8",
            text: "#14344a",
            grid: "rgba(20, 52, 74, 0.08)",
            border: "rgba(20, 52, 74, 0.12)",
            historyLine: "#0f5a64",
            top: "rgba(15, 90, 100, 0.24)",
            bottom: "rgba(15, 90, 100, 0.02)",
            actual: "#14344a",
            predicted: "#dd7b45"
          },
    [mounted, theme]
  );

  useEffect(() => {
    let chart: IChartApi | null = null;
    let resizeObserver: ResizeObserver | null = null;
    let cancelled = false;

    async function renderChart() {
      if (!containerRef.current) {
        return;
      }

      const { ColorType, createChart } = await import("lightweight-charts");
      if (cancelled || !containerRef.current) {
        return;
      }

      chart = createChart(containerRef.current, {
        width: containerRef.current.clientWidth,
        height: 320,
        layout: {
          background: {
            type: ColorType.Solid,
            color: palette.background
          },
          textColor: palette.text,
          fontFamily: "var(--font-body)"
        },
        grid: {
          vertLines: {
            color: palette.grid
          },
          horzLines: {
            color: palette.grid
          }
        },
        rightPriceScale: {
          borderColor: palette.border
        },
        timeScale: {
          borderColor: palette.border
        }
      });

      const areaSeries = chart.addAreaSeries({
        lineColor: palette.historyLine,
        topColor: palette.top,
        bottomColor: palette.bottom,
        lineWidth: 3
      });

      areaSeries.setData(historySeries);

      if (predictionSeries.actual.length) {
        const validationActualSeries = chart.addLineSeries({
          color: palette.actual,
          lineWidth: 2,
          priceLineVisible: false,
          title: "Validation actual"
        });

        validationActualSeries.setData(predictionSeries.actual);
      }

      if (predictionSeries.predicted.length) {
        const predictedSeries = chart.addLineSeries({
          color: palette.predicted,
          lineWidth: 3,
          priceLineVisible: false,
          title: "Predicted"
        });

        predictedSeries.setData(predictionSeries.predicted);
      }

      chart.timeScale().fitContent();

      resizeObserver = new ResizeObserver((entries) => {
        const width = entries[0]?.contentRect.width;
        if (!width || !chart) {
          return;
        }

        chart.applyOptions({ width });
      });

      resizeObserver.observe(containerRef.current);
    }

    void renderChart();

    return () => {
      cancelled = true;
      resizeObserver?.disconnect();
      chart?.remove();
    };
  }, [historySeries, palette, predictionSeries.actual, predictionSeries.predicted]);

  return (
    <Card className="h-full bg-card/90">
      <CardHeader className="gap-4 border-b border-border/60 pb-5">
        <div className="flex flex-wrap items-start justify-between gap-3">
          <div>
            <CardTitle>Full price history</CardTitle>
            <CardDescription>
              The complete close series for the returned stock window, with the
              model's validation slice layered on top.
            </CardDescription>
          </div>
          <div className="flex flex-wrap gap-2">
            <Badge variant="outline">{data.length} history points</Badge>
            {predictionSeries.predicted.length ? (
              <Badge variant="accent">Validation overlay active</Badge>
            ) : null}
          </div>
        </div>
        <div className="flex flex-wrap gap-2 text-sm text-muted-foreground">
          <div className="inline-flex items-center gap-2 rounded-full bg-secondary/60 px-3 py-1.5">
            <span
              className="h-2.5 w-2.5 rounded-full"
              style={{ backgroundColor: palette.historyLine }}
            />
            <span>Full close history</span>
          </div>
          {predictionSeries.actual.length ? (
            <div className="inline-flex items-center gap-2 rounded-full bg-secondary/60 px-3 py-1.5">
              <span
                className="h-2.5 w-2.5 rounded-full"
                style={{ backgroundColor: palette.actual }}
              />
              <span>Validation actual</span>
            </div>
          ) : null}
          {predictionSeries.predicted.length ? (
            <div className="inline-flex items-center gap-2 rounded-full bg-secondary/60 px-3 py-1.5">
              <span
                className="h-2.5 w-2.5 rounded-full"
                style={{ backgroundColor: palette.predicted }}
              />
              <span>Model prediction</span>
            </div>
          ) : null}
          <div className="inline-flex items-center gap-2 rounded-full bg-secondary/60 px-3 py-1.5">
            <TrendingUp className="h-4 w-4 text-primary" />
            <span>
              {validationWindow
                ? `${formatDateRange(validationWindow.startDate, validationWindow.endDate)} validation slice`
                : "Showing the full returned review window"}
            </span>
          </div>
        </div>
      </CardHeader>
      <CardContent>
        <div
          ref={containerRef}
          className="h-80 w-full rounded-2xl border border-border/60"
          style={{ backgroundColor: palette.background }}
        />
      </CardContent>
    </Card>
  );
}
