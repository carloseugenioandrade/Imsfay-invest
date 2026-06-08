import { useEffect, useState } from "react";
import {
  Compass,
  ClipboardList,
  Flame,
  ShieldCheck,
  Rocket,
  Infinity as InfinityIcon,
  Lock,
  Check,
  ChevronRight,
} from "lucide-react";
import PageHeader from "../components/PageHeader";
import GlassCard from "../components/GlassCard";
import { api } from "../lib/api";
import { brl } from "../lib/format";
import type { Capitulo, PerfilFinanceiro, PerguntaQuiz, Trilha } from "../lib/types";

const ICONS: Record<string, typeof Compass> = {
  compass: Compass,
  clipboard: ClipboardList,
  flame: Flame,
  shield: ShieldCheck,
  rocket: Rocket,
  infinity: InfinityIcon,
};

function renderInline(text: string) {
  // Converte **negrito** simples em <strong>.
  const parts = text.split(/(\*\*[^*]+\*\*)/g);
  return parts.map((p, i) =>
    p.startsWith("**") && p.endsWith("**") ? (
      <strong key={i} className="font-semibold text-white">
        {p.slice(2, -2)}
      </strong>
    ) : (
      <span key={i}>{p}</span>
    ),
  );
}

/* ===== Quiz ===== */
function Quiz({ onDone }: { onDone: () => void }) {
  const [perguntas, setPerguntas] = useState<PerguntaQuiz[]>([]);
  const [idx, setIdx] = useState(0);
  const [respostas, setRespostas] = useState<number[]>([]);
  const [enviando, setEnviando] = useState(false);

  useEffect(() => {
    api.get<{ perguntas: PerguntaQuiz[] }>("/jornada/quiz").then((r) => setPerguntas(r.data.perguntas));
  }, []);

  if (perguntas.length === 0) return <p className="text-slate-400">Carregando quiz...</p>;

  const responder = async (opcao: number) => {
    const novas = [...respostas, opcao];
    if (idx + 1 < perguntas.length) {
      setRespostas(novas);
      setIdx(idx + 1);
    } else {
      setEnviando(true);
      await api.post("/jornada/quiz", { respostas: novas });
      onDone();
    }
  };

  const p = perguntas[idx];
  const progresso = Math.round((idx / perguntas.length) * 100);

  return (
    <div>
      <div className="mb-4 h-1.5 w-full overflow-hidden rounded-full bg-white/10">
        <div className="h-full rounded-full bg-gradient-to-r from-brand to-accent-cyan transition-all" style={{ width: `${progresso}%` }} />
      </div>
      <p className="mb-1 text-xs uppercase tracking-wider text-brand">
        Pergunta {idx + 1} de {perguntas.length}
      </p>
      <h3 className="mb-5 font-display text-xl font-semibold text-white">{p.pergunta}</h3>
      <div className="space-y-2">
        {p.opcoes.map((o, i) => (
          <button
            key={i}
            disabled={enviando}
            onClick={() => responder(i)}
            className="flex w-full items-center justify-between rounded-xl border border-white/10 bg-white/[0.02] px-4 py-3 text-left text-sm text-slate-200 transition-all hover:border-brand/40 hover:bg-brand/10 disabled:opacity-50"
          >
            {o}
            <ChevronRight size={16} className="text-slate-500" />
          </button>
        ))}
      </div>
    </div>
  );
}

