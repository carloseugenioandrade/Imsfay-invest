import PageHeader from "../components/PageHeader";

export default function Dividendos() {
  return (
    <div>
      <PageHeader
        title="Dividendos"
        description="Evolução de proventos, Yield on Cost e agenda preditiva (IA)."
      />
      {/* TODO: gráfico de proventos mês a mês, agenda preditiva por mês/ativo */}
      <div className="rounded-xl border border-dashed border-slate-300 p-12 text-center text-slate-400">
        Em construção — Dividendos Inteligentes e agenda preditiva.
      </div>
    </div>
  );
}
