import streamlit as st
import sqlite3
import pandas as pd
import matplotlib.pyplot as plt

st.set_page_config(page_title="Dashboard Financeiro", layout="wide")
st.title("📊 Seu Dashboard Financeiro")

# Obter user_id da URL
query_params = st.query_params
user_id = query_params.get("user_id", [None])[0]

if not user_id:
    st.error("🔐 Acesso negado: nenhum usuário identificado na URL.")
    st.stop()

try:
    user_id = int(user_id)
except ValueError:
    st.error("❌ user_id inválido.")
    st.stop()

# Conectar ao banco de dados
DB_PATH = "data/finance.db"
conn = sqlite3.connect(DB_PATH)
df = pd.read_sql_query("SELECT * FROM transacoes WHERE user_id = ?", conn, params=(user_id,))
conn.close()

if df.empty:
    st.info("📭 Nenhuma transação encontrada para este usuário.")
    st.stop()

# Processar dados
df["data"] = pd.to_datetime(df["data"])
df["mês"] = df["data"].dt.to_period("M").astype(str)

# Resumo financeiro
receita_total = df[df["tipo"] == "receita"]["valor"].sum()
gasto_total = df[df["tipo"] == "gasto"]["valor"].sum()
saldo = receita_total - gasto_total

col1, col2, col3 = st.columns(3)
col1.metric("💰 Total de Receitas", f"R$ {receita_total:.2f}")
col2.metric("💸 Total de Gastos", f"R$ {gasto_total:.2f}")
col3.metric("📊 Saldo", f"R$ {saldo:.2f}")

st.divider()

# Gráfico de pizza por categoria
st.subheader("📂 Distribuição de gastos por categoria")
df_gastos = df[df["tipo"] == "gasto"]
gastos_categoria = df_gastos.groupby("categoria")["valor"].sum()

fig1, ax1 = plt.subplots()
ax1.pie(gastos_categoria, labels=gastos_categoria.index, autopct="%1.1f%%", startangle=90)
ax1.axis("equal")
st.pyplot(fig1)

# Gráfico de linha por mês
st.subheader("📈 Evolução mensal")
df_mes = df.groupby(["mês", "tipo"])["valor"].sum().reset_index()
pivot = df_mes.pivot(index="mês", columns="tipo", values="valor").fillna(0)

st.line_chart(pivot)