/* ===== Editor de capítulos do tipo "form" ===== */
function FormCapitulo({ cap, perfil, onSave }: { cap: Capitulo; perfil: PerfilFinanceiro; onSave: (patch: Partial<PerfilFinanceiro>) => void }) {
  const [renda, setRenda] = useState(String(perfil.renda_mensal || ""));
  const [gasto, setGasto] = useState(String(perfil.gasto_mensal_estimado || ""));
  const [dividas, setDividas] = useState(String(perfil.total_dividas || ""));
  const [reserva, setReserva] = useState(String(perfil.reserva_atual || ""));
  const [meses, setMeses] = useState(perfil.meses_reserva_meta || 6);

  const num = (s: string) => parseFloat(s.replace(",", ".")) || 0;

  if (cap.id === "diagnostico") {
    return (
      <div className="mt-4 grid grid-cols-2 gap-3">
        <Campo label="Renda mensal (R$)" value={renda} onChange={setRenda} />
        <Campo label="Gasto mensal (R$)" value={gasto} onChange={setGasto} />
        <button onClick={() => onSave({ renda_mensal: num(renda), gasto_mensal_estimado: num(gasto) })} className="col-span-2 btn-primary">
          Salvar diagnóstico
        </button>
      </div>
    );
  }
  if (cap.id === "dividas") {
    return (
      <div className="mt-4 grid grid-cols-2 gap-3">
        <Campo label="Total de dívidas (R$)" value={dividas} onChange={setDividas} />
        <div className="flex items-end">
          <button onClick={() => onSave({ total_dividas: num(dividas) })} className="btn-primary w-full">
            Atualizar
          </button>
        </div>
        <p className="col-span-2 text-xs text-slate-500">Atualize até zerar. Quando chegar a R$ 0, este capítulo é concluído.</p>
      </div>
    );
  }
  // reserva
  return (
    <div className="mt-4 grid grid-cols-2 gap-3">
      <Campo label="Reserva atual (R$)" value={reserva} onChange={setReserva} />
      <div>
        <label className="mb-1 block text-xs text-slate-400">Meses de meta</label>
        <input
          type="number"
          min={1}
          max={24}
          value={meses}
          onChange={(e) => setMeses(Number(e.target.value))}
          className="w-full rounded-lg border border-white/10 bg-ink-900/60 px-3 py-2 text-sm text-white focus:border-brand/50 focus:outline-none"
        />
      </div>
      <button onClick={() => onSave({ reserva_atual: num(reserva), meses_reserva_meta: meses })} className="col-span-2 btn-primary">
        Atualizar reserva
      </button>
    </div>
  );
}

function Campo({ label, value, onChange }: { label: string; value: string; onChange: (v: string) => void }) {
  return (
    <div>
      <label className="mb-1 block text-xs text-slate-400">{label}</label>
      <input
        value={value}
        onChange={(e) => onChange(e.target.value)}
        inputMode="decimal"
        placeholder="0,00"
        className="w-full rounded-lg border border-white/10 bg-ink-900/60 px-3 py-2 text-sm text-white focus:border-brand/50 focus:outline-none"
      />
    </div>
  );
}

/* ===== Card de capítulo ===== */
function CapituloCard({
  cap,
  perfil,
  onQuiz,
  onSavePerfil,
  onConcluir,
}: {
  cap: Capitulo;
  perfil: PerfilFinanceiro | null;
  onQuiz: () => void;
  onSavePerfil: (patch: Partial<PerfilFinanceiro>) => void;
  onConcluir: (id: string) => void;
}) {
  const Icon = ICONS[cap.icone] ?? Compass;
  const locked = cap.status === "locked";
  const done = cap.status === "done";
  const reserva = cap.metrica as { meta_reserva?: number; reserva_atual?: number; progresso_pct?: number } | undefined;

  return (
    <div
      className={`relative rounded-2xl border p-5 transition-all ${
        done
          ? "border-emerald-500/30 bg-emerald-500/[0.04]"
          : cap.status === "active"
            ? "border-brand/40 bg-brand/[0.06] shadow-glow"
            : "border-white/10 bg-white/[0.02] opacity-60"
      }`}
    >
      <div className="flex items-start gap-4">
        <div
          className={`flex h-11 w-11 shrink-0 items-center justify-center rounded-xl ${
            done ? "bg-emerald-500/20 text-emerald-400" : locked ? "bg-white/5 text-slate-500" : "bg-brand/20 text-brand"
          }`}
        >
          {done ? <Check size={20} /> : locked ? <Lock size={18} /> : <Icon size={20} />}
        </div>
        <div className="flex-1">
          <div className="flex items-center gap-2">
            <h3 className="font-display text-lg font-semibold text-white">{cap.titulo}</h3>
            {done && <span className="rounded-md bg-emerald-500/15 px-2 py-0.5 text-[10px] font-semibold text-emerald-400">CONCLUÍDO</span>}
          </div>
          <p className="mt-0.5 text-sm text-slate-400">{cap.subtitulo}</p>

          {!locked && (
            <>
              <p className="mt-3 text-sm text-slate-300">{renderInline(cap.resumo)}</p>

              {/* Barra de progresso da reserva */}
              {cap.id === "reserva" && reserva?.meta_reserva ? (
                <div className="mt-3">
                  <div className="h-2 w-full overflow-hidden rounded-full bg-white/10">
                    <div className="h-full rounded-full bg-gradient-to-r from-brand to-accent-cyan" style={{ width: `${reserva.progresso_pct ?? 0}%` }} />
                  </div>
                  <p className="mt-1 text-xs text-slate-500">
                    {brl(reserva.reserva_atual ?? 0)} de {brl(reserva.meta_reserva)}
                  </p>
                </div>
              ) : null}

              {cap.passos && (
                <ul className="mt-3 space-y-1.5">
                  {cap.passos.map((s, i) => (
                    <li key={i} className="flex items-start gap-2 text-sm text-slate-400">
                      <span className="mt-0.5 text-brand">›</span>
                      {s}
                    </li>
                  ))}
                </ul>
              )}

              {/* Ações por tipo */}
              {!done && cap.tipo === "quiz" && (
                <button onClick={onQuiz} className="btn-primary mt-4">
                  Responder quiz
                </button>
              )}
              {cap.tipo === "form" && perfil && <FormCapitulo cap={cap} perfil={perfil} onSave={onSavePerfil} />}
              {!done && cap.tipo === "leitura" && (
                <button onClick={() => onConcluir(cap.id)} className="btn-primary mt-4">
                  Marcar como concluído
                </button>
              )}
            </>
          )}
          {locked && <p className="mt-3 text-sm text-slate-500">Conclua os passos anteriores para desbloquear.</p>}
        </div>
      </div>
    </div>
  );
}

