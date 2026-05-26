"use client";

import { create } from "zustand";

type PredictionFormStore = {
  symbol: string;
  startDate: string;
  endDate: string;
  recentSymbols: string[];
  lastSubmittedSymbol: string | null;
  setSymbol: (value: string) => void;
  setStartDate: (value: string) => void;
  setEndDate: (value: string) => void;
  rememberSubmission: (value: string) => void;
};

const DEFAULT_RECENT_SYMBOLS = ["AAPL", "MSFT", "NVDA"];

export const usePredictionFormStore = create<PredictionFormStore>((set) => ({
  symbol: "",
  startDate: "",
  endDate: "",
  recentSymbols: DEFAULT_RECENT_SYMBOLS,
  lastSubmittedSymbol: null,
  setSymbol: (value) => {
    set({ symbol: value });
  },
  setStartDate: (value) => {
    set({ startDate: value });
  },
  setEndDate: (value) => {
    set({ endDate: value });
  },
  rememberSubmission: (value) => {
    const normalizedValue = value.trim().toUpperCase();

    set((state) => ({
      lastSubmittedSymbol: normalizedValue,
      recentSymbols: [normalizedValue, ...state.recentSymbols.filter((item) => item !== normalizedValue)].slice(0, 5)
    }));
  }
}));
