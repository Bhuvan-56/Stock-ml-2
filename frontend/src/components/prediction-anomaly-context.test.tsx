import React from "react";
import { render, screen } from "@testing-library/react";

import { PredictionAnomalyContext } from "@/components/prediction-anomaly-context";

describe("PredictionAnomalyContext", () => {
  it("renders anomaly-day news links when context is available", () => {
    render(
      <PredictionAnomalyContext
        anomalies={[
          {
            date: "2024-05-10",
            actual: 210,
            predicted: 198,
            residual: 12,
            absolute_residual: 12,
            anomaly_threshold: 8,
            news: [
              {
                title: "Company rallies after earnings surprise",
                url: "https://example.com/news",
                source: "example.com",
                summary: "The company beat expectations and raised guidance.",
                published_at: "2024-05-10T13:30:00Z"
              }
            ]
          }
        ]}
        newsStatus="ready"
        symbol="AAPL"
      />
    );

    expect(screen.getByText("What may have moved AAPL?")).toBeInTheDocument();
    expect(screen.getByText("Company rallies after earnings surprise")).toBeInTheDocument();
    expect(screen.getByText(/Missed by/i)).toBeInTheDocument();
  });
});
