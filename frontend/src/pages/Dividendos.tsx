import { useEffect, useState } from "react";
import {
  BarChart, Bar, ResponsiveContainer, XAxis, YAxis, CartesianGrid, Tooltip,
} from "recharts";
import { Coins, Percent, Sparkles } from "lucide-react";
import PageHeader from "../components/PageHeader";
import GlassCard from "../components/GlassCard";
import StatCard from "../components/StatCard";
import { api } from "../lib/api";
import { brl, pct } from "../lib/format";
import type { ProventoResumo, AgendaPreditiva } from "../lib/types";

const tooltipStyle = {
  background: "rgba(9,11,18,0.95)",
  border: "1px solid rgba(255,255,255,0.1)",
  borderRadius: 12,
  color: "#e2e8f0",
};

function corProb(p: number): string {
  if (p >= 0.75) return "rgba(45,212,191,0.9)";
  if (p >= 0.5) return "rgba(45,212,191,0.6)";
  if (p >= 0.25) return "rgba(139,92,246,0.5)";
  if (p > 0) return "rgba(139,92,246,0.3)";
  return "rgba(148,163,184,0.08)";
}

export default function Dividendos() {
  const [resumo, setResumo] = useState<ProventoResumo | null>(null);
  const [agenda, setAgenda] = useState<AgendaPreditiva | null>(null);

  useEffect(() => {
    api.get<ProventoResumo>("/proventos/resumo").then((r) => setResumo(r.data)).catch(() => undefined);
    api.get<AgendaPreditiva>("/proventos/agenda-preditiva").then((r) => setAgenda(r.data)).catch(() => undefined);
  }, []);

  return (
    <div>
      <PageHeader
        eyebrow="Renda Passiva"
        title="Dividendos Inteligentes"
        description="Evolução de proventos, Yield on Cost e agenda preditiva por sazonalidade histórica."
      />

      {resumo && (
        <div className="mb-6 grid grid-cols-1 gap-4 sm:grid-cols-3">
          <StatCard label="Total recebido" value={brl(resumo.total_recebido)} icon={Coins} />
          <StatCard label="Yield on Cost" value={pct(resumo.yield_on_cost_pct)} icon={Percent} tone="positive" hint="Sobre o custo investido" />
          <StatCard label="Base de custo" value={brl(resumo.custo_base)} icon={Sparkles} />
        </div>
      )}

      <GlassCard title="Evolução de proventos" subtitle="Total recebido por mês">
        {resumo && resumo.evolucao_mensal.length > 0 ? (
          <ResponsiveContainer width="100%" height={280}>
            <BarChart data={resumo.evolucao_mensal} margin={{ left: 4, right: 8, top: 8 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="rgba(148,163,184,0.08)" />
              <XAxis dataKey="mes" stroke="#64748b" fontSize={12} tickLine={false} axisLine={false} />
              <YAxis stroke="#64748b" fontSize={12} tickLine={false} axisLine={false} tickFormatter={(v: number) => `R$${v}`} />
              <Tooltip contentStyle={tooltipStyle} formatter={(v: number) => brl(v)} cursor={{ fill: "rgba(255,255,255,0.03)" }} />
              <Bar dataKey="valor" name="Proventos" radius={[6, 6, 0, 0]} fill="#2dd4bf" />
            </BarChart>
          </ResponsiveContainer>
        ) : (
          <p className="py-12 text-center text-sm text-slate-500">Nenhum provento registrado.</p>
        )}
      </GlassCard>

      <GlassCard className="mt-6" title="Agenda preditiva" subtitle="Probabilidade de provento por mês (sazonalidade histórica)">
        {agenda ? (
          <div className="space-y-4">
            <Heatmap titulo="Carteira (média)" meses={agenda.carteira} />
            {agenda.por_ativo.map((a) => (
              <Heatmap key={a.ticker} titulo={a.ticker} meses={a.meses} />
            ))}
            {agenda.por_ativo.length === 0 && (
              <p className="py-6 text-center text-sm text-slate-500">Sem histórico de proventos para prever.</p>
            )}
          </div>
        ) : (
          <p className="py-12 text-center text-sm text-slate-500">Carregando...</p>
        )}
      </GlassCard>
    </div>
  );
}

function Heatmap({ titulo, meses }: { titulo: string; meses: { mes: string; probabilidade: number }[] }) {
  return (
    <div>
      <p className="mb-1.5 text-xs font-semibold text-slate-400">{titulo}</p>
      <div className="grid grid-cols-12 gap-1.5">
        {meses.map((m) => (
          <div
            key={m.mes}
            title={`${m.mes}: ${(m.probabilidade * 100).toFixed(0)}%`}
            className="flex h-10 flex-col items-center justify-center rounded-md text-[10px] text-slate-300"
            style={{ background: corProb(m.probabilidade) }}
          >
            <span>{m.mes}</span>
          </div>
        ))}
      </div>
    </div>
  );
}
