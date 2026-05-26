"use client";

import { LineChart } from "lucide-react";
import { useEffect, useMemo, useRef } from "react";
import type { IChartApi } from "lightweight-charts";

import {
  buildPredictionSeries,
  getDatedPredictionPoints,
  getValidationWindow
} from "@/components/charts/chart-utils";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { formatDateRange } from "@/lib/format";
import type { PredictionPoint } from "@/lib/types";
import { useTheme } from "@/providers/theme-provider";

type PredictionComparisonChartProps = {
  data: PredictionPoint[];
};

export function PredictionComparisonChart({ data }: PredictionComparisonChartProps) {
  const containerRef = useRef<HTMLDivElement | null>(null);
  const { mounted, theme } = useTheme();
  const chartData = useMemo(() => getDatedPredictionPoints(data), [data]);
  const predictionSeries = useMemo(
    () => buildPredictionSeries(chartData),
    [chartData]
  );
  const validationWindow = useMemo(
    () => getValidationWindow(chartData),
    [chartData]
  );

  const palette = useMemo(
    () =>
      mounted && theme === "dark"
        ? {
            background: "#111922",
            text: "#efe3cf",
            grid: "rgba(239, 227, 207, 0.08)",
            border: "rgba(239, 227, 207, 0.12)",
            actual: "#63c4cb",
            predicted: "#f09a63"
          }
        : {
            background: "#fffdf8",
            text: "#14344a",
            grid: "rgba(20, 52, 74, 0.08)",
            border: "rgba(20, 52, 74, 0.12)",
            actual: "#0f5a64",
            predicted: "#dd7b45"
          },
    [mounted, theme]
  );

  useEffect(() => {
    if (!chartData.length) {
      return undefined;
    }

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

      const actualSeries = chart.addLineSeries({
        color: palette.actual,
        lineWidth: 3,
        priceLineVisible: false,
        title: "Actual"
      });
      const predictedSeries = chart.addLineSeries({
        color: palette.predicted,
        lineWidth: 3,
        priceLineVisible: false,
        title: "Predicted"
      });

      actualSeries.setData(predictionSeries.actual);
      predictedSeries.setData(predictionSeries.predicted);

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
  }, [palette, predictionSeries.actual, predictionSeries.predicted]);

  return (
    <Card className="h-full bg-card/90">
      <CardHeader className="gap-4 border-b border-border/60 pb-5">
        <div className="flex flex-wrap items-start justify-between gap-3">
          <div>
            <CardTitle>Validation slice detail</CardTitle>
            <CardDescription>
              A tighter view of the scored portion of the window, isolated for
              miss analysis.
            </CardDescription>
          </div>
          <Badge variant="outline">{chartData.length} validation points</Badge>
        </div>
        <div className="flex flex-wrap gap-2 text-sm text-muted-foreground">
          <div className="inline-flex items-center gap-2 rounded-full bg-secondary/60 px-3 py-1.5">
            <span className="h-2.5 w-2.5 rounded-full" style={{ backgroundColor: palette.actual }} />
            <span>Actual</span>
          </div>
          <div className="inline-flex items-center gap-2 rounded-full bg-secondary/60 px-3 py-1.5">
            <span className="h-2.5 w-2.5 rounded-full" style={{ backgroundColor: palette.predicted }} />
            <span>Predicted</span>
          </div>
          <div className="inline-flex items-center gap-2 rounded-full bg-secondary/60 px-3 py-1.5">
            <LineChart className="h-4 w-4 text-primary" />
            <span>
              {validationWindow
                ? formatDateRange(validationWindow.startDate, validationWindow.endDate)
                : "Look for divergence clusters near anomaly dates."}
            </span>
          </div>
        </div>
      </CardHeader>
      <CardContent>
        {chartData.length ? (
          <div
            ref={containerRef}
            className="h-80 w-full rounded-2xl border border-border/60"
            style={{ backgroundColor: palette.background }}
          />
        ) : (
          <div className="flex h-80 items-center justify-center rounded-2xl border border-dashed border-border bg-muted/50 text-sm text-muted-foreground">
            The prediction response did not include date-based validation points.
          </div>
        )}
      </CardContent>
    </Card>
  );
}