export default function Jornada() {
  const [trilha, setTrilha] = useState<Trilha | null>(null);
  const [perfil, setPerfil] = useState<PerfilFinanceiro | null>(null);
  const [quizAberto, setQuizAberto] = useState(false);

  const carregar = () => {
    api.get<Trilha>("/jornada").then((r) => setTrilha(r.data));
    api.get<PerfilFinanceiro>("/financas/perfil").then((r) => setPerfil(r.data));
  };

  useEffect(carregar, []);

  const salvarPerfil = async (patch: Partial<PerfilFinanceiro>) => {
    await api.patch("/financas/perfil", patch);
    carregar();
  };
  const concluir = async (id: string) => {
    await api.post(`/jornada/capitulos/${id}/concluir`);
    carregar();
  };

  return (
    <div>
      <PageHeader
        eyebrow="Aprenda a Investir e Ter Liberdade Financeira"
        title="Sua jornada personalizada"
        description="Um passo a passo do zero à liberdade financeira: quite dívidas, monte sua reserva e comece a investir — no seu ritmo, desbloqueando cada etapa."
      />

      {trilha && (
        <GlassCard className="mb-6">
          <div className="flex flex-wrap items-center justify-between gap-4">
            <div>
              <p className="text-sm text-slate-400">Seu progresso</p>
              <p className="font-display text-2xl font-bold text-white">
                {trilha.capitulos_concluidos} de {trilha.capitulos_total} etapas
              </p>
            </div>
            {trilha.perfil_investidor && (
              <div className="rounded-xl border border-brand/30 bg-brand/10 px-4 py-2 text-center">
                <p className="text-[10px] uppercase tracking-wider text-brand">Perfil</p>
                <p className="font-semibold text-white">{trilha.perfil_investidor}</p>
              </div>
            )}
          </div>
          <div className="mt-4 h-2.5 w-full overflow-hidden rounded-full bg-white/10">
            <div className="h-full rounded-full bg-gradient-to-r from-brand to-accent-cyan transition-all" style={{ width: `${trilha.progresso_pct}%` }} />
          </div>
        </GlassCard>
      )}

      {quizAberto ? (
        <GlassCard title="Descubra seu perfil de investidor">
          <Quiz
            onDone={() => {
              setQuizAberto(false);
              carregar();
            }}
          />
        </GlassCard>
      ) : (
        <div className="space-y-3">
          {trilha?.capitulos.map((cap) => (
            <CapituloCard
              key={cap.id}
              cap={cap}
              perfil={perfil}
              onQuiz={() => setQuizAberto(true)}
              onSavePerfil={salvarPerfil}
              onConcluir={concluir}
            />
          ))}
        </div>
      )}
    </div>
  );
}
