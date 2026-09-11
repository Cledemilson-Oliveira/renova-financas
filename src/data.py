from __future__ import annotations

from datetime import date, timedelta

import pandas as pd


CATEGORIES = [
    "Moradia",
    "Alimentação",
    "Transporte",
    "Saúde",
    "Educação",
    "Família",
    "Lazer",
    "Assinaturas",
    "Vendas",
    "Serviços",
    "Outros",
]


def demo_transactions() -> pd.DataFrame:
    today = date.today()
    rows = [
        (today - timedelta(days=1), "Receita", "Serviços", "Gestão de tráfego", 399.00, "Conta RENOVA"),
        (today - timedelta(days=2), "Despesa", "Alimentação", "Mercado", 186.40, "Carteira"),
        (today - timedelta(days=3), "Despesa", "Moradia", "Energia", 160.00, "Conta principal"),
        (today - timedelta(days=4), "Receita", "Vendas", "Plano RENOVA", 599.00, "Conta RENOVA"),
        (today - timedelta(days=5), "Despesa", "Transporte", "Deslocamento", 48.00, "Carteira"),
        (today - timedelta(days=7), "Despesa", "Assinaturas", "Ferramentas digitais", 89.90, "Conta RENOVA"),
        (today - timedelta(days=9), "Receita", "Serviços", "Freelance", 300.00, "Conta principal"),
        (today - timedelta(days=11), "Despesa", "Família", "Compras da casa", 220.00, "Conta principal"),
    ]
    return pd.DataFrame(rows, columns=["data", "tipo", "categoria", "descricao", "valor", "conta"])


def demo_accounts() -> pd.DataFrame:
    return pd.DataFrame(
        [
            ("Conta principal", "Conta corrente", 1220.00),
            ("Conta RENOVA", "Conta digital", 1847.10),
            ("Carteira", "Dinheiro", 120.00),
        ],
        columns=["conta", "tipo", "saldo"],
    )


def demo_cards() -> pd.DataFrame:
    return pd.DataFrame(
        [
            ("Cartão principal", 1200.00, 386.40, 10, 17),
            ("Cartão digital", 800.00, 189.90, 12, 20),
        ],
        columns=["cartao", "limite", "fatura", "fechamento", "vencimento"],
    )


def demo_budgets() -> pd.DataFrame:
    return pd.DataFrame(
        [
            ("Moradia", 900.00, 630.00),
            ("Alimentação", 700.00, 486.40),
            ("Transporte", 250.00, 148.00),
            ("Família", 900.00, 620.00),
            ("Assinaturas", 250.00, 189.90),
        ],
        columns=["categoria", "orcamento", "realizado"],
    )


def financial_summary(transactions: pd.DataFrame, accounts: pd.DataFrame) -> dict:
    income = transactions.loc[transactions["tipo"] == "Receita", "valor"].sum()
    expense = transactions.loc[transactions["tipo"] == "Despesa", "valor"].sum()
    balance = float(accounts["saldo"].sum())
    result = float(income - expense)
    savings_rate = (result / income * 100) if income else 0.0
    return {
        "receitas": float(income),
        "despesas": float(expense),
        "resultado": result,
        "saldo": balance,
        "taxa_economia": float(savings_rate),
    }


def brl(value: float) -> str:
    text = f"{value:,.2f}"
    return "R$ " + text.replace(",", "X").replace(".", ",").replace("X", ".")
