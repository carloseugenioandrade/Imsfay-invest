import { NavLink, Outlet } from "react-router-dom";
import { LayoutDashboard, Wallet, Calculator, Coins, Receipt } from "lucide-react";

const nav = [
  { to: "/", label: "Dashboard", icon: LayoutDashboard, end: true },
  { to: "/carteira", label: "Carteira", icon: Wallet },
  { to: "/valuation", label: "Valuation", icon: Calculator },
  { to: "/dividendos", label: "Dividendos", icon: Coins },
  { to: "/fiscal", label: "Fiscal", icon: Receipt },
];

export default function Layout() {
  return (
    <div className="flex min-h-screen">
      <aside className="w-60 shrink-0 bg-slate-900 text-slate-100 p-4">
        <div className="text-xl font-bold text-brand mb-8 px-2">Imsfay Invest</div>
        <nav className="space-y-1">
          {nav.map(({ to, label, icon: Icon, end }) => (
            <NavLink
              key={to}
              to={to}
              end={end}
              className={({ isActive }) =>
                `flex items-center gap-3 rounded-lg px-3 py-2 text-sm transition-colors ${
                  isActive ? "bg-brand text-white" : "text-slate-300 hover:bg-slate-800"
                }`
              }
            >
              <Icon size={18} />
              {label}
            </NavLink>
          ))}
        </nav>
      </aside>
      <main className="flex-1 p-8">
        <Outlet />
      </main>
    </div>
  );
}
