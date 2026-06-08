import json

from sqlalchemy.orm import Session

from app.models import PerfilFinanceiro
from app.services.financas import gasto_medio_mensal

# ===== Quiz de perfil de investidor (10 perguntas, alternativas com peso 0..3) =====
QUIZ = [
    {
        "pergunta": "Qual é o seu principal objetivo ao investir?",
        "opcoes": [
            "Preservar meu dinheiro, sem perdas",
            "Crescer um pouco acima da poupança",
            "Crescer de forma consistente no longo prazo",
            "Maximizar ganhos, aceitando grandes oscilações",
        ],
    },
    {
        "pergunta": "Se sua carteira caísse 20% em um mês, o que você faria?",
        "opcoes": [
            "Venderia tudo imediatamente",
            "Venderia uma parte, com medo",
            "Manteria e esperaria recuperar",
            "Compraria mais, aproveitando a queda",
        ],
    },
    {
        "pergunta": "Por quanto tempo pretende deixar o dinheiro investido?",
        "opcoes": ["Menos de 1 ano", "1 a 3 anos", "3 a 10 anos", "Mais de 10 anos"],
    },
    {
        "pergunta": "Qual sua experiência com investimentos?",
        "opcoes": [
            "Nenhuma, só poupança",
            "Conheço renda fixa básica",
            "Já invisto em ações/FIIs",
            "Invisto em diversos ativos e derivativos",
        ],
    },
    {
        "pergunta": "Quanto da sua renda sobra todo mês?",
        "opcoes": ["Nada ou fico no negativo", "Até 10%", "Entre 10% e 30%", "Mais de 30%"],
    },
    {
        "pergunta": "Como você reage a notícias econômicas negativas?",
        "opcoes": [
            "Fico muito ansioso e mexo na carteira",
            "Fico preocupado, mas espero",
            "Acompanho com calma",
            "Vejo como oportunidade",
        ],
    },
    {
        "pergunta": "Qual retorno anual você considera satisfatório?",
        "opcoes": ["O da poupança já está bom", "Um pouco acima do CDI", "Bem acima do CDI", "O máximo possível"],
    },
    {
        "pergunta": "Você já tem reserva de emergência?",
        "opcoes": ["Não tenho nada", "Tenho menos de 3 meses", "Tenho de 3 a 6 meses", "Tenho mais de 6 meses"],
    },
    {
        "pergunta": "Qual frase combina mais com você?",
        "opcoes": [
            "Não durmo se posso perder dinheiro",
            "Aceito risco pequeno por um retorno melhor",
            "Aceito oscilações pensando no longo prazo",
            "Risco alto não me incomoda",
        ],
    },
    {
        "pergunta": "Se recebesse um bônus inesperado, você...",
        "opcoes": [
            "Deixaria tudo na conta/poupança",
            "Colocaria em renda fixa segura",
            "Dividiria entre renda fixa e variável",
            "Investiria a maior parte em renda variável",
        ],
    },
]


def avaliar_perfil(respostas: list[int]) -> tuple[str, int]:
    score = sum(max(0, min(3, r)) for r in respostas)  # 0..30
    if score <= 12:
        perfil = "Conservador"
    elif score <= 22:
        perfil = "Moderado"
    else:
        perfil = "Arrojado"
    return perfil, score


def _carregar_concluidos(perfil: PerfilFinanceiro) -> set[str]:
    if not perfil.capitulos_concluidos:
        return set()
    try:
        return set(json.loads(perfil.capitulos_concluidos))
    except (ValueError, TypeError):
        return set()


def salvar_concluidos(perfil: PerfilFinanceiro, ids: set[str]) -> None:
    perfil.capitulos_concluidos = json.dumps(sorted(ids))


ALOCACAO_SUGERIDA = {
    "Conservador": {"Renda Fixa": 80, "FIIs": 10, "Ações": 10},
    "Moderado": {"Renda Fixa": 50, "FIIs": 25, "Ações": 25},
    "Arrojado": {"Renda Fixa": 25, "FIIs": 30, "Ações": 45},
}


