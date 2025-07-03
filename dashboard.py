
import streamlit as st
from sqlalchemy import create_engine, text
import pandas as pd
from dotenv import load_dotenv
import os

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_engine(DATABASE_URL)

st.set_page_config(page_title="Dashboard Financeiro", page_icon="📊", layout="centered")

st.title("📊 Seu Dashboard Financeiro")

query_params = st.query_params
user_id = query_params.get("user_id")

if not user_id:
    st.error("🚫 Acesso negado: nenhum usuário identificado na URL.")
    st.stop()

st.success(f"Usuário identificado: {user_id}")

with engine.connect() as conn:
    result = conn.execute(text("""
        SELECT data, tipo, valor, categoria
        FROM transacoes
        WHERE user_id = :user_id
        ORDER BY data DESC
    """), {"user_id": user_id})
    rows = result.fetchall()

if not rows:
    st.warning("📭 Nenhuma transação encontrada para este usuário.")
    st.stop()

df = pd.DataFrame(rows, columns=["Data", "Tipo", "Valor", "Categoria"])
df["Data"] = pd.to_datetime(df["Data"])
df = df.sort_values(by="Data", ascending=False)

st.subheader("📌 Últimas transações")
st.dataframe(df, use_container_width=True)

st.subheader("💰 Resumo por tipo")
resumo_tipo = df.groupby("Tipo")["Valor"].sum().reset_index()
st.bar_chart(resumo_tipo.set_index("Tipo"))

st.subheader("📂 Gastos por categoria")
gastos = df[df["Tipo"] == "gasto"]
if not gastos.empty:
    cat = gastos.groupby("Categoria")["Valor"].sum().reset_index()
    st.bar_chart(cat.set_index("Categoria"))
