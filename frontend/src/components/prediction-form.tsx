"use client";

import { Clock3, RotateCcw, Search, ShieldCheck, Sparkles } from "lucide-react";
import type { FormEvent } from "react";

import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { DatePickerField } from "@/components/ui/date-picker-field";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { formatDateLabel } from "@/lib/format";

type PredictionFormProps = {
  symbol: string;
  startDate: string;
  endDate: string;
  suggestions: string[];
  isPending: boolean;
  onSymbolChange: (value: string) => void;
  onStartDateChange: (value: string) => void;
  onEndDateChange: (value: string) => void;
  onSuggestionSelect: (value: string) => void;
  onSubmit: (event: FormEvent<HTMLFormElement>) => void;
};

export function PredictionForm({
  symbol,
  startDate,
  endDate,
  suggestions,
  isPending,
  onSymbolChange,
  onStartDateChange,
  onEndDateChange,
  onSuggestionSelect,
  onSubmit
}: PredictionFormProps) {
  const windowSummary =
    startDate && endDate
      ? `${formatDateLabel(startDate)} to ${formatDateLabel(endDate)}`
      : startDate
        ? `From ${formatDateLabel(startDate)} onward`
        : endDate
          ? `Through ${formatDateLabel(endDate)}`
          : "Using the default trailing history window";

  return (
    <>
      <CardHeader className="space-y-5 border-b border-border/60 pb-5">
        <div className="flex items-start justify-between gap-4">
          <div className="flex items-center gap-3">
            <div className="flex h-12 w-12 items-center justify-center rounded-2xl bg-primary/10 text-primary">
              <Sparkles className="h-5 w-5" />
            </div>
            <div>
              <CardTitle>Run a prediction</CardTitle>
              <CardDescription>
                Choose a ticker and narrow the market window with a faster calendar flow.
              </CardDescription>
            </div>
          </div>
          <Badge className="shrink-0" variant="accent">
            Local-ready
          </Badge>
        </div>

        <div className="grid gap-3 sm:grid-cols-2">
          <div className="rounded-[1.35rem] border border-primary/10 bg-primary/6 p-4">
            <div className="mb-3 flex h-9 w-9 items-center justify-center rounded-2xl bg-primary/12 text-primary">
              <Clock3 className="h-4 w-4" />
            </div>
            <p className="text-sm font-semibold text-foreground">Year-aware calendar</p>
            <p className="mt-1 text-sm leading-6 text-muted-foreground">
              Jump directly to the right month and year instead of stepping through the calendar one month at a time.
            </p>
          </div>
          <div className="rounded-[1.35rem] border border-accent/15 bg-accent/6 p-4">
            <div className="mb-3 flex h-9 w-9 items-center justify-center rounded-2xl bg-accent/12 text-accent">
              <ShieldCheck className="h-4 w-4" />
            </div>
            <p className="text-sm font-semibold text-foreground">Typed review flow</p>
            <p className="mt-1 text-sm leading-6 text-muted-foreground">
              The result view keeps metrics, validation charts, and anomaly-day context in one typed response.
            </p>
          </div>
        </div>
      </CardHeader>
      <CardContent className="space-y-5">
        <form className="space-y-5" onSubmit={onSubmit}>
          <div className="space-y-2">
            <Label htmlFor="symbol">Ticker symbol</Label>
            <div className="relative">
              <Search className="pointer-events-none absolute left-4 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
              <Input
                id="symbol"
                autoComplete="off"
                className="pl-10 uppercase"
                inputMode="text"
                maxLength={16}
                placeholder="AAPL"
                value={symbol}
                onChange={(event) => {
                  onSymbolChange(event.target.value.toUpperCase());
                }}
              />
            </div>
            <p className="text-xs leading-5 text-muted-foreground">
              Try a US ticker or index symbol like AAPL, MSFT, NVDA, or ^GSPC.
            </p>
          </div>

          <div className="space-y-3 rounded-[1.5rem] border border-border/70 bg-card/55 p-4">
            <div className="flex items-start justify-between gap-3">
              <div>
                <p className="text-sm font-semibold text-foreground">Date window</p>
                <p className="text-xs leading-5 text-muted-foreground">
                  Use the calendar controls to target a specific training window quickly.
                </p>
              </div>
              {startDate || endDate ? (
                <Button
                  className="h-9 gap-2 rounded-full"
                  size="sm"
                  variant="ghost"
                  onClick={() => {
                    onStartDateChange("");
                    onEndDateChange("");
                  }}
                >
                  <RotateCcw className="h-4 w-4" />
                  Reset range
                </Button>
              ) : null}
            </div>

            <div className="grid gap-3 sm:grid-cols-2">
              <DatePickerField
                description="Optional lower bound for history."
                id="start-date"
                label="Start date"
                maxValue={endDate || undefined}
                placeholder="Select start date"
                value={startDate}
                onChange={onStartDateChange}
              />
              <DatePickerField
                description="Optional upper bound for history."
                id="end-date"
                label="End date"
                minValue={startDate || undefined}
                placeholder="Select end date"
                value={endDate}
                onChange={onEndDateChange}
              />
            </div>
          </div>

          <div className="space-y-3 rounded-[1.5rem] border border-border/70 bg-card/55 p-4">
            <div className="flex items-center justify-between gap-3">
              <p className="text-sm font-semibold text-foreground">Quick picks</p>
              <p className="text-xs text-muted-foreground">Common local demo tickers</p>
            </div>
            <div className="flex flex-wrap gap-2">
              {suggestions.map((suggestion) => (
                <Button
                  key={suggestion}
                  size="sm"
                  className="rounded-full"
                  variant={symbol === suggestion ? "secondary" : "outline"}
                  onClick={() => {
                    onSuggestionSelect(suggestion);
                  }}
                >
                  {suggestion}
                </Button>
              ))}
            </div>
          </div>

          <div className="hero-panel rounded-[1.65rem] p-4 shadow-soft">
            <p className="text-[11px] uppercase tracking-[0.28em] hero-panel-muted">Submission</p>
            <p className="mt-2 text-sm font-medium">Window summary</p>
            <p className="mt-1 text-sm leading-6 hero-panel-muted">{windowSummary}</p>

            <Button
              className="mt-4 w-full bg-accent text-accent-foreground hover:bg-accent/92"
              size="lg"
              type="submit"
              disabled={isPending}
            >
              {isPending ? "Generating prediction..." : "Generate prediction"}
            </Button>
          </div>
        </form>
      </CardContent>
    </>
  );
}
