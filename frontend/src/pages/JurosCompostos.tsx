import { useMemo, useState } from "react";
import {
  AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer,
} from "recharts";
import { Banknote, TrendingUp, Coins, Percent } from "lucide-react";
import PageHeader from "../components/PageHeader";
import GlassCard from "../components/GlassCard";
import StatCard from "../components/StatCard";
import { brl } from "../lib/format";

type Periodicidade = "mensal" | "anual";

interface Ponto {
  periodo: number;
  investido: number;
  juros: number;
  total: number;
}

const tooltipStyle = {
  background: "rgba(9,11,18,0.95)",
  border: "1px solid rgba(255,255,255,0.1)",
  borderRadius: 12,
  color: "#e2e8f0",
};

function parseNum(v: string): number {
  const n = parseFloat(v.replace(",", "."));
  return Number.isFinite(n) ? n : 0;
}

function calcular(
  inicial: number,
  aporte: number,
  taxaMensal: number,
  meses: number,
): Ponto[] {
  const pontos: Ponto[] = [{ periodo: 0, investido: inicial, juros: 0, total: inicial }];
  let saldo = inicial;
  let investido = inicial;

  for (let m = 1; m <= meses; m++) {
    saldo = saldo * (1 + taxaMensal) + aporte;
    investido += aporte;
    const juros = saldo - investido;
    pontos.push({
      periodo: m,
      investido: Math.round(investido * 100) / 100,
      juros: Math.round(juros * 100) / 100,
      total: Math.round(saldo * 100) / 100,
    });
  }
  return pontos;
}

