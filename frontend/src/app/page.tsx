import { Activity, BrainCircuit, Newspaper, ShieldCheck } from "lucide-react";

import { PredictionDashboard } from "@/components/prediction-dashboard";
import { ThemeToggle } from "@/components/theme-toggle";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent } from "@/components/ui/card";

const highlights = [
  {
    icon: BrainCircuit,
    title: "Validation-driven predictions",
    description:
      "One typed backend response carries feature columns, metrics, price history, and validation outputs."
  },
  {
    icon: Newspaper,
    title: "Anomaly-day context",
    description:
      "When the model misses badly, the UI can attach same-day market news so the miss becomes explainable."
  },
  {
    icon: Activity,
    title: "Local product feel",
    description:
      "Theme-aware charts, polished form states, and compact cards make the local workflow feel like a real app."
  }
];

const stats = [
  {
    label: "Typed payload",
    value: "1 request",
    detail: "Predictions, metrics, anomaly news, and metadata arrive in one contract."
  },
  {
    label: "Review surfaces",
    value: "2 charts",
    detail: "History and validation output stay visible while you inspect the rest of the result."
  },
  {
    label: "Context layer",
    value: "Same-day news",
    detail: "Large misses can be paired with what happened in the market on that date."
  }
];

export default function HomePage() {
  return (
    <main className="relative min-h-screen overflow-hidden">
      <div className="pointer-events-none absolute inset-0 -z-10 bg-[radial-gradient(circle_at_top_left,rgba(18,88,97,0.14),transparent_30%),radial-gradient(circle_at_82%_0%,rgba(226,131,77,0.12),transparent_24%)]" />
      <div className="mx-auto flex w-full max-w-7xl flex-col gap-6 px-4 py-4 sm:px-6 lg:px-8 lg:py-8">
        <section className="glass-panel relative overflow-hidden rounded-[2.35rem]">
          <div className="absolute inset-x-0 top-0 h-24 bg-gradient-to-r from-primary/18 via-accent/12 to-transparent" />
          <div className="relative grid gap-6 px-5 py-5 lg:grid-cols-[minmax(0,1.12fr)_minmax(340px,0.88fr)] lg:px-8 lg:py-8">
            <div className="space-y-5">
              <div className="flex flex-wrap items-center justify-between gap-3">
                <div className="flex flex-wrap gap-2">
                  <Badge variant="outline">FastAPI API</Badge>
                  <Badge variant="outline">Next.js 15</Badge>
                  <Badge variant="outline">Typed anomaly context</Badge>
                </div>
                <ThemeToggle />
              </div>

              <div className="space-y-3">
                <h1 className="max-w-3xl text-4xl font-semibold text-balance text-foreground sm:text-[3.35rem]">
                  A sharper stock lab for predictions, anomaly review, and same-day market context.
                </h1>
                <p className="max-w-2xl text-[15px] leading-7 text-muted-foreground sm:text-base">
                  Enter a ticker, choose a time window with a year-aware calendar, and review the
                  validation output in a theme-aware workspace that feels like a real product.
                </p>
              </div>

              <div className="grid gap-3 sm:grid-cols-3">
                {stats.map((stat) => (
                  <div
                    key={stat.label}
                    className="rounded-[1.4rem] border border-border/70 bg-card/72 p-4 shadow-sm"
                  >
                    <p className="text-[11px] font-semibold uppercase tracking-[0.24em] text-muted-foreground">
                      {stat.label}
                    </p>
                    <p className="mt-3 text-2xl font-semibold tracking-tight text-foreground">
                      {stat.value}
                    </p>
                    <p className="mt-2 text-sm leading-6 text-muted-foreground">{stat.detail}</p>
                  </div>
                ))}
              </div>
            </div>

            <Card className="hero-panel overflow-hidden border-primary/15 shadow-soft">
              <CardContent className="space-y-5 p-5">
                <div className="flex items-center justify-between gap-3">
                  <div className="space-y-1">
                    <p className="text-xs uppercase tracking-[0.3em] hero-panel-muted">
                      Platform snapshot
                    </p>
                    <h2 className="text-2xl font-semibold">What this page gives you</h2>
                  </div>
                  <div className="flex h-10 w-10 items-center justify-center rounded-2xl bg-white/10 text-white">
                    <ShieldCheck className="h-5 w-5" />
                  </div>
                </div>

                <div className="grid gap-3">
                  {highlights.map(({ icon: Icon, title, description }) => (
                    <div
                      key={title}
                      className="grid gap-3 rounded-[1.35rem] border border-white/10 bg-white/6 p-4 sm:grid-cols-[auto_1fr]"
                    >
                      <div className="flex h-10 w-10 items-center justify-center rounded-2xl bg-white/10 text-white">
                        <Icon className="h-5 w-5" />
                      </div>
                      <div>
                        <h3 className="text-base font-medium">{title}</h3>
                        <p className="mt-1 text-sm leading-6 hero-panel-muted">{description}</p>
                      </div>
                    </div>
                  ))}
                </div>

                <div className="rounded-[1.35rem] border border-white/10 bg-white/6 p-4">
                  <p className="text-[11px] uppercase tracking-[0.24em] hero-panel-muted">
                    Expected flow
                  </p>
                  <p className="mt-2 text-sm leading-6 hero-panel-muted">
                    Search a ticker, jump to the right year in the calendar, then inspect metrics,
                    charts, and anomaly-day context in one place.
                  </p>
                </div>
              </CardContent>
            </Card>
          </div>
        </section>

        <PredictionDashboard />
      </div>
    </main>
  );
}
