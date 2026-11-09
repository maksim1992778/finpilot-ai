
import streamlit as st
import pandas as pd
import numpy as np

st.set_page_config(
    page_title="ДеньгиПодКонтролем AI",
    page_icon="💰",
    layout="wide"
)

st.title("💰 ДеньгиПодКонтролем AI")
st.caption("Финансовый аналитик для бизнеса | MVP 0.1")

@st.cache_data
def demo_data():
    rng = np.random.default_rng(42)
    dates = pd.date_range(end=pd.Timestamp.today(), periods=90)
    rows = []
    for date in dates:
        rows.append({
            "Дата": date,
            "Категория": "Продажи",
            "Сумма": int(rng.integers(15000, 65000))
        })
        rows.append({
            "Дата": date,
            "Категория": "Поставщики",
            "Сумма": -int(rng.integers(8000, 42000))
        })
        if date.day in (5, 20):
            rows.append({
                "Дата": date,
                "Категория": "Зарплата",
                "Сумма": -65000
            })
    return pd.DataFrame(rows)

uploaded = st.file_uploader(
    "Загрузите CSV или Excel",
    type=["csv", "xlsx"]
)

if uploaded is not None:
    try:
        if uploaded.name.endswith(".csv"):
            df = pd.read_csv(uploaded)
        else:
            df = pd.read_excel(uploaded)

        required = {"Дата", "Категория", "Сумма"}
        if not required.issubset(df.columns):
            st.error("Нужны столбцы: Дата, Категория, Сумма")
            st.stop()

        df["Дата"] = pd.to_datetime(df["Дата"], errors="coerce")
        df["Сумма"] = pd.to_numeric(df["Сумма"], errors="coerce")
        df = df.dropna(subset=["Дата", "Сумма"])
    except Exception as e:
        st.error(f"Ошибка чтения файла: {e}")
        st.stop()
else:
    df = demo_data()
    st.info("Сейчас используются демонстрационные данные.")

income = df.loc[df["Сумма"] > 0, "Сумма"].sum()
expenses = -df.loc[df["Сумма"] < 0, "Сумма"].sum()
net = income - expenses

a, b, c = st.columns(3)
a.metric("Поступления", f"{income:,.0f} ₽")
b.metric("Расходы", f"{expenses:,.0f} ₽")
c.metric("Денежный поток", f"{net:,.0f} ₽")

st.subheader("Денежный поток")
daily = df.groupby("Дата")["Сумма"].sum().sort_index()
st.line_chart(daily.cumsum())

st.subheader("Расходы по категориям")
expense_df = df[df["Сумма"] < 0].copy()
expense_df["Расход"] = -expense_df["Сумма"]
by_category = expense_df.groupby("Категория")["Расход"].sum()
st.bar_chart(by_category)

st.subheader("Прогноз на 30 дней")
opening_balance = st.number_input(
    "Текущий остаток на счетах, ₽",
    min_value=0.0,
    value=500000.0,
    step=10000.0
)

future_income = st.number_input(
    "Ожидаемые поступления за 30 дней, ₽",
    min_value=0.0,
    value=900000.0,
    step=10000.0
)

future_expenses = st.number_input(
    "Плановые платежи за 30 дней, ₽",
    min_value=0.0,
    value=1100000.0,
    step=10000.0
)

reserve = st.number_input(
    "Минимальный резерв, ₽",
    min_value=0.0,
    value=200000.0,
    step=10000.0
)

forecast = opening_balance + future_income - future_expenses

st.metric("Прогнозный остаток через 30 дней", f"{forecast:,.0f} ₽")

if forecast < 0:
    st.error("Прогнозируется отрицательный остаток денежных средств.")
elif forecast < reserve:
    st.warning("Прогнозный остаток ниже заданного резерва.")
else:
    st.success("Прогнозный остаток выше установленного резерва.")

st.subheader("Финансовые рекомендации")
if expenses > income:
    st.warning("Расходы за анализируемый период превышают поступления.")
else:
    st.success("Поступления за анализируемый период покрывают расходы.")

if not by_category.empty:
    top = by_category.idxmax()
    st.write(f"Крупнейшая категория расходов: {top}. Проверьте её структуру.")

st.caption(
    "Прогноз основан на введённых суммах, без календаря платежей. "
    "Он не определяет даты возможных кассовых разрывов. "
    "AI-модуль будет добавлен позднее."
)