def construir_trilha(db: Session, perfil: PerfilFinanceiro) -> dict:
    """Monta a trilha personalizada com status (done/active/locked) por capítulo."""
    concluidos = _carregar_concluidos(perfil)

    renda = float(perfil.renda_mensal or 0)
    gasto_base = float(perfil.gasto_mensal_estimado or 0) or gasto_medio_mensal(db)
    dividas = float(perfil.total_dividas or 0)
    reserva_atual = float(perfil.reserva_atual or 0)
    meses_meta = int(perfil.meses_reserva_meta or 6)
    meta_reserva = round(gasto_base * meses_meta, 2)
    sobra_mensal = round(renda - gasto_base, 2)
    perfil_inv = perfil.perfil_investidor or "Moderado"

    # Condições de conclusão "data-driven"
    perfil_ok = perfil.perfil_investidor is not None
    diag_ok = renda > 0 and gasto_base > 0
    dividas_ok = diag_ok and dividas <= 0
    reserva_ok = meta_reserva > 0 and reserva_atual >= meta_reserva

    capitulos = []

    # 1. Perfil de investidor
    capitulos.append(
        {
            "id": "perfil",
            "titulo": "Descubra seu perfil de investidor",
            "subtitulo": "10 perguntas rápidas para personalizar toda a sua jornada.",
            "icone": "compass",
            "tipo": "quiz",
            "done": perfil_ok,
            "resumo": (
                f"Seu perfil é **{perfil_inv}**. Vamos adaptar as recomendações a você."
                if perfil_ok
                else "Responda o quiz para liberarmos os próximos passos."
            ),
        }
    )

    # 2. Diagnóstico financeiro
    capitulos.append(
        {
            "id": "diagnostico",
            "titulo": "Diagnóstico financeiro",
            "subtitulo": "Informe sua renda e seus gastos para sabermos seu ponto de partida.",
            "icone": "clipboard",
            "tipo": "form",
            "done": diag_ok,
            "metrica": {
                "renda_mensal": renda,
                "gasto_mensal": gasto_base,
                "sobra_mensal": sobra_mensal,
            },
            "resumo": (
                f"Você ganha {renda:.0f} e gasta cerca de {gasto_base:.0f} por mês — "
                + ("sobra **R$ {:.0f}**.".format(sobra_mensal) if sobra_mensal > 0 else "**atenção: você está no vermelho.**")
                if diag_ok
                else "Preencha renda e gastos no Organizador Financeiro ou aqui mesmo."
            ),
            "passos": [
                "Lance suas receitas e despesas no Organizador Financeiro.",
                "Some quanto entra e quanto sai por mês.",
                "O objetivo é fazer a sobra mensal ser positiva.",
            ],
        }
    )

    # 3. Quitar dívidas
    cap_dividas = {
        "id": "dividas",
        "titulo": "Quite suas dívidas caras",
        "subtitulo": "Antes de investir, elimine juros que corroem seu patrimônio.",
        "icone": "flame",
        "tipo": "form",
        "done": dividas_ok,
        "metrica": {"total_dividas": dividas, "sobra_mensal": sobra_mensal},
        "passos": [
            "Liste todas as dívidas com seus juros mensais.",
            "Priorize as de juros mais altos (cartão, cheque especial) — método avalanche.",
            "Negocie e, se possível, troque dívida cara por uma mais barata.",
            f"Direcione a sobra mensal de R$ {max(sobra_mensal, 0):.0f} para abater o saldo.",
        ],
    }
    if dividas > 0:
        cap_dividas["resumo"] = (
            f"Você tem **R$ {dividas:.0f}** em dívidas. Foque em quitar as de juros mais altos primeiro."
        )
    elif diag_ok:
        cap_dividas["resumo"] = "Sem dívidas caras — excelente! Você está pronto para a reserva."
    else:
        cap_dividas["resumo"] = "Conclua o diagnóstico para avaliarmos suas dívidas."
    capitulos.append(cap_dividas)

    # 4. Reserva de emergência (6 meses por padrão)
    progresso_reserva = round((reserva_atual / meta_reserva * 100), 1) if meta_reserva > 0 else 0.0
    capitulos.append(
        {
            "id": "reserva",
            "titulo": "Monte sua reserva de emergência",
            "subtitulo": f"O alvo é {meses_meta} meses dos seus gastos, em liquidez diária.",
            "icone": "shield",
            "tipo": "form",
            "done": reserva_ok,
            "metrica": {
                "meta_reserva": meta_reserva,
                "reserva_atual": reserva_atual,
                "progresso_pct": min(progresso_reserva, 100),
                "meses_meta": meses_meta,
            },
            "resumo": (
                f"Sua meta é **R$ {meta_reserva:.0f}** ({meses_meta} meses). "
                + (
                    f"Você já tem R$ {reserva_atual:.0f} ({min(progresso_reserva, 100):.0f}%)."
                    if meta_reserva > 0
                    else "Conclua o diagnóstico para calcularmos a meta."
                )
            ),
            "passos": [
                "Guarde em Tesouro Selic ou CDB de liquidez diária (100%+ do CDI).",
                "Nunca invista a reserva em renda variável.",
                f"Aporte mensalmente até atingir R$ {meta_reserva:.0f}.",
            ],
        }
    )

    # 5. Comece a investir (depende do perfil)
    aloc = ALOCACAO_SUGERIDA.get(perfil_inv, ALOCACAO_SUGERIDA["Moderado"])
    capitulos.append(
        {
            "id": "comecar_investir",
            "titulo": "Comece a investir com estratégia",
            "subtitulo": "Sua primeira carteira, alinhada ao seu perfil.",
            "icone": "rocket",
            "tipo": "leitura",
            "done": "comecar_investir" in concluidos,
            "metrica": {"alocacao_sugerida": aloc, "perfil": perfil_inv},
            "resumo": f"Como **{perfil_inv}**, uma alocação inicial equilibrada seria: "
            + ", ".join(f"{k} {v}%" for k, v in aloc.items())
            + ".",
            "passos": [
                "Abra conta em uma corretora sem taxas.",
                "Comece pela renda fixa que entende.",
                "Adicione FIIs e ações boas pagadoras aos poucos.",
                "Use a aba Valuation para escolher bons preços de entrada.",
            ],
        }
    )

    # 6. Diversificação e consistência
    capitulos.append(
        {
            "id": "consistencia",
            "titulo": "Consistência e longo prazo",
            "subtitulo": "O segredo dos juros compostos é o tempo e a regularidade.",
            "icone": "infinity",
            "tipo": "leitura",
            "done": "consistencia" in concluidos,
            "resumo": "Aporte todo mês, reinvista os proventos e revise a carteira a cada trimestre.",
            "passos": [
                "Automatize aportes mensais (pague-se primeiro).",
                "Reinvista dividendos e juros — use a aba Juros Compostos para simular.",
                "Rebalanceie a carteira 1x por trimestre.",
                "Ignore o ruído de curto prazo: foco no plano.",
            ],
        }
    )

    # Define status (gradual): primeiro não-concluído vira "active", resto "locked".
    achou_ativo = False
    for cap in capitulos:
        if cap["done"]:
            cap["status"] = "done"
        elif not achou_ativo:
            cap["status"] = "active"
            achou_ativo = True
        else:
            cap["status"] = "locked"

    total = len(capitulos)
    feitos = sum(1 for c in capitulos if c["done"])
    return {
        "perfil_investidor": perfil.perfil_investidor,
        "progresso_pct": round(feitos / total * 100),
        "capitulos_total": total,
        "capitulos_concluidos": feitos,
        "capitulos": capitulos,
    }
