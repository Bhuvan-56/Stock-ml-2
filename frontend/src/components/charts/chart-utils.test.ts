import {
  buildHistoricalCloseSeries,
  buildPredictionSeries,
  getDatedPredictionPoints,
  getValidationWindow
} from "@/components/charts/chart-utils";

describe("chart-utils", () => {
  it("filters and sorts only dated prediction points", () => {
    const points = getDatedPredictionPoints([
      {
        label: "row-2",
        date: "2024-05-15",
        actual: 188.4,
        predicted: 190.1,
        residual: -1.7
      },
      {
        label: "row-1",
        date: null,
        actual: 184.2,
        predicted: 183.8,
        residual: 0.4
      },
      {
        label: "row-0",
        date: "2024-05-10",
        actual: 181.1,
        predicted: 180.2,
        residual: 0.9
      }
    ]);

    expect(points).toHaveLength(2);
    expect(points.map((point) => point.date)).toEqual([
      "2024-05-10",
      "2024-05-15"
    ]);
  });

  it("builds full-history and validation overlay series", () => {
    const historySeries = buildHistoricalCloseSeries([
      {
        date: "2024-05-09",
        open: 178.1,
        high: 180.4,
        low: 177.9,
        close: 179.8,
        volume: 100
      },
      {
        date: "2024-05-10",
        open: 180.1,
        high: 182.7,
        low: 179.4,
        close: 181.1,
        volume: 120
      }
    ]);
    const datedPredictions = getDatedPredictionPoints([
      {
        label: "row-0",
        date: "2024-05-10",
        actual: 181.1,
        predicted: 180.2,
        residual: 0.9
      },
      {
        label: "row-1",
        date: "2024-05-15",
        actual: 188.4,
        predicted: 190.1,
        residual: -1.7
      }
    ]);
    const overlaySeries = buildPredictionSeries(datedPredictions);

    expect(historySeries).toEqual([
      { time: "2024-05-09", value: 179.8 },
      { time: "2024-05-10", value: 181.1 }
    ]);
    expect(overlaySeries.actual).toEqual([
      { time: "2024-05-10", value: 181.1 },
      { time: "2024-05-15", value: 188.4 }
    ]);
    expect(overlaySeries.predicted).toEqual([
      { time: "2024-05-10", value: 180.2 },
      { time: "2024-05-15", value: 190.1 }
    ]);
    expect(getValidationWindow(datedPredictions)).toEqual({
      startDate: "2024-05-10",
      endDate: "2024-05-15"
    });
  });
});
