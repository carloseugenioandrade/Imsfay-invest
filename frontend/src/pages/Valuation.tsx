import PageHeader from "../components/PageHeader";

export default function Valuation() {
  return (
    <div>
      <PageHeader
        title="Valuation"
        description="Preço Justo (Graham), Preço Teto (Bazin) e rankings de margem de segurança."
      />
      {/* TODO: formulários Graham/Bazin e tabela de ranking com Upside */}
      <div className="rounded-xl border border-dashed border-slate-300 p-12 text-center text-slate-400">
        Em construção — calculadoras e rankings de valuation.
      </div>
    </div>
  );
}
