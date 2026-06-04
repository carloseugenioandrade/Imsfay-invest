import PageHeader from "../components/PageHeader";

export default function Fiscal() {
  return (
    <div>
      <PageHeader
        title="Fiscal"
        description="Isentômetro mensal e auxílio ao IR (Bens e Direitos / DARF)."
      />
      {/* TODO: barra de progresso do Isentômetro e gerador de relatório IR */}
      <div className="rounded-xl border border-dashed border-slate-300 p-12 text-center text-slate-400">
        Em construção — Isentômetro e relatório de IR.
      </div>
    </div>
  );
}
