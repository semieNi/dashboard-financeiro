import streamlit as st
from sqlalchemy import create_engine, text
import pandas as pd
from dotenv import load_dotenv
import os

# Carrega variáveis do .env
load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_engine(DATABASE_URL)

st.set_page_config(page_title="Dashboard Financeiro", page_icon="📊", layout="centered")
st.title(":bar_chart: Dashboard Financeiro")

# Lê user_id da URL
user_id = st.query_params.get("user_id")

if user_id is None:
    st.error("🚫 Nenhum user_id foi passado na URL.")
    st.stop()

try:
    user_id = int(user_id)
except ValueError:
    st.error("❌ user_id inválido.")
    st.stop()

st.success(f"🔑 Usuário identificado: {user_id}")

# Diagnóstico (opcional): mostrar user_ids com dados no banco
with engine.connect() as conn:
    debug_result = conn.execute(text("SELECT DISTINCT user_id FROM transacoes"))
    debug_ids = [str(r[0]) for r in debug_result.fetchall()]
    st.info(f"🧪 IDs com transações no banco: {debug_ids}")

# Busca transações no PostgreSQL
with engine.connect() as conn:
    result = conn.execute(text("""
        SELECT data, tipo, valor, categoria
        FROM transacoes
        WHERE user_id = :user_id
        ORDER BY data DESC
    """), {"user_id": user_id})
    rows = result.fetchall()

if not rows:
    st.warning(":mailbox: Nenhuma transação encontrada para este usuário.")
    st.stop()

# Cria DataFrame
df = pd.DataFrame(rows, columns=["Data", "Tipo", "Valor", "Categoria"])
df["Data"] = pd.to_datetime(df["Data"])
df = df.sort_values(by="Data", ascending=False)

# Exibe tabela
st.subheader(":pushpin: Últimas transações")
st.dataframe(df, use_container_width=True)

# Gráfico por tipo (gasto/receita)
st.subheader(":moneybag: Resumo por tipo")
resumo_tipo = df.groupby("Tipo")["Valor"].sum().reset_index()
st.bar_chart(resumo_tipo.set_index("Tipo"))

# Gráfico por categoria (gastos)
st.subheader(":file_folder: Gastos por categoria")
gastos = df[df["Tipo"] == "gasto"]
if not gastos.empty:
    cat = gastos.groupby("Categoria")["Valor"].sum().reset_index()
    st.bar_chart(cat.set_index("Categoria"))
