"""Importador de extratos da B3 / corretoras (XLSX/PDF).

Estratégia pessoal: o usuário faz upload do arquivo da "Área do Investidor da
B3" ou extrato da corretora; o parser limpa e injeta na tabela `transacoes`.

TODO: implementar parsing de XLSX (openpyxl/pandas) e PDF.
"""

from __future__ import annotations


def parse_extrato_xlsx(conteudo: bytes) -> list[dict]:
    raise NotImplementedError("Parser de extrato XLSX ainda não implementado.")


def parse_extrato_pdf(conteudo: bytes) -> list[dict]:
    raise NotImplementedError("Parser de extrato PDF ainda não implementado.")
