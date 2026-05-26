import React from "react";
import { render, screen } from "@testing-library/react";

import { PredictionResults } from "@/components/prediction-results";

describe("PredictionResults", () => {
  it("renders the empty state when no prediction has been requested", () => {
    render(
      <PredictionResults
        errorMessage={null}
        focusSymbol={null}
        isPending={false}
        result={undefined}
      />
    );

    expect(screen.getByText("Ready when you are")).toBeInTheDocument();
    expect(
      screen.getByText(/Submit a stock symbol to see the full response path/i)
    ).toBeInTheDocument();
  });
});
