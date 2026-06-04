import PageHeader from "../components/PageHeader";

export default function Carteira() {
  return (
    <div>
      <PageHeader
        title="Carteira"
        description="Posições, preço médio, rentabilidade (TWR) e consolidação por classe/setor."
      />
      {/* TODO: tabela de posições, gráficos de alocação, importar extrato B3 */}
      <div className="rounded-xl border border-dashed border-slate-300 p-12 text-center text-slate-400">
        Em construção — gestão de carteira e importação de extratos.
      </div>
    </div>
  );
}
