import { useCallback, useEffect, useState } from "react";
import {
  PieChart, Pie, Cell, ResponsiveContainer, Tooltip, Legend,
  AreaChart, Area, XAxis, YAxis, CartesianGrid,
} from "recharts";
import { Wallet, Banknote, TrendingUp, PieChart as PieIcon, RefreshCw } from "lucide-react";
import PageHeader from "../components/PageHeader";
import StatCard from "../components/StatCard";
import GlassCard from "../components/GlassCard";
import { api } from "../lib/api";
import { brl, pct } from "../lib/format";
import type { ResumoCarteira, EvolucaoPonto } from "../lib/types";

const CORES = ["#2dd4bf", "#22d3ee", "#8b5cf6", "#f59e0b", "#f43f5e", "#34d399"];

const fmtMes = (iso: string) =>
  new Date(iso).toLocaleDateString("pt-BR", { month: "short", year: "2-digit" });

export default function Dashboard() {
  const [resumo, setResumo] = useState<ResumoCarteira | null>(null);
  const [evolucao, setEvolucao] = useState<EvolucaoPonto[]>([]);
  const [erro, setErro] = useState<string | null>(null);
  const [sincronizando, setSincronizando] = useState(false);

  const carregar = useCallback(() => {
    api
      .get<ResumoCarteira>("/carteira/resumo")
      .then((r) => setResumo(r.data))
      .catch(() => setErro("Não foi possível carregar a carteira."));
    api
      .get<{ items: EvolucaoPonto[] }>("/carteira/evolucao?benchmark_cdi=true")
      .then((r) => setEvolucao(r.data.items))
      .catch(() => undefined);
  }, []);

  useEffect(() => {
    carregar();
  }, [carregar]);

  const sincronizar = async () => {
    setSincronizando(true);
    try {
      await api.post("/market/sync/cotacoes");
      carregar();
    } catch {
      setErro("Falha ao sincronizar cotações (verifique a conexão / token Brapi).");
    } finally {
      setSincronizando(false);
    }
  };

  return (
    <div>
      <div className="flex items-start justify-between gap-4">
        <PageHeader
          eyebrow="Cockpit do Investidor"
          title="Dashboard"
          description="Visão consolidada do seu patrimônio, rentabilidade e alocação em tempo real."
        />
        <button
          onClick={sincronizar}
          disabled={sincronizando}
          className="flex shrink-0 items-center gap-2 rounded-xl border border-white/10 bg-white/5 px-4 py-2.5 text-sm font-medium text-slate-200 transition-all hover:border-brand/40 hover:bg-brand/10 hover:text-white disabled:opacity-50"
        >
          <RefreshCw size={16} className={sincronizando ? "animate-spin text-brand" : "text-brand"} />
          {sincronizando ? "Sincronizando..." : "Sincronizar mercado"}
        </button>
      </div>

      {erro && (
        <div className="glass mb-4 border-rose-500/30 p-4 text-rose-300">{erro}</div>
      )}

      {resumo && (
        <>
          <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
            <StatCard label="Patrimônio atual" value={brl(resumo.valor_atual)} icon={Wallet} delay={0} />
            <StatCard label="Total investido" value={brl(resumo.valor_investido)} icon={Banknote} delay={60} />
            <StatCard
              label="Lucro / Prejuízo"
              value={brl(resumo.lucro)}
              tone={resumo.lucro >= 0 ? "positive" : "negative"}
              icon={TrendingUp}
              delay={120}
            />
            <StatCard
              label="Rentabilidade"
              value={pct(resumo.rentabilidade_pct)}
              hint={`${resumo.quantidade_ativos} ativos na carteira`}
              tone={resumo.rentabilidade_pct >= 0 ? "positive" : "negative"}
              icon={PieIcon}
              delay={180}
            />
          </div>

          <GlassCard
            className="mt-6"
            title="Evolução do patrimônio"
            subtitle="Patrimônio (marcado a mercado) vs total investido"
            delay={210}
          >
            <EvolucaoChart data={evolucao} />
          </GlassCard>

          <div className="mt-6 grid grid-cols-1 gap-4 lg:grid-cols-2">
            <GlassCard title="Alocação por classe" subtitle="Distribuição do patrimônio por tipo de ativo" delay={260}>
              <DonutChart data={resumo.alocacao_por_classe} />
            </GlassCard>
            <GlassCard title="Alocação por setor" subtitle="Exposição setorial da carteira" delay={320}>
              <DonutChart data={resumo.alocacao_por_setor} />
            </GlassCard>
          </div>
        </>
      )}
    </div>
  );
}

