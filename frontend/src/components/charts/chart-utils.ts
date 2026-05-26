"use client";

import type { HistoricalPricePoint, PredictionPoint } from "@/lib/types";

export type DatedPredictionPoint = PredictionPoint & { date: string };

export type ChartSeriesPoint = {
  time: string;
  value: number;
};

export type ValidationWindow = {
  startDate: string;
  endDate: string;
};

export function getDatedPredictionPoints(
  points: PredictionPoint[]
): DatedPredictionPoint[] {
  return points
    .filter((point): point is DatedPredictionPoint => point.date !== null)
    .slice()
    .sort((left, right) => left.date.localeCompare(right.date));
}

export function getValidationWindow(
  points: DatedPredictionPoint[]
): ValidationWindow | null {
  if (!points.length) {
    return null;
  }

  return {
    startDate: points[0].date,
    endDate: points[points.length - 1].date
  };
}

export function buildHistoricalCloseSeries(
  points: HistoricalPricePoint[]
): ChartSeriesPoint[] {
  return points.map((point) => ({
    time: point.date,
    value: point.close
  }));
}

export function buildPredictionSeries(
  points: DatedPredictionPoint[]
): {
  actual: ChartSeriesPoint[];
  predicted: ChartSeriesPoint[];
} {
  return {
    actual: points.map((point) => ({
      time: point.date,
      value: point.actual
    })),
    predicted: points.map((point) => ({
      time: point.date,
      value: point.predicted
    }))
  };
}