export default function JurosCompostos() {
  const [inicial, setInicial] = useState("1000");
  const [aporte, setAporte] = useState("300");
  const [taxa, setTaxa] = useState("1");
  const [taxaPer, setTaxaPer] = useState<Periodicidade>("mensal");
  const [periodo, setPeriodo] = useState("10");
  const [periodoPer, setPeriodoPer] = useState<Periodicidade>("anual");

  const dados = useMemo(() => {
    const vi = parseNum(inicial);
    const ap = parseNum(aporte);
    const tx = parseNum(taxa) / 100;
    const taxaMensal = taxaPer === "anual" ? Math.pow(1 + tx, 1 / 12) - 1 : tx;
    const meses = periodoPer === "anual" ? Math.round(parseNum(periodo) * 12) : Math.round(parseNum(periodo));
    const mesesLimit = Math.min(Math.max(meses, 0), 1200);
    return calcular(vi, ap, taxaMensal, mesesLimit);
  }, [inicial, aporte, taxa, taxaPer, periodo, periodoPer]);

  const final = dados[dados.length - 1];
  const totalInvestido = final?.investido ?? 0;
  const totalJuros = final?.juros ?? 0;
  const totalFinal = final?.total ?? 0;
  const rendimentoPct = totalInvestido > 0 ? (totalJuros / totalInvestido) * 100 : 0;

  return (
    <div>
      <PageHeader
        eyebrow="Simulador de Investimentos"
        title="Juros Compostos"
        description="Projete o crescimento do seu patrimônio com aportes mensais e veja o poder dos juros sobre juros ao longo do tempo."
      />

      <div className="grid gap-6 lg:grid-cols-[360px_1fr]">
        <GlassCard title="Parâmetros" subtitle="Configure sua simulação">
          <div className="space-y-4">
            <CampoMoeda label="Valor inicial" value={inicial} onChange={setInicial} />
            <CampoMoeda label="Aporte mensal" value={aporte} onChange={setAporte} />

            <CampoComToggle
              label="Taxa de juros"
              value={taxa}
              onChange={setTaxa}
              suffix="%"
              per={taxaPer}
              onPer={setTaxaPer}
            />

            <CampoComToggle
              label="Período"
              value={periodo}
              onChange={setPeriodo}
              per={periodoPer}
              onPer={setPeriodoPer}
              perLabels={{ mensal: "meses", anual: "anos" }}
            />
          </div>
        </GlassCard>

        <div className="space-y-6">
          <div className="grid grid-cols-1 gap-4 sm:grid-cols-3">
            <StatCard label="Valor total final" value={brl(totalFinal)} icon={TrendingUp} tone="positive" delay={0} />
            <StatCard label="Total investido" value={brl(totalInvestido)} icon={Banknote} delay={60} />
            <StatCard
              label="Total em juros"
              value={brl(totalJuros)}
              hint={`+${rendimentoPct.toLocaleString("pt-BR", { maximumFractionDigits: 1 })}% sobre o investido`}
              icon={Coins}
              tone="positive"
              delay={120}
            />
          </div>

          <GlassCard title="Evolução do patrimônio" subtitle="Valor investido vs. juros acumulados" delay={160}>
            <GraficoEvolucao data={dados} />
          </GlassCard>
        </div>
      </div>

      <GlassCard className="mt-6 !p-0 overflow-hidden" delay={200}>
        <div className="flex items-center justify-between px-6 py-4">
          <div>
            <h2 className="font-display text-lg font-semibold text-white">Detalhamento</h2>
            <p className="mt-0.5 text-xs text-slate-400">Saldo mês a mês da simulação</p>
          </div>
          <Percent size={18} className="text-brand" />
        </div>
        <div className="max-h-[420px] overflow-y-auto">
          <table className="w-full text-sm">
            <thead className="sticky top-0 border-y border-white/10 bg-ink-900/90 text-left text-xs uppercase tracking-wider text-slate-500 backdrop-blur">
              <tr>
                <th className="px-6 py-3 font-medium">Mês</th>
                <th className="px-6 py-3 text-right font-medium">Investido</th>
                <th className="px-6 py-3 text-right font-medium">Juros</th>
                <th className="px-6 py-3 text-right font-medium">Total</th>
              </tr>
            </thead>
            <tbody>
              {dados.slice(1).map((p) => (
                <tr key={p.periodo} className="border-b border-white/5 transition-colors hover:bg-white/[0.03]">
                  <td className="px-6 py-3 font-mono text-slate-400">
                    {p.periodo}
                    <span className="ml-2 text-[11px] text-slate-600">
                      {p.periodo % 12 === 0 ? `(${p.periodo / 12} ${p.periodo / 12 === 1 ? "ano" : "anos"})` : ""}
                    </span>
                  </td>
                  <td className="px-6 py-3 text-right font-mono text-slate-300">{brl(p.investido)}</td>
                  <td className="px-6 py-3 text-right font-mono text-emerald-400">{brl(p.juros)}</td>
                  <td className="px-6 py-3 text-right font-mono font-semibold text-white">{brl(p.total)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </GlassCard>
    </div>
  );
}

function GraficoEvolucao({ data }: { data: Ponto[] }) {
  if (data.length <= 1) {
    return <p className="py-12 text-center text-sm text-slate-500">Informe os parâmetros para simular.</p>;
  }
  return (
    <ResponsiveContainer width="100%" height={320}>
      <AreaChart data={data} margin={{ left: 4, right: 8, top: 8 }}>
        <defs>
          <linearGradient id="gInvestidoJ" x1="0" y1="0" x2="0" y2="1">
            <stop offset="0%" stopColor="#8b5cf6" stopOpacity={0.5} />
            <stop offset="100%" stopColor="#8b5cf6" stopOpacity={0} />
          </linearGradient>
          <linearGradient id="gJurosJ" x1="0" y1="0" x2="0" y2="1">
            <stop offset="0%" stopColor="#2dd4bf" stopOpacity={0.6} />
            <stop offset="100%" stopColor="#2dd4bf" stopOpacity={0} />
          </linearGradient>
        </defs>
        <CartesianGrid strokeDasharray="3 3" stroke="rgba(148,163,184,0.08)" />
        <XAxis
          dataKey="periodo"
          stroke="#64748b"
          fontSize={12}
          tickLine={false}
          axisLine={false}
          tickFormatter={(m: number) => (m % 12 === 0 ? `${m / 12}a` : `${m}m`)}
        />
        <YAxis
          stroke="#64748b"
          fontSize={12}
          tickLine={false}
          axisLine={false}
          tickFormatter={(v: number) => `R$${(v / 1000).toFixed(0)}k`}
        />
        <Tooltip
          contentStyle={tooltipStyle}
          formatter={(v: number) => brl(v)}
          labelFormatter={(m: number) => `Mês ${m}`}
        />
        <Legend formatter={(value) => <span className="text-slate-300">{value}</span>} />
        <Area
          type="monotone"
          dataKey="investido"
          name="Investido"
          stackId="1"
          stroke="#8b5cf6"
          strokeWidth={2}
          fill="url(#gInvestidoJ)"
        />
        <Area
          type="monotone"
          dataKey="juros"
          name="Juros"
          stackId="1"
          stroke="#2dd4bf"
          strokeWidth={2}
          fill="url(#gJurosJ)"
        />
      </AreaChart>
    </ResponsiveContainer>
  );
}

function CampoMoeda({ label, value, onChange }: { label: string; value: string; onChange: (v: string) => void }) {
  return (
    <label className="block">
      <span className="text-xs text-slate-500">{label}</span>
      <div className="mt-1 flex items-center rounded-lg border border-white/10 bg-ink-800 focus-within:border-brand/50">
        <span className="pl-3 text-sm text-slate-500">R$</span>
        <input
          type="number"
          inputMode="decimal"
          value={value}
          onChange={(e) => onChange(e.target.value)}
          className="w-full bg-transparent px-2 py-2 text-sm text-white outline-none"
        />
      </div>
    </label>
  );
}

function CampoComToggle({
  label, value, onChange, suffix, per, onPer, perLabels = { mensal: "ao mês", anual: "ao ano" },
}: {
  label: string;
  value: string;
  onChange: (v: string) => void;
  suffix?: string;
  per: Periodicidade;
  onPer: (p: Periodicidade) => void;
  perLabels?: Record<Periodicidade, string>;
}) {
  return (
    <label className="block">
      <span className="text-xs text-slate-500">{label}</span>
      <div className="mt-1 flex items-center gap-2">
        <div className="flex flex-1 items-center rounded-lg border border-white/10 bg-ink-800 focus-within:border-brand/50">
          <input
            type="number"
            inputMode="decimal"
            value={value}
            onChange={(e) => onChange(e.target.value)}
            className="w-full bg-transparent px-3 py-2 text-sm text-white outline-none"
          />
          {suffix && <span className="pr-3 text-sm text-slate-500">{suffix}</span>}
        </div>
        <div className="flex shrink-0 rounded-lg border border-white/10 bg-ink-800 p-0.5">
          {(["mensal", "anual"] as Periodicidade[]).map((p) => (
            <button
              key={p}
              type="button"
              onClick={() => onPer(p)}
              className={`rounded-md px-2.5 py-1.5 text-xs font-medium transition-colors ${
                per === p ? "bg-brand/20 text-brand" : "text-slate-500 hover:text-slate-300"
              }`}
            >
              {perLabels[p]}
            </button>
          ))}
        </div>
      </div>
    </label>
  );
}