const tooltipStyle = {
  background: "rgba(9,11,18,0.95)",
  border: "1px solid rgba(255,255,255,0.1)",
  borderRadius: 12,
  color: "#e2e8f0",
};

function EvolucaoChart({ data }: { data: EvolucaoPonto[] }) {
  if (data.length === 0) {
    return <p className="py-12 text-center text-sm text-slate-500">Sem histórico de cotações ainda.</p>;
  }
  return (
    <ResponsiveContainer width="100%" height={300}>
      <AreaChart data={data} margin={{ left: 4, right: 8, top: 8 }}>
        <defs>
          <linearGradient id="gPatrimonio" x1="0" y1="0" x2="0" y2="1">
            <stop offset="0%" stopColor="#2dd4bf" stopOpacity={0.5} />
            <stop offset="100%" stopColor="#2dd4bf" stopOpacity={0} />
          </linearGradient>
          <linearGradient id="gInvestido" x1="0" y1="0" x2="0" y2="1">
            <stop offset="0%" stopColor="#8b5cf6" stopOpacity={0.3} />
            <stop offset="100%" stopColor="#8b5cf6" stopOpacity={0} />
          </linearGradient>
        </defs>
        <CartesianGrid strokeDasharray="3 3" stroke="rgba(148,163,184,0.08)" />
        <XAxis dataKey="data" tickFormatter={fmtMes} stroke="#64748b" fontSize={12} tickLine={false} axisLine={false} />
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
          labelFormatter={(l: string) => fmtMes(l)}
        />
        <Legend formatter={(value) => <span className="text-slate-300">{value}</span>} />
        <Area
          type="monotone"
          dataKey="patrimonio"
          name="Patrimônio"
          stroke="#2dd4bf"
          strokeWidth={2}
          fill="url(#gPatrimonio)"
        />
        <Area
          type="monotone"
          dataKey="investido"
          name="Investido"
          stroke="#8b5cf6"
          strokeWidth={2}
          strokeDasharray="5 4"
          fill="url(#gInvestido)"
        />
        {data.some((d) => d.cdi != null) && (
          <Area
            type="monotone"
            dataKey="cdi"
            name="CDI"
            stroke="#f59e0b"
            strokeWidth={2}
            strokeDasharray="2 3"
            fill="none"
          />
        )}
      </AreaChart>
    </ResponsiveContainer>
  );
}

function DonutChart({ data }: { data: { nome: string; valor: number }[] }) {
  return (
    <ResponsiveContainer width="100%" height={280}>
      <PieChart>
        <Pie
          data={data}
          dataKey="valor"
          nameKey="nome"
          innerRadius={70}
          outerRadius={110}
          paddingAngle={3}
          stroke="none"
        >
          {data.map((_, i) => (
            <Cell key={i} fill={CORES[i % CORES.length]} />
          ))}
        </Pie>
        <Tooltip
          formatter={(v: number) => brl(v)}
          contentStyle={{
            background: "rgba(9,11,18,0.95)",
            border: "1px solid rgba(255,255,255,0.1)",
            borderRadius: 12,
            color: "#e2e8f0",
          }}
        />
        <Legend
          iconType="circle"
          formatter={(value) => <span className="text-slate-300">{value}</span>}
        />
      </PieChart>
    </ResponsiveContainer>
  );
}
