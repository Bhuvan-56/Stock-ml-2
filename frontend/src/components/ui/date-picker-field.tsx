"use client";

import {
  CalendarDays,
  ChevronDown,
  ChevronLeft,
  ChevronRight,
  X
} from "lucide-react";
import { useEffect, useMemo, useRef, useState } from "react";

import { Button } from "@/components/ui/button";
import { Label } from "@/components/ui/label";
import { cn } from "@/lib/utils";

type DatePickerFieldProps = {
  id: string;
  label: string;
  value: string;
  placeholder: string;
  description?: string;
  minValue?: string;
  maxValue?: string;
  onChange: (value: string) => void;
};

type CalendarCell = {
  date: Date;
  isCurrentMonth: boolean;
};

const weekdayFormatter = new Intl.DateTimeFormat("en-US", {
  weekday: "short",
  timeZone: "UTC"
});

const displayFormatter = new Intl.DateTimeFormat("en-US", {
  month: "short",
  day: "numeric",
  year: "numeric",
  timeZone: "UTC"
});

const accessibleDateFormatter = new Intl.DateTimeFormat("en-US", {
  month: "long",
  day: "numeric",
  year: "numeric",
  timeZone: "UTC"
});

const monthLabelFormatter = new Intl.DateTimeFormat("en-US", {
  month: "long",
  timeZone: "UTC"
});

const weekdayLabels = Array.from({ length: 7 }, (_, index) =>
  weekdayFormatter
    .format(new Date(Date.UTC(2024, 0, 7 + index)))
    .slice(0, 2)
    .toUpperCase()
);

const monthOptions = Array.from({ length: 12 }, (_, index) => ({
  value: index,
  label: monthLabelFormatter.format(new Date(Date.UTC(2024, index, 1)))
}));

function parseIsoDate(value: string | undefined): Date | null {
  if (!value) {
    return null;
  }

  const match = /^(\d{4})-(\d{2})-(\d{2})$/.exec(value);
  if (!match) {
    return null;
  }

  const year = Number(match[1]);
  const month = Number(match[2]) - 1;
  const day = Number(match[3]);
  const parsedDate = new Date(Date.UTC(year, month, day));

  if (
    parsedDate.getUTCFullYear() !== year ||
    parsedDate.getUTCMonth() !== month ||
    parsedDate.getUTCDate() !== day
  ) {
    return null;
  }

  return parsedDate;
}

function formatIsoDate(value: Date): string {
  const year = value.getUTCFullYear();
  const month = String(value.getUTCMonth() + 1).padStart(2, "0");
  const day = String(value.getUTCDate()).padStart(2, "0");
  return `${year}-${month}-${day}`;
}

function addUtcDays(value: Date, amount: number): Date {
  const nextValue = new Date(value);
  nextValue.setUTCDate(nextValue.getUTCDate() + amount);
  return nextValue;
}

function shiftUtcMonth(value: Date, amount: number): Date {
  return new Date(Date.UTC(value.getUTCFullYear(), value.getUTCMonth() + amount, 1));
}

function buildCalendarCells(visibleMonth: Date): CalendarCell[] {
  const firstDayOfMonth = new Date(
    Date.UTC(visibleMonth.getUTCFullYear(), visibleMonth.getUTCMonth(), 1)
  );
  const gridStartDate = addUtcDays(firstDayOfMonth, -firstDayOfMonth.getUTCDay());

  return Array.from({ length: 42 }, (_, index) => {
    const date = addUtcDays(gridStartDate, index);

    return {
      date,
      isCurrentMonth: date.getUTCMonth() === visibleMonth.getUTCMonth()
    };
  });
}

function buildYearOptions({
  selectedDate,
  minDate,
  maxDate,
  today
}: {
  selectedDate: Date | null;
  minDate: Date | null;
  maxDate: Date | null;
  today: Date;
}): number[] {
  const todayYear = today.getUTCFullYear();
  const selectedYear = selectedDate?.getUTCFullYear() ?? todayYear;
  const minYear = minDate?.getUTCFullYear() ?? Math.min(selectedYear, todayYear - 25);
  const maxYear = maxDate?.getUTCFullYear() ?? Math.max(selectedYear, todayYear);

  return Array.from({ length: maxYear - minYear + 1 }, (_, index) => minYear + index);
}

function isSameUtcDate(left: Date | null, right: Date): boolean {
  return left !== null && left.getTime() === right.getTime();
}

function isDateOutOfRange(value: Date, minDate: Date | null, maxDate: Date | null): boolean {
  if (minDate && value.getTime() < minDate.getTime()) {
    return true;
  }

  if (maxDate && value.getTime() > maxDate.getTime()) {
    return true;
  }

  return false;
}

function formatDisplayDate(value: Date | null): string {
  return value ? displayFormatter.format(value) : "";
}

