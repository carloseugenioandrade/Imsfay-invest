import { useEffect, useState } from "react";
import PageHeader from "../components/PageHeader";
import GlassCard from "../components/GlassCard";
import { api } from "../lib/api";
import { brl, pct } from "../lib/format";
import type { RankingItem } from "../lib/types";

export default function Valuation() {
  const [itens, setItens] = useState<RankingItem[]>([]);
  const [erro, setErro] = useState<string | null>(null);

  useEffect(() => {
    api
      .get<{ items: RankingItem[] }>("/valuation/ranking")
      .then((r) => setItens(r.data.items))
      .catch(() => setErro("Não foi possível carregar o ranking."));
  }, []);

  return (
    <div>
      <PageHeader
        eyebrow="Margem de Segurança"
        title="Valuation"
        description="Ranking por Preço Justo (Graham) e Preço Teto (Bazin), além de calculadoras manuais."
      />

      {erro && <div className="glass mb-4 border-rose-500/30 p-4 text-rose-300">{erro}</div>}

      <GlassCard className="!p-0 overflow-hidden" title="" >
        <table className="w-full text-sm">
          <thead className="border-b border-white/10 text-left text-xs uppercase tracking-wider text-slate-500">
            <tr>
              <th className="px-6 py-4 font-medium">Ativo</th>
              <th className="px-6 py-4 text-right font-medium">Preço atual</th>
              <th className="px-6 py-4 text-right font-medium">Justo (Graham)</th>
              <th className="px-6 py-4 text-right font-medium">Upside</th>
              <th className="px-6 py-4 text-right font-medium">Teto (Bazin)</th>
              <th className="px-6 py-4 text-center font-medium">Situação</th>
            </tr>
          </thead>
          <tbody>
            {itens.map((it) => (
              <tr key={it.ticker} className="border-b border-white/5 transition-colors hover:bg-white/[0.03]">
                <td className="px-6 py-4 font-display font-bold text-white">{it.ticker}</td>
                <td className="px-6 py-4 text-right font-mono text-slate-300">{brl(it.preco_atual)}</td>
                <td className="px-6 py-4 text-right font-mono text-slate-300">{it.preco_justo != null ? brl(it.preco_justo) : "—"}</td>
                <td className="px-6 py-4 text-right">
                  {it.upside_pct != null ? (
                    <span className={`font-mono font-semibold ${it.upside_pct >= 0 ? "text-emerald-400" : "text-rose-400"}`}>{pct(it.upside_pct)}</span>
                  ) : "—"}
                </td>
                <td className="px-6 py-4 text-right font-mono text-slate-300">{it.preco_teto != null ? brl(it.preco_teto) : "—"}</td>
                <td className="px-6 py-4 text-center">
                  {it.abaixo_teto == null ? (
                    <span className="text-slate-600">—</span>
                  ) : (
                    <span className={`rounded-md px-2 py-1 text-[11px] font-semibold ${it.abaixo_teto ? "bg-emerald-400/10 text-emerald-400" : "bg-rose-400/10 text-rose-400"}`}>
                      {it.abaixo_teto ? "Abaixo do teto" : "Acima do teto"}
                    </span>
                  )}
                </td>
              </tr>
            ))}
            {itens.length === 0 && !erro && (
              <tr><td colSpan={6} className="px-6 py-12 text-center text-slate-500">Sem dados de indicadores. Rode o seed.</td></tr>
            )}
          </tbody>
        </table>
      </GlassCard>

      <div className="mt-6 grid gap-4 lg:grid-cols-2">
        <CalculadoraGraham />
        <CalculadoraBazin />
      </div>
    </div>
  );
}

function CalculadoraGraham() {
  const [lpa, setLpa] = useState("");
  const [vpa, setVpa] = useState("");
  const [preco, setPreco] = useState("");
  const [res, setRes] = useState<{ preco_justo: number | null; upside_pct: number | null } | null>(null);

  const calcular = async () => {
    const r = await api.get(`/valuation/graham?lpa=${lpa}&vpa=${vpa}&preco_atual=${preco}`);
    setRes(r.data);
  };

  return (
    <GlassCard title="Calculadora Graham" subtitle="Preço justo = √(22,5 × LPA × VPA)">
      <div className="grid grid-cols-3 gap-2">
        <Campo label="LPA" value={lpa} onChange={setLpa} />
        <Campo label="VPA" value={vpa} onChange={setVpa} />
        <Campo label="Preço atual" value={preco} onChange={setPreco} />
      </div>
      <Botao onClick={calcular} />
      {res && (
        <div className="mt-4 flex items-center justify-between rounded-lg border border-white/5 bg-white/[0.02] p-4">
          <div>
            <p className="text-xs text-slate-500">Preço justo</p>
            <p className="font-display text-lg font-bold text-white">{res.preco_justo != null ? brl(res.preco_justo) : "—"}</p>
          </div>
          {res.upside_pct != null && (
            <span className={`font-display text-lg font-bold ${res.upside_pct >= 0 ? "text-emerald-400" : "text-rose-400"}`}>{pct(res.upside_pct)}</span>
          )}
        </div>
      )}
    </GlassCard>
  );
}

function CalculadoraBazin() {
  const [div5, setDiv5] = useState("");
  const [preco, setPreco] = useState("");
  const [res, setRes] = useState<{ preco_teto: number | null; abaixo_do_teto: boolean | null } | null>(null);

  const calcular = async () => {
    const r = await api.get(`/valuation/bazin?dividendos_medios_5_anos=${div5}&preco_atual=${preco}`);
    setRes(r.data);
  };

  return (
    <GlassCard title="Calculadora Bazin" subtitle="Preço teto = dividendo médio ÷ 6%">
      <div className="grid grid-cols-2 gap-2">
        <Campo label="Div. médio 5 anos" value={div5} onChange={setDiv5} />
        <Campo label="Preço atual" value={preco} onChange={setPreco} />
      </div>
      <Botao onClick={calcular} />
      {res && (
        <div className="mt-4 flex items-center justify-between rounded-lg border border-white/5 bg-white/[0.02] p-4">
          <div>
            <p className="text-xs text-slate-500">Preço teto</p>
            <p className="font-display text-lg font-bold text-white">{res.preco_teto != null ? brl(res.preco_teto) : "—"}</p>
          </div>
          {res.abaixo_do_teto != null && (
            <span className={`rounded-md px-2 py-1 text-xs font-semibold ${res.abaixo_do_teto ? "bg-emerald-400/10 text-emerald-400" : "bg-rose-400/10 text-rose-400"}`}>
              {res.abaixo_do_teto ? "Abaixo do teto" : "Acima do teto"}
            </span>
          )}
        </div>
      )}
    </GlassCard>
  );
}

function Campo({ label, value, onChange }: { label: string; value: string; onChange: (v: string) => void }) {
  return (
    <label className="block">
      <span className="text-xs text-slate-500">{label}</span>
      <input
        type="number"
        value={value}
        onChange={(e) => onChange(e.target.value)}
        className="mt-1 w-full rounded-lg border border-white/10 bg-ink-800 px-3 py-2 text-sm text-white outline-none focus:border-brand/50"
      />
    </label>
  );
}

function Botao({ onClick }: { onClick: () => void }) {
  return (
    <button
      onClick={onClick}
      className="mt-4 w-full rounded-lg bg-gradient-to-r from-brand to-accent-cyan px-4 py-2.5 text-sm font-semibold text-ink-950 transition-opacity hover:opacity-90"
    >
      Calcular
    </button>
  );
}
