import { Card, CardContent } from "@/components/ui/card";

type MetricCardProps = {
  label: string;
  value: string;
  hint: string;
};

export function MetricCard({ label, value, hint }: MetricCardProps) {
  return (
    <Card className="overflow-hidden border-primary/10 bg-gradient-to-br from-card via-card to-secondary/45">
      <CardContent className="space-y-3 p-4">
        <div className="flex items-start justify-between gap-3">
          <p className="text-[11px] font-semibold uppercase tracking-[0.24em] text-muted-foreground">
            {label}
          </p>
          <div className="h-2.5 w-2.5 rounded-full bg-accent/70" />
        </div>
        <div className="space-y-1.5">
          <p className="text-[1.7rem] font-semibold tracking-tight text-foreground">{value}</p>
          <p className="text-xs leading-5 text-muted-foreground">{hint}</p>
        </div>
      </CardContent>
    </Card>
  );
}