export function DatePickerField({
  id,
  label,
  value,
  placeholder,
  description,
  minValue,
  maxValue,
  onChange
}: DatePickerFieldProps) {
  const rootRef = useRef<HTMLDivElement | null>(null);
  const selectedDate = useMemo(() => parseIsoDate(value), [value]);
  const minDate = useMemo(() => parseIsoDate(minValue), [minValue]);
  const maxDate = useMemo(() => parseIsoDate(maxValue), [maxValue]);
  const today = useMemo(() => parseIsoDate(formatIsoDate(new Date())) ?? new Date(), []);
  const [isOpen, setIsOpen] = useState(false);
  const [visibleMonth, setVisibleMonth] = useState<Date>(
    selectedDate
      ? new Date(Date.UTC(selectedDate.getUTCFullYear(), selectedDate.getUTCMonth(), 1))
      : new Date(Date.UTC(today.getUTCFullYear(), today.getUTCMonth(), 1))
  );

  useEffect(() => {
    if (!selectedDate) {
      return;
    }

    setVisibleMonth(
      new Date(Date.UTC(selectedDate.getUTCFullYear(), selectedDate.getUTCMonth(), 1))
    );
  }, [selectedDate]);

  useEffect(() => {
    if (!isOpen) {
      return;
    }

    function handlePointerDown(event: MouseEvent) {
      if (!rootRef.current?.contains(event.target as Node)) {
        setIsOpen(false);
      }
    }

    function handleKeyDown(event: KeyboardEvent) {
      if (event.key === "Escape") {
        setIsOpen(false);
      }
    }

    document.addEventListener("mousedown", handlePointerDown);
    document.addEventListener("keydown", handleKeyDown);

    return () => {
      document.removeEventListener("mousedown", handlePointerDown);
      document.removeEventListener("keydown", handleKeyDown);
    };
  }, [isOpen]);

  const calendarCells = useMemo(() => buildCalendarCells(visibleMonth), [visibleMonth]);
  const yearOptions = useMemo(
    () => buildYearOptions({ selectedDate, minDate, maxDate, today }),
    [selectedDate, minDate, maxDate, today]
  );

  return (
    <div ref={rootRef} className="relative space-y-2">
      <div className="flex items-center justify-between gap-2">
        <Label htmlFor={`${id}-trigger`}>{label}</Label>
        {value ? (
          <button
            className="inline-flex items-center gap-1 text-xs font-medium text-muted-foreground transition hover:text-foreground"
            type="button"
            onClick={() => {
              onChange("");
            }}
          >
            <X className="h-3.5 w-3.5" />
            Clear
          </button>
        ) : null}
      </div>

      <button
        aria-expanded={isOpen}
        aria-haspopup="dialog"
        aria-label={`Choose ${label.toLowerCase()}`}
        className={cn(
          "group flex h-12 w-full items-center gap-3 rounded-2xl border border-input bg-card/86 px-4 text-left text-sm shadow-sm transition hover:border-primary/40 hover:bg-card focus-visible:outline-none focus-visible:ring-4 focus-visible:ring-primary/10",
          isOpen && "border-primary/50 ring-4 ring-primary/10"
        )}
        id={`${id}-trigger`}
        type="button"
        onClick={() => {
          setIsOpen((currentValue) => !currentValue);
        }}
      >
        <div className="flex h-9 w-9 items-center justify-center rounded-xl bg-primary/10 text-primary transition group-hover:bg-primary/15">
          <CalendarDays className="h-4 w-4" />
        </div>
        <div className="min-w-0 flex-1">
          <p
            className={cn(
              "truncate font-medium",
              selectedDate ? "text-foreground" : "text-muted-foreground"
            )}
          >
            {selectedDate ? formatDisplayDate(selectedDate) : placeholder}
          </p>
          <p className="truncate text-xs text-muted-foreground">
            {description ?? "Pick a specific day from the calendar."}
          </p>
        </div>
        <ChevronDown
          className={cn(
            "h-4 w-4 shrink-0 text-muted-foreground transition",
            isOpen && "rotate-180"
          )}
        />
      </button>

      {isOpen ? (
        <div
          aria-label={`${label} calendar`}
          className="absolute left-0 top-full z-30 mt-2 w-full min-w-[18rem] rounded-[1.5rem] border border-border/70 bg-popover/95 p-4 shadow-[0_28px_60px_rgba(14,37,61,0.18)] backdrop-blur-xl"
          role="dialog"
        >
          <div className="mb-4 space-y-3">
            <div>
              <p className="text-[11px] uppercase tracking-[0.28em] text-muted-foreground">
                Calendar
              </p>
              <p className="text-base font-semibold text-foreground">
                Jump by month or year
              </p>
            </div>

            <div className="grid gap-3 sm:grid-cols-[minmax(0,1fr)_124px_auto] sm:items-end">
              <div className="space-y-1.5">
                <label
                  className="text-[11px] font-semibold uppercase tracking-[0.2em] text-muted-foreground"
                  htmlFor={`${id}-month-select`}
                >
                  Month
                </label>
                <select
                  aria-label={`Select month for ${label.toLowerCase()}`}
                  className="h-10 w-full rounded-2xl border border-input bg-card/80 px-3 text-sm text-foreground shadow-sm outline-none transition focus:border-primary focus:ring-4 focus:ring-primary/10"
                  id={`${id}-month-select`}
                  value={visibleMonth.getUTCMonth()}
                  onChange={(event) => {
                    setVisibleMonth(
                      new Date(
                        Date.UTC(
                          visibleMonth.getUTCFullYear(),
                          Number(event.target.value),
                          1
                        )
                      )
                    );
                  }}
                >
                  {monthOptions.map((monthOption) => (
                    <option key={monthOption.value} value={monthOption.value}>
                      {monthOption.label}
                    </option>
                  ))}
                </select>
              </div>

              <div className="space-y-1.5">
                <label
                  className="text-[11px] font-semibold uppercase tracking-[0.2em] text-muted-foreground"
                  htmlFor={`${id}-year-select`}
                >
                  Year
                </label>
                <select
                  aria-label={`Select year for ${label.toLowerCase()}`}
                  className="h-10 w-full rounded-2xl border border-input bg-card/80 px-3 text-sm text-foreground shadow-sm outline-none transition focus:border-primary focus:ring-4 focus:ring-primary/10"
                  id={`${id}-year-select`}
                  value={visibleMonth.getUTCFullYear()}
                  onChange={(event) => {
                    setVisibleMonth(
                      new Date(
                        Date.UTC(
                          Number(event.target.value),
                          visibleMonth.getUTCMonth(),
                          1
                        )
                      )
                    );
                  }}
                >
                  {yearOptions.map((yearOption) => (
                    <option key={yearOption} value={yearOption}>
                      {yearOption}
                    </option>
                  ))}
                </select>
              </div>

              <div className="flex items-center gap-1 sm:justify-end">
                <Button
                  aria-label={`Show previous month for ${label.toLowerCase()}`}
                  className="h-10 w-10 rounded-full px-0"
                  size="sm"
                  type="button"
                  variant="ghost"
                  onClick={() => {
                    setVisibleMonth((currentValue) => shiftUtcMonth(currentValue, -1));
                  }}
                >
                  <ChevronLeft className="h-4 w-4" />
                </Button>
                <Button
                  aria-label={`Show next month for ${label.toLowerCase()}`}
                  className="h-10 w-10 rounded-full px-0"
                  size="sm"
                  type="button"
                  variant="ghost"
                  onClick={() => {
                    setVisibleMonth((currentValue) => shiftUtcMonth(currentValue, 1));
                  }}
                >
                  <ChevronRight className="h-4 w-4" />
                </Button>
              </div>
            </div>
          </div>

          <div className="grid grid-cols-7 gap-1 text-center">
            {weekdayLabels.map((weekday) => (
              <div
                key={weekday}
                className="pb-2 text-[11px] font-semibold tracking-[0.18em] text-muted-foreground"
              >
                {weekday}
              </div>
            ))}

            {calendarCells.map((cell) => {
              const isSelected = isSameUtcDate(selectedDate, cell.date);
              const isToday = isSameUtcDate(today, cell.date);
              const isDisabled = isDateOutOfRange(cell.date, minDate, maxDate);

              return (
                <button
                  key={cell.date.toISOString()}
                  aria-label={accessibleDateFormatter.format(cell.date)}
                  className={cn(
                    "flex h-10 items-center justify-center rounded-xl text-sm font-medium transition focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary/20",
                    cell.isCurrentMonth ? "text-foreground" : "text-muted-foreground/45",
                    !isSelected && !isDisabled && "hover:bg-secondary/80",
                    isToday && !isSelected && "text-primary",
                    isSelected && "bg-primary text-primary-foreground shadow-sm",
                    isDisabled && "cursor-not-allowed opacity-30"
                  )}
                  disabled={isDisabled}
                  type="button"
                  onClick={() => {
                    onChange(formatIsoDate(cell.date));
                    setVisibleMonth(
                      new Date(Date.UTC(cell.date.getUTCFullYear(), cell.date.getUTCMonth(), 1))
                    );
                    setIsOpen(false);
                  }}
                >
                  {cell.date.getUTCDate()}
                </button>
              );
            })}
          </div>

          <div className="mt-4 flex items-center justify-between border-t border-border/70 pt-3">
            <button
              className="text-xs font-medium uppercase tracking-[0.2em] text-muted-foreground transition hover:text-foreground"
              type="button"
              onClick={() => {
                onChange("");
                setIsOpen(false);
              }}
            >
              Clear
            </button>
            <button
              className="text-xs font-medium uppercase tracking-[0.2em] text-primary transition hover:text-primary/80"
              type="button"
              onClick={() => {
                onChange(formatIsoDate(today));
                setVisibleMonth(new Date(Date.UTC(today.getUTCFullYear(), today.getUTCMonth(), 1)));
                setIsOpen(false);
              }}
            >
              Jump to today
            </button>
          </div>
        </div>
      ) : null}
    </div>
  );
}
