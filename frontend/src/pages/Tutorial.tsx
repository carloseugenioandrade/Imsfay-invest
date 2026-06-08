import {
  LayoutDashboard,
  Wallet,
  Calculator,
  Coins,
  Receipt,
  LineChart,
  PiggyBank,
  GraduationCap,
  Upload,
  Compass,
} from "lucide-react";
import PageHeader from "../components/PageHeader";
import GlassCard from "../components/GlassCard";

const passosRapidos = [
  {
    icon: GraduationCap,
    titulo: "1. Comece pela Jornada",
    texto: "Responda o quiz de perfil e siga a trilha personalizada: quitar dívidas, montar reserva e começar a investir.",
  },
  {
    icon: PiggyBank,
    titulo: "2. Organize suas finanças",
    texto: "Lance receitas e despesas no Organizador Financeiro para saber quanto sobra para investir todo mês.",
  },
  {
    icon: Upload,
    titulo: "3. Importe sua carteira",
    texto: "Na Carteira, importe seu extrato da B3 (XLSX ou PDF) e veja suas posições consolidadas automaticamente.",
  },
  {
    icon: Calculator,
    titulo: "4. Avalie e acompanhe",
    texto: "Use Valuation, Dividendos e Fiscal para tomar decisões melhores e ficar em dia com o imposto de renda.",
  },
];

const areas = [
  { icon: LayoutDashboard, nome: "Dashboard", desc: "Visão geral do seu patrimônio, alocação e principais indicadores em um só lugar." },
  { icon: PiggyBank, nome: "Organizador Financeiro", desc: "Controle de receitas e despesas com gráficos, categorias e taxa de poupança mensal." },
  { icon: GraduationCap, nome: "Liberdade Financeira", desc: "Trilha guiada do zero ao investidor: perfil, dívidas, reserva de emergência e investimentos." },
  { icon: Wallet, nome: "Carteira", desc: "Posições consolidadas com preço médio, cotação atual e rentabilidade. Importa extrato da B3." },
  { icon: Calculator, nome: "Valuation", desc: "Preço justo (Graham) e preço teto (Bazin) para identificar boas oportunidades de compra." },
  { icon: Coins, nome: "Dividendos", desc: "Acompanhe proventos recebidos, yield on cost e a agenda preditiva de pagamentos." },
  { icon: Receipt, nome: "Fiscal", desc: "Isentômetro de vendas, imposto estimado e relatório de bens e direitos para o IR." },
  { icon: LineChart, nome: "Juros Compostos", desc: "Simule o crescimento do seu patrimônio no tempo com aportes mensais." },
];

export default function Tutorial() {
  return (
    <div>
      <PageHeader
        eyebrow="Tutorial"
        title="Como usar o Imsfay Invest"
        description="Um guia rápido para você aproveitar 100% da plataforma — do controle de gastos até a construção de uma carteira de longo prazo."
      />

      <GlassCard title="Por onde começar" subtitle="Siga esta ordem para tirar o máximo proveito" className="mb-6">
        <div className="grid gap-4 sm:grid-cols-2">
          {passosRapidos.map(({ icon: Icon, titulo, texto }) => (
            <div key={titulo} className="flex gap-3 rounded-xl border border-white/10 bg-white/[0.02] p-4">
              <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-lg bg-brand/15 text-brand">
                <Icon size={20} />
              </div>
              <div>
                <p className="font-semibold text-white">{titulo}</p>
                <p className="mt-1 text-sm text-slate-400">{texto}</p>
              </div>
            </div>
          ))}
        </div>
      </GlassCard>

      <GlassCard title="Conheça cada área" subtitle="O que você encontra em cada aba do menu">
        <div className="grid gap-3 sm:grid-cols-2">
          {areas.map(({ icon: Icon, nome, desc }) => (
            <div key={nome} className="flex items-start gap-3 rounded-xl p-3 transition-colors hover:bg-white/[0.03]">
              <Icon size={18} className="mt-0.5 shrink-0 text-accent-cyan" />
              <div>
                <p className="font-medium text-white">{nome}</p>
                <p className="text-sm text-slate-400">{desc}</p>
              </div>
            </div>
          ))}
        </div>
      </GlassCard>

      <div className="mt-6 flex items-center gap-3 rounded-2xl border border-brand/30 bg-brand/[0.06] p-5">
        <Compass size={24} className="shrink-0 text-brand" />
        <p className="text-sm text-slate-300">
          <strong className="text-white">Dica:</strong> a plataforma é progressiva. Quanto mais você preenche (gastos, renda, carteira), mais
          personalizadas ficam as recomendações da sua jornada de liberdade financeira.
        </p>
      </div>
    </div>
  );
}
