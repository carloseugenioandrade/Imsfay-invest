import { useEffect, useRef, useState } from "react";
import { Upload } from "lucide-react";
import PageHeader from "../components/PageHeader";
import GlassCard from "../components/GlassCard";
import { api } from "../lib/api";
import { brl, pct } from "../lib/format";
import type { Posicao } from "../lib/types";

const tipoBadge: Record<string, string> = {
  Acao: "bg-brand/15 text-brand",
  FII: "bg-accent-violet/15 text-accent-violet",
  ETF: "bg-accent-cyan/15 text-accent-cyan",
  Stock: "bg-amber-400/15 text-amber-300",
  REIT: "bg-sky-400/15 text-sky-300",
  Cripto: "bg-orange-400/15 text-orange-300",
};

export default function Carteira() {
  const [posicoes, setPosicoes] = useState<Posicao[]>([]);
  const [erro, setErro] = useState<string | null>(null);
  const [msg, setMsg] = useState<string | null>(null);
  const [importando, setImportando] = useState(false);
  const inputRef = useRef<HTMLInputElement>(null);

  const carregar = () => {
    api
      .get<{ items: Posicao[] }>("/carteira/posicoes")
      .then((r) => setPosicoes(r.data.items))
      .catch(() => setErro("Não foi possível carregar as posições."));
  };

  useEffect(() => {
    carregar();
  }, []);

  const importar = async (file: File) => {
    setImportando(true);
    setErro(null);
    setMsg(null);
    const form = new FormData();
    form.append("file", file);
    try {
      const r = await api.post("/transacoes/importar", form);
      const d = r.data;
      setMsg(`Importado: ${d.inseridas} inseridas, ${d.duplicadas} duplicadas, ${d.ativos_criados} ativos criados.`);
      carregar();
    } catch (e: unknown) {
      const err = e as { response?: { data?: { detail?: string } }; request?: unknown };
      const detail = err?.response?.data?.detail;
      if (detail) {
        setErro(detail);
      } else if (err?.request) {
        setErro(
          `Não foi possível falar com o servidor (${api.defaults.baseURL}). Verifique se o backend está rodando e se VITE_API_URL aponta para ele.`,
        );
      } else {
        setErro("Falha ao importar o extrato.");
      }
    } finally {
      setImportando(false);
      if (inputRef.current) inputRef.current.value = "";
    }
  };

  return (
    <div>
      <div className="flex items-start justify-between gap-4">
        <PageHeader
          eyebrow="Gestão de Carteira"
          title="Carteira"
          description="Posições consolidadas com preço médio, cotação atual e rentabilidade por ativo."
        />
        <button
          onClick={() => inputRef.current?.click()}
          disabled={importando}
          className="flex shrink-0 items-center gap-2 rounded-xl border border-white/10 bg-white/5 px-4 py-2.5 text-sm font-medium text-slate-200 transition-all hover:border-brand/40 hover:bg-brand/10 hover:text-white disabled:opacity-50"
        >
          <Upload size={16} className="text-brand" />
          {importando ? "Importando..." : "Importar extrato B3 (XLSX/PDF)"}
        </button>
        <input
          ref={inputRef}
          type="file"
          accept=".xlsx,.xls,.pdf"
          className="hidden"
          onChange={(e) => e.target.files?.[0] && importar(e.target.files[0])}
        />
      </div>

      {erro && <div className="glass mb-4 border-rose-500/30 p-4 text-rose-300">{erro}</div>}
      {msg && <div className="glass mb-4 border-brand/30 p-4 text-brand">{msg}</div>}

      <GlassCard className="!p-0 overflow-hidden">
        <table className="w-full text-sm">
          <thead className="border-b border-white/10 text-left text-xs uppercase tracking-wider text-slate-500">
            <tr>
              <th className="px-6 py-4 font-medium">Ativo</th>
              <th className="px-6 py-4 text-right font-medium">Qtde</th>
              <th className="px-6 py-4 text-right font-medium">Preço médio</th>
              <th className="px-6 py-4 text-right font-medium">Preço atual</th>
              <th className="px-6 py-4 text-right font-medium">Valor atual</th>
              <th className="px-6 py-4 text-right font-medium">Rentab.</th>
            </tr>
          </thead>
          <tbody>
            {posicoes.map((p) => (
              <tr key={p.ativo_id} className="border-b border-white/5 transition-colors hover:bg-white/[0.03]">
                <td className="px-6 py-4">
                  <div className="flex items-center gap-3">
                    <span className={`rounded-md px-2 py-0.5 text-[11px] font-semibold ${tipoBadge[p.tipo] ?? "bg-white/10 text-slate-300"}`}>
                      {p.tipo}
                    </span>
                    <div>
                      <div className="font-semibold text-white">{p.ticker}</div>
                      <div className="text-xs text-slate-500">{p.setor ?? "-"}</div>
                    </div>
                  </div>
                </td>
                <td className="px-6 py-4 text-right font-mono text-slate-300">{p.quantidade}</td>
                <td className="px-6 py-4 text-right font-mono text-slate-300">{brl(p.preco_medio)}</td>
                <td className="px-6 py-4 text-right font-mono text-slate-300">{p.preco_atual != null ? brl(p.preco_atual) : "-"}</td>
                <td className="px-6 py-4 text-right font-mono font-semibold text-white">{brl(p.valor_atual)}</td>
                <td className="px-6 py-4 text-right">
                  <span className={`rounded-md px-2 py-1 font-mono text-xs font-semibold ${p.rentabilidade_pct >= 0 ? "bg-emerald-400/10 text-emerald-400" : "bg-rose-400/10 text-rose-400"}`}>
                    {pct(p.rentabilidade_pct)}
                  </span>
                </td>
              </tr>
            ))}
            {posicoes.length === 0 && !erro && (
              <tr>
                <td colSpan={6} className="px-6 py-12 text-center text-slate-500">
                  Nenhuma posição. Rode o seed ou cadastre transações.
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </GlassCard>
    </div>
  );
}
