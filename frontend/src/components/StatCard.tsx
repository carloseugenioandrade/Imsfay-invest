import type { LucideIcon } from "lucide-react";

interface StatCardProps {
  label: string;
  value: string;
  hint?: string;
  tone?: "neutral" | "positive" | "negative";
  icon?: LucideIcon;
  delay?: number;
}

const toneClasses: Record<NonNullable<StatCardProps["tone"]>, string> = {
  neutral: "text-white",
  positive: "text-emerald-400",
  negative: "text-rose-400",
};

export default function StatCard({ label, value, hint, tone = "neutral", icon: Icon, delay = 0 }: StatCardProps) {
  return (
    <div
      className="glass glass-hover group relative overflow-hidden p-5 animate-fade-up"
      style={{ animationDelay: `${delay}ms` }}
    >
      <div className="pointer-events-none absolute -right-8 -top-8 h-24 w-24 rounded-full bg-brand/10 blur-2xl transition-opacity duration-300 group-hover:opacity-100" />
      <div className="flex items-start justify-between">
        <p className="text-sm text-slate-400">{label}</p>
        {Icon && (
          <span className="flex h-9 w-9 items-center justify-center rounded-lg border border-white/10 bg-white/5 text-brand">
            <Icon size={16} />
          </span>
        )}
      </div>
      <p className={`mt-3 font-display text-2xl font-bold ${toneClasses[tone]}`}>{value}</p>
      {hint && <p className="mt-1 text-xs text-slate-500">{hint}</p>}
    </div>
  );
}
