import { NavLink, Outlet } from "react-router-dom";
import {
  LayoutDashboard,
  Wallet,
  Calculator,
  Coins,
  Receipt,
  TrendingUp,
  Activity,
  LineChart,
  PiggyBank,
  GraduationCap,
  BookOpen,
} from "lucide-react";

const nav = [
  { to: "/", label: "Dashboard", icon: LayoutDashboard, end: true },
  { to: "/jornada", label: "Liberdade Financeira", icon: GraduationCap },
  { to: "/organizador", label: "Organizador", icon: PiggyBank },
  { to: "/carteira", label: "Carteira", icon: Wallet },
  { to: "/valuation", label: "Valuation", icon: Calculator },
  { to: "/dividendos", label: "Dividendos", icon: Coins },
  { to: "/fiscal", label: "Fiscal", icon: Receipt },
  { to: "/juros-compostos", label: "Juros Compostos", icon: LineChart },
  { to: "/tutorial", label: "Tutorial", icon: BookOpen },
];

export default function Layout() {
  return (
    <div className="flex min-h-screen">
      <aside className="sticky top-0 flex h-screen w-64 shrink-0 flex-col border-r border-white/10 bg-ink-900/60 backdrop-blur-xl">
        <div className="flex items-center gap-3 px-6 py-7">
          <div className="relative flex h-10 w-10 items-center justify-center rounded-xl bg-gradient-to-br from-brand to-accent-cyan shadow-glow">
            <TrendingUp size={20} className="text-ink-950" />
          </div>
          <div>
            <p className="font-display text-lg font-bold leading-none text-white">Imsfay</p>
            <p className="text-xs font-medium tracking-widest text-brand">INVEST</p>
          </div>
        </div>

        <nav className="mt-4 flex-1 space-y-1 px-3">
          {nav.map(({ to, label, icon: Icon, end }) => (
            <NavLink
              key={to}
              to={to}
              end={end}
              className={({ isActive }) =>
                `group relative flex items-center gap-3 rounded-xl px-4 py-3 text-sm font-medium transition-all duration-300 ${
                  isActive
                    ? "bg-gradient-to-r from-brand/20 to-transparent text-white shadow-glow"
                    : "text-slate-400 hover:bg-white/5 hover:text-slate-100"
                }`
              }
            >
              {({ isActive }) => (
                <>
                  {isActive && (
                    <span className="absolute left-0 top-1/2 h-6 -translate-y-1/2 rounded-r-full bg-brand shadow-glow" style={{ width: 3 }} />
                  )}
                  <Icon size={18} className={isActive ? "text-brand" : ""} />
                  {label}
                </>
              )}
            </NavLink>
          ))}
        </nav>

        <div className="m-3 rounded-xl border border-white/10 bg-white/[0.02] p-4">
          <div className="flex items-center gap-2 text-xs text-slate-400">
            <Activity size={14} className="text-brand animate-pulse-glow" />
            Mercado conectado
          </div>
          <p className="mt-1 text-[11px] text-slate-500">Dados via Brapi · Yahoo · BCB</p>
        </div>
      </aside>

      <main className="grid-bg relative flex-1 overflow-x-hidden">
        <div className="mx-auto max-w-7xl px-8 py-8">
          <Outlet />
        </div>
      </main>
    </div>
  );
}
