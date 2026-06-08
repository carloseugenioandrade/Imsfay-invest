export interface Posicao {
  ativo_id: number;
  ticker: string;
  nome: string;
  tipo: string;
  setor: string | null;
  quantidade: number;
  preco_medio: number;
  preco_atual: number | null;
  valor_investido: number;
  valor_atual: number;
  lucro: number;
  rentabilidade_pct: number;
}

export interface Alocacao {
  nome: string;
  valor: number;
}

export interface ResumoCarteira {
  valor_atual: number;
  valor_investido: number;
  lucro: number;
  rentabilidade_pct: number;
  quantidade_ativos: number;
  alocacao_por_classe: Alocacao[];
  alocacao_por_setor: Alocacao[];
  posicoes: Posicao[];
}

export interface RankingItem {
  ticker: string;
  preco_atual: number;
  preco_justo: number | null;
  upside_pct: number | null;
  preco_teto: number | null;
  abaixo_teto: boolean | null;
}

export interface EvolucaoPonto {
  data: string;
  patrimonio: number;
  investido: number;
  cdi?: number;
}

export interface Isentometro {
  ano: number;
  mes: number;
  total_vendas: number;
  teto: number;
  percentual_teto: number;
  isento: boolean;
  status: "verde" | "amarelo" | "vermelho";
  lucro_realizado: number;
  imposto_estimado: number;
}

export interface BemDireito {
  ticker: string;
  nome: string;
  tipo: string;
  quantidade: number;
  preco_medio: number;
  valor_total: number;
  discriminacao: string;
}

export interface RelatorioIR {
  ano: number;
  data_posicao: string;
  total: number;
  itens: BemDireito[];
}

export interface ProventoResumo {
  total_recebido: number;
  yield_on_cost_pct: number;
  custo_base: number;
  evolucao_mensal: { mes: string; valor: number }[];
  por_ano: { ano: number; valor: number }[];
}

export interface MesProbabilidade {
  mes: string;
  probabilidade: number;
}

export interface AgendaPreditiva {
  carteira: MesProbabilidade[];
  por_ativo: { ticker: string; meses: MesProbabilidade[] }[];
}

// ===== Organizador Financeiro =====
export interface Lancamento {
  id: number;
  tipo: "receita" | "despesa";
  categoria: string;
  descricao: string | null;
  valor: number;
  data: string;
  recorrente: boolean;
}

export interface ResumoFinanceiro {
  mes_referencia: string;
  receitas: number;
  despesas: number;
  saldo: number;
  taxa_poupanca: number;
  por_categoria: { categoria: string; valor: number }[];
  serie_mensal: { mes: string; receitas: number; despesas: number; saldo: number }[];
}

export interface PerfilFinanceiro {
  id: number;
  renda_mensal: number;
  gasto_mensal_estimado: number;
  total_dividas: number;
  reserva_atual: number;
  meses_reserva_meta: number;
  perfil_investidor: string | null;
  score_perfil: number;
  onboarding_completo: boolean;
}

// ===== Jornada =====
export interface Capitulo {
  id: string;
  titulo: string;
  subtitulo: string;
  icone: string;
  tipo: "quiz" | "form" | "leitura";
  done: boolean;
  status: "done" | "active" | "locked";
  resumo: string;
  passos?: string[];
  metrica?: Record<string, number | string | Record<string, number>>;
}

export interface Trilha {
  perfil_investidor: string | null;
  progresso_pct: number;
  capitulos_total: number;
  capitulos_concluidos: number;
  capitulos: Capitulo[];
}

export interface PerguntaQuiz {
  pergunta: string;
  opcoes: string[];
}
