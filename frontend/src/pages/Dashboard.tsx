import PageHeader from "../components/PageHeader";

export default function Dashboard() {
  return (
    <div>
      <PageHeader
        title="Dashboard"
        description="Visão geral do patrimônio, rentabilidade e alertas."
      />
      {/* TODO: cards de patrimônio, gráfico de evolução vs Ibovespa/CDI, proventos do mês */}
      <div className="rounded-xl border border-dashed border-slate-300 p-12 text-center text-slate-400">
        Em construção — consolidação de patrimônio e indicadores.
      </div>
    </div>
  );
}
