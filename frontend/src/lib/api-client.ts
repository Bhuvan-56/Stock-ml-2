import { apiBaseUrl } from "@/lib/config";
import type { ApiErrorResponse, PredictionRequest, PredictionResponse } from "@/lib/types";

export class ApiClientError extends Error {
  readonly code: string;
  readonly status: number;
  readonly details?: unknown;

  constructor({
    message,
    code,
    status,
    details
  }: {
    message: string;
    code: string;
    status: number;
    details?: unknown;
  }) {
    super(message);
    this.name = "ApiClientError";
    this.code = code;
    this.status = status;
    this.details = details;
  }
}

export async function predictStock(
  request: PredictionRequest
): Promise<PredictionResponse> {
  const response = await fetch(`${apiBaseUrl}/api/v1/predictions/`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json"
    },
    body: JSON.stringify(request),
    cache: "no-store"
  });

  if (!response.ok) {
    let payload: ApiErrorResponse | null = null;

    try {
      payload = (await response.json()) as ApiErrorResponse;
    } catch {
      payload = null;
    }

    throw new ApiClientError({
      message: payload?.error.message ?? "Prediction request failed.",
      code: payload?.error.code ?? "unknown_error",
      status: response.status,
      details: payload?.error.details
    });
  }

  return (await response.json()) as PredictionResponse;
}
