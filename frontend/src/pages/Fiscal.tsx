import { useEffect, useState } from "react";
import { ShieldCheck, AlertTriangle, OctagonAlert } from "lucide-react";
import PageHeader from "../components/PageHeader";
import GlassCard from "../components/GlassCard";
import { api } from "../lib/api";
import { brl } from "../lib/format";
import type { Isentometro, RelatorioIR } from "../lib/types";

const MESES = ["Jan", "Fev", "Mar", "Abr", "Mai", "Jun", "Jul", "Ago", "Set", "Out", "Nov", "Dez"];

const statusMap = {
  verde: { cor: "text-emerald-400", barra: "from-emerald-500 to-emerald-400", icon: ShieldCheck, label: "Isento" },
  amarelo: { cor: "text-amber-400", barra: "from-amber-500 to-amber-400", icon: AlertTriangle, label: "Atenção" },
  vermelho: { cor: "text-rose-400", barra: "from-rose-500 to-rose-400", icon: OctagonAlert, label: "Tributável" },
} as const;

export default function Fiscal() {
  const agora = new Date();
  const [ano, setAno] = useState(agora.getFullYear());
  const [mes, setMes] = useState(agora.getMonth() + 1);
  const [anoIr, setAnoIr] = useState(2024);
  const [iso, setIso] = useState<Isentometro | null>(null);
  const [ir, setIr] = useState<RelatorioIR | null>(null);

  useEffect(() => {
    api.get<Isentometro>(`/fiscal/isentometro?ano=${ano}&mes=${mes}`).then((r) => setIso(r.data)).catch(() => undefined);
  }, [ano, mes]);

  useEffect(() => {
    api.get<RelatorioIR>(`/fiscal/relatorio-ir?ano=${anoIr}`).then((r) => setIr(r.data)).catch(() => undefined);
  }, [anoIr]);

  const st = iso ? statusMap[iso.status] : statusMap.verde;
  const StatusIcon = st.icon;
  const largura = iso ? Math.min(iso.percentual_teto, 100) : 0;

  return (
    <div>
      <PageHeader
        eyebrow="Controle Fiscal"
        title="Imposto de Renda"
        description="Isentômetro mensal de vendas de ações e relatório de Bens e Direitos (posição 31/12)."
      />

      <div className="grid gap-4 lg:grid-cols-2">
        <GlassCard
          title="Isentômetro"
          subtitle="Vendas de ações no mês vs teto de isenção (R$ 20.000)"
          action={
            <div className="flex gap-2">
              <select value={mes} onChange={(e) => setMes(+e.target.value)} className="rounded-lg border border-white/10 bg-ink-800 px-2 py-1 text-sm text-slate-200">
                {MESES.map((m, i) => <option key={m} value={i + 1}>{m}</option>)}
              </select>
              <select value={ano} onChange={(e) => setAno(+e.target.value)} className="rounded-lg border border-white/10 bg-ink-800 px-2 py-1 text-sm text-slate-200">
                {[2023, 2024, 2025, 2026].map((a) => <option key={a} value={a}>{a}</option>)}
              </select>
            </div>
          }
        >
          {iso && (
            <div>
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <StatusIcon className={st.cor} size={20} />
                  <span className={`font-semibold ${st.cor}`}>{st.label}</span>
                </div>
                <span className="font-mono text-sm text-slate-400">{iso.percentual_teto.toFixed(1)}% do teto</span>
              </div>
              <div className="mt-3 h-3 w-full overflow-hidden rounded-full bg-white/5">
                <div className={`h-full rounded-full bg-gradient-to-r ${st.barra}`} style={{ width: `${largura}%` }} />
              </div>
              <div className="mt-5 grid grid-cols-2 gap-4 text-sm">
                <Info label="Vendas no mês" valor={brl(iso.total_vendas)} />
                <Info label="Teto de isenção" valor={brl(iso.teto)} />
                <Info label="Lucro realizado" valor={brl(iso.lucro_realizado)} tone={iso.lucro_realizado >= 0 ? "pos" : "neg"} />
                <Info label="Imposto estimado (15%)" valor={brl(iso.imposto_estimado)} tone={iso.imposto_estimado > 0 ? "neg" : undefined} />
              </div>
            </div>
          )}
        </GlassCard>

        <GlassCard
          title="Bens e Direitos"
          subtitle={ir ? `Posição em ${new Date(ir.data_posicao).toLocaleDateString("pt-BR")}` : "Posição em 31/12"}
          action={
            <select value={anoIr} onChange={(e) => setAnoIr(+e.target.value)} className="rounded-lg border border-white/10 bg-ink-800 px-2 py-1 text-sm text-slate-200">
              {[2023, 2024, 2025].map((a) => <option key={a} value={a}>{a}</option>)}
            </select>
          }
        >
          {ir && (
            <div className="space-y-3">
              {ir.itens.map((b) => (
                <div key={b.ticker} className="rounded-lg border border-white/5 bg-white/[0.02] p-3">
                  <div className="flex items-center justify-between">
                    <span className="font-semibold text-white">{b.ticker}</span>
                    <span className="font-mono text-sm text-brand">{brl(b.valor_total)}</span>
                  </div>
                  <p className="mt-1 text-xs text-slate-500">{b.discriminacao}</p>
                </div>
              ))}
              <div className="flex items-center justify-between border-t border-white/10 pt-3 text-sm">
                <span className="text-slate-400">Total declarado</span>
                <span className="font-display font-bold text-white">{brl(ir.total)}</span>
              </div>
              {ir.itens.length === 0 && <p className="py-6 text-center text-slate-500">Sem posição neste ano.</p>}
            </div>
          )}
        </GlassCard>
      </div>
    </div>
  );
}

function Info({ label, valor, tone }: { label: string; valor: string; tone?: "pos" | "neg" }) {
  const cor = tone === "pos" ? "text-emerald-400" : tone === "neg" ? "text-rose-400" : "text-white";
  return (
    <div className="rounded-lg border border-white/5 bg-white/[0.02] p-3">
      <p className="text-xs text-slate-500">{label}</p>
      <p className={`mt-1 font-mono font-semibold ${cor}`}>{valor}</p>
    </div>
  );
}
