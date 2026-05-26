const currencyFormatter = new Intl.NumberFormat("en-US", {
  style: "currency",
  currency: "USD",
  maximumFractionDigits: 2
});

const signedCurrencyFormatter = new Intl.NumberFormat("en-US", {
  style: "currency",
  currency: "USD",
  maximumFractionDigits: 2,
  signDisplay: "always"
});

const numberFormatter = new Intl.NumberFormat("en-US", {
  maximumFractionDigits: 3
});

const integerFormatter = new Intl.NumberFormat("en-US");

export function formatCurrency(value: number): string {
  return currencyFormatter.format(value);
}

export function formatSignedCurrency(value: number): string {
  return signedCurrencyFormatter.format(value);
}

export function formatMetric(value: number): string {
  return numberFormatter.format(value);
}

export function formatInteger(value: number): string {
  return integerFormatter.format(value);
}

export function formatDateLabel(value: string): string {
  const parsedDate = new Date(`${value}T00:00:00Z`);
  return new Intl.DateTimeFormat("en-US", {
    month: "short",
    day: "numeric",
    year: "numeric",
    timeZone: "UTC"
  }).format(parsedDate);
}

export function formatDateRange(startDate: string, endDate: string): string {
  return `${formatDateLabel(startDate)} to ${formatDateLabel(endDate)}`;
}

export function formatDateTimeLabel(value: string | Date): string {
  const parsedDate = value instanceof Date ? value : new Date(value);
  return new Intl.DateTimeFormat("en-US", {
    month: "short",
    day: "numeric",
    year: "numeric",
    hour: "numeric",
    minute: "2-digit"
  }).format(parsedDate);
}
