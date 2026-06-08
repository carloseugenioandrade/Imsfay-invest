import { useEffect, useMemo, useState, type FormEvent } from "react";
import {
  Bar,
  BarChart,
  Cell,
  Legend,
  Pie,
  PieChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import { Plus, Trash2, TrendingUp, TrendingDown, Wallet, PiggyBank } from "lucide-react";
import PageHeader from "../components/PageHeader";
import GlassCard from "../components/GlassCard";
import { api } from "../lib/api";
import { brl } from "../lib/format";
import type { Lancamento, ResumoFinanceiro } from "../lib/types";

const CATEGORIAS_DESPESA = [
  "Moradia",
  "Alimentação",
  "Transporte",
  "Saúde",
  "Educação",
  "Lazer",
  "Assinaturas",
  "Dívidas",
  "Outros",
];
const CATEGORIAS_RECEITA = ["Salário", "Freelance", "Investimentos", "Outros"];

const PIE_COLORS = ["#22d3a5", "#38bdf8", "#a78bfa", "#fbbf24", "#fb7185", "#34d399", "#f472b6", "#60a5fa", "#94a3b8"];

const hoje = () => new Date().toISOString().slice(0, 10);

function StatCard({
  label,
  value,
  icon: Icon,
  tone,
}: {
  label: string;
  value: string;
  icon: typeof Wallet;
  tone: string;
}) {
  return (
    <GlassCard className="!p-5">
      <div className="flex items-center justify-between">
        <span className="text-xs uppercase tracking-wider text-slate-500">{label}</span>
        <Icon size={18} className={tone} />
      </div>
      <p className="mt-2 font-display text-2xl font-bold text-white">{value}</p>
    </GlassCard>
  );
}

export default function Organizador() {
  const [resumo, setResumo] = useState<ResumoFinanceiro | null>(null);
  const [lancamentos, setLancamentos] = useState<Lancamento[]>([]);
  const [erro, setErro] = useState<string | null>(null);

  const [tipo, setTipo] = useState<"receita" | "despesa">("despesa");
  const [categoria, setCategoria] = useState("Moradia");
  const [valor, setValor] = useState("");
  const [descricao, setDescricao] = useState("");
  const [data, setData] = useState(hoje());
  const [recorrente, setRecorrente] = useState(false);
  const [salvando, setSalvando] = useState(false);

  const carregar = () => {
    api.get<ResumoFinanceiro>("/financas/resumo").then((r) => setResumo(r.data)).catch(() => setErro("Erro ao carregar resumo."));
    api.get<Lancamento[]>("/financas/lancamentos").then((r) => setLancamentos(r.data)).catch(() => undefined);
  };

  useEffect(carregar, []);

  const categorias = tipo === "despesa" ? CATEGORIAS_DESPESA : CATEGORIAS_RECEITA;
  useEffect(() => {
    setCategoria(categorias[0]);
  }, [tipo]); // eslint-disable-line react-hooks/exhaustive-deps

  const adicionar = async (e: FormEvent) => {
    e.preventDefault();
    const v = parseFloat(valor.replace(",", "."));
    if (!v || v <= 0) {
      setErro("Informe um valor válido.");
      return;
    }
    setSalvando(true);
    setErro(null);
    try {
      await api.post("/financas/lancamentos", {
        tipo,
        categoria,
        descricao: descricao || null,
        valor: v,
        data,
        recorrente,
      });
      setValor("");
      setDescricao("");
      carregar();
    } catch {
      setErro("Não foi possível salvar o lançamento.");
    } finally {
      setSalvando(false);
    }
  };

  const remover = async (id: number) => {
    await api.delete(`/financas/lancamentos/${id}`);
    carregar();
  };

  const pieData = useMemo(
    () => (resumo?.por_categoria ?? []).map((c) => ({ name: c.categoria, value: c.valor })),
    [resumo],
  );

  return (
    <div>
      <PageHeader
        eyebrow="Organizador Financeiro"
        title="Suas finanças, no controle"
        description="Registre receitas e despesas para enxergar para onde vai o seu dinheiro e quanto sobra para investir."
      />

      {erro && <div className="glass mb-4 border-rose-500/30 p-4 text-rose-300">{erro}</div>}

      <div className="mb-6 grid grid-cols-2 gap-4 lg:grid-cols-4">
        <StatCard label="Receitas (mês)" value={brl(resumo?.receitas ?? 0)} icon={TrendingUp} tone="text-emerald-400" />
        <StatCard label="Despesas (mês)" value={brl(resumo?.despesas ?? 0)} icon={TrendingDown} tone="text-rose-400" />
        <StatCard label="Saldo" value={brl(resumo?.saldo ?? 0)} icon={Wallet} tone="text-brand" />
        <StatCard
          label="Taxa de poupança"
          value={`${(resumo?.taxa_poupanca ?? 0).toLocaleString("pt-BR", { maximumFractionDigits: 1 })}%`}
          icon={PiggyBank}
          tone="text-accent-cyan"
        />
      </div>

      <div className="grid gap-6 lg:grid-cols-3">
        {/* Formulário */}
        <GlassCard title="Novo lançamento" className="lg:col-span-1">
          <form onSubmit={adicionar} className="space-y-4">
            <div className="grid grid-cols-2 gap-2">
              {(["despesa", "receita"] as const).map((t) => (
                <button
                  key={t}
                  type="button"
                  onClick={() => setTipo(t)}
                  className={`rounded-lg border px-3 py-2 text-sm font-medium capitalize transition-all ${
                    tipo === t
                      ? t === "despesa"
                        ? "border-rose-500/40 bg-rose-500/10 text-rose-300"
                        : "border-emerald-500/40 bg-emerald-500/10 text-emerald-300"
                      : "border-white/10 bg-white/5 text-slate-400 hover:text-white"
                  }`}
                >
                  {t}
                </button>
              ))}
            </div>

            <div>
              <label className="mb-1 block text-xs text-slate-400">Categoria</label>
              <select
                value={categoria}
                onChange={(e) => setCategoria(e.target.value)}
                className="w-full rounded-lg border border-white/10 bg-ink-900/60 px-3 py-2 text-sm text-white focus:border-brand/50 focus:outline-none"
              >
                {categorias.map((c) => (
                  <option key={c} value={c}>
                    {c}
                  </option>
                ))}
              </select>
            </div>

            <div className="grid grid-cols-2 gap-2">
              <div>
                <label className="mb-1 block text-xs text-slate-400">Valor (R$)</label>
                <input
                  value={valor}
                  onChange={(e) => setValor(e.target.value)}
                  inputMode="decimal"
                  placeholder="0,00"
                  className="w-full rounded-lg border border-white/10 bg-ink-900/60 px-3 py-2 text-sm text-white focus:border-brand/50 focus:outline-none"
                />
              </div>
              <div>
                <label className="mb-1 block text-xs text-slate-400">Data</label>
                <input
                  type="date"
                  value={data}
                  onChange={(e) => setData(e.target.value)}
                  className="w-full rounded-lg border border-white/10 bg-ink-900/60 px-3 py-2 text-sm text-white focus:border-brand/50 focus:outline-none"
                />
              </div>
            </div>

            <div>
              <label className="mb-1 block text-xs text-slate-400">Descrição (opcional)</label>
              <input
                value={descricao}
                onChange={(e) => setDescricao(e.target.value)}
                placeholder="Ex.: aluguel, mercado..."
                className="w-full rounded-lg border border-white/10 bg-ink-900/60 px-3 py-2 text-sm text-white focus:border-brand/50 focus:outline-none"
              />
            </div>

            <label className="flex items-center gap-2 text-sm text-slate-300">
              <input type="checkbox" checked={recorrente} onChange={(e) => setRecorrente(e.target.checked)} className="accent-brand" />
              Lançamento recorrente (todo mês)
            </label>

            <button
              type="submit"
              disabled={salvando}
              className="flex w-full items-center justify-center gap-2 rounded-lg bg-gradient-to-r from-brand to-accent-cyan px-4 py-2.5 text-sm font-semibold text-ink-950 transition-all hover:opacity-90 disabled:opacity-50"
            >
              <Plus size={16} /> {salvando ? "Salvando..." : "Adicionar"}
            </button>
          </form>
        </GlassCard>

        {/* Gráficos */}
        <GlassCard title="Fluxo dos últimos 6 meses" className="lg:col-span-2">
          <ResponsiveContainer width="100%" height={240}>
            <BarChart data={resumo?.serie_mensal ?? []}>
              <XAxis dataKey="mes" tick={{ fill: "#94a3b8", fontSize: 12 }} axisLine={false} tickLine={false} />
              <YAxis tick={{ fill: "#94a3b8", fontSize: 12 }} axisLine={false} tickLine={false} width={40} />
              <Tooltip
                contentStyle={{ background: "#0f1115", border: "1px solid rgba(255,255,255,0.1)", borderRadius: 12 }}
                formatter={(v: number) => brl(v)}
              />
              <Legend wrapperStyle={{ fontSize: 12 }} />
              <Bar dataKey="receitas" name="Receitas" fill="#22d3a5" radius={[4, 4, 0, 0]} />
              <Bar dataKey="despesas" name="Despesas" fill="#fb7185" radius={[4, 4, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </GlassCard>
      </div>

      <div className="mt-6 grid gap-6 lg:grid-cols-3">
        <GlassCard title="Despesas por categoria" className="lg:col-span-1">
          {pieData.length === 0 ? (
            <p className="py-12 text-center text-sm text-slate-500">Sem despesas neste mês.</p>
          ) : (
            <ResponsiveContainer width="100%" height={260}>
              <PieChart>
                <Pie data={pieData} dataKey="value" nameKey="name" cx="50%" cy="50%" innerRadius={55} outerRadius={90} paddingAngle={2}>
                  {pieData.map((_, i) => (
                    <Cell key={i} fill={PIE_COLORS[i % PIE_COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip
                  contentStyle={{ background: "#0f1115", border: "1px solid rgba(255,255,255,0.1)", borderRadius: 12 }}
                  formatter={(v: number) => brl(v)}
                />
              </PieChart>
            </ResponsiveContainer>
          )}
        </GlassCard>

        <GlassCard title="Lançamentos" subtitle="Histórico recente" className="lg:col-span-2 !p-0 overflow-hidden">
          <div className="max-h-[360px] overflow-y-auto">
            <table className="w-full text-sm">
              <thead className="sticky top-0 border-b border-white/10 bg-ink-900/80 text-left text-xs uppercase tracking-wider text-slate-500 backdrop-blur">
                <tr>
                  <th className="px-5 py-3 font-medium">Data</th>
                  <th className="px-5 py-3 font-medium">Categoria</th>
                  <th className="px-5 py-3 text-right font-medium">Valor</th>
                  <th className="px-5 py-3"></th>
                </tr>
              </thead>
              <tbody>
                {lancamentos.map((l) => (
                  <tr key={l.id} className="border-b border-white/5 hover:bg-white/[0.03]">
                    <td className="px-5 py-3 text-slate-400">{l.data.split("-").reverse().join("/")}</td>
                    <td className="px-5 py-3">
                      <span className="font-medium text-white">{l.categoria}</span>
                      {l.descricao && <span className="ml-2 text-xs text-slate-500">{l.descricao}</span>}
                    </td>
                    <td className={`px-5 py-3 text-right font-mono font-semibold ${l.tipo === "receita" ? "text-emerald-400" : "text-rose-400"}`}>
                      {l.tipo === "receita" ? "+" : "-"}
                      {brl(l.valor)}
                    </td>
                    <td className="px-5 py-3 text-right">
                      <button onClick={() => remover(l.id)} className="text-slate-600 transition-colors hover:text-rose-400">
                        <Trash2 size={15} />
                      </button>
                    </td>
                  </tr>
                ))}
                {lancamentos.length === 0 && (
                  <tr>
                    <td colSpan={4} className="px-5 py-12 text-center text-slate-500">
                      Nenhum lançamento ainda. Adicione o primeiro ao lado.
                    </td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>
        </GlassCard>
      </div>
    </div>
  );
}
