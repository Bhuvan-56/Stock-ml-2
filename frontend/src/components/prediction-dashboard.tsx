"use client";

import type { FormEvent } from "react";
import { useState } from "react";

import { PredictionForm } from "@/components/prediction-form";
import { PredictionResults } from "@/components/prediction-results";
import { Card } from "@/components/ui/card";
import { usePredictStock } from "@/hooks/use-predict-stock";
import { ApiClientError } from "@/lib/api-client";
import type { PredictionResponse } from "@/lib/types";
import { usePredictionFormStore } from "@/stores/prediction-form-store";

export function PredictionDashboard() {
  const {
    symbol,
    startDate,
    endDate,
    recentSymbols,
    lastSubmittedSymbol,
    setSymbol,
    setStartDate,
    setEndDate,
    rememberSubmission
  } = usePredictionFormStore();
  const predictionMutation = usePredictStock();
  const [clientError, setClientError] = useState<string | null>(null);
  const [lastSuccessfulResult, setLastSuccessfulResult] = useState<PredictionResponse | undefined>(
    undefined
  );

  function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();

    const normalizedSymbol = symbol.trim().toUpperCase();
    if (!normalizedSymbol) {
      setClientError("Enter a ticker symbol before submitting.");
      return;
    }

    if (startDate && endDate && startDate > endDate) {
      setClientError("Start date must be earlier than or equal to the end date.");
      return;
    }

    setClientError(null);
    setSymbol(normalizedSymbol);
    rememberSubmission(normalizedSymbol);

    predictionMutation.mutate(
      {
        symbol: normalizedSymbol,
        start_date: startDate || undefined,
        end_date: endDate || undefined
      },
      {
        onSuccess: (result) => {
          setLastSuccessfulResult(result);
        }
      }
    );
  }

  const serverError =
    predictionMutation.error instanceof ApiClientError
      ? predictionMutation.error.message
      : predictionMutation.error?.message ?? null;

  return (
    <section className="grid gap-6 xl:grid-cols-[392px_minmax(0,1fr)] xl:items-start">
      <Card className="glass-panel border-primary/10 xl:sticky xl:top-5">
        <PredictionForm
          endDate={endDate}
          isPending={predictionMutation.isPending}
          startDate={startDate}
          suggestions={recentSymbols}
          symbol={symbol}
          onEndDateChange={setEndDate}
          onStartDateChange={setStartDate}
          onSubmit={handleSubmit}
          onSuggestionSelect={setSymbol}
          onSymbolChange={setSymbol}
        />
      </Card>

      <PredictionResults
        errorMessage={clientError ?? serverError}
        focusSymbol={lastSubmittedSymbol ?? (symbol.trim().toUpperCase() || null)}
        isPending={predictionMutation.isPending}
        result={lastSuccessfulResult ?? predictionMutation.data}
      />
    </section>
  );
}
