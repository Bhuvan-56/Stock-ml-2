"use client";

import { useMutation } from "@tanstack/react-query";

import { predictStock } from "@/lib/api-client";
import type { PredictionRequest, PredictionResponse } from "@/lib/types";

export function usePredictStock() {
  return useMutation<PredictionResponse, Error, PredictionRequest>({
    mutationFn: predictStock
  });
}
