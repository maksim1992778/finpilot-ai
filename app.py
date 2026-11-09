
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

# ===== Календарь платежей v0.2 =====

st.divider()
st.header("📅 Календарь платежей")

from datetime import date, timedelta

today = date.today()

if "payments" not in st.session_state:
    st.session_state.payments = [
        {
            "Дата": today + timedelta(days=5),
            "Описание": "Оплата поставщику",
            "Тип": "Расход",
            "Сумма": 350000.0
        },
        {
            "Дата": today + timedelta(days=12),
            "Описание": "Оплата от покупателя",
            "Тип": "Поступление",
            "Сумма": 600000.0
        },
        {
            "Дата": today + timedelta(days=18),
            "Описание": "Аренда и зарплата",
            "Тип": "Расход",
            "Сумма": 450000.0
        }
    ]

with st.form("add_payment", clear_on_submit=True):
    st.subheader("Добавить операцию")

    payment_date = st.date_input(
        "Дата операции",
        value=today
    )

    description = st.text_input("Описание")
    payment_type = st.selectbox(
        "Тип операции",
        ["Расход", "Поступление"]
    )

    amount = st.number_input(
        "Сумма, ₽",
        min_value=0.01,
        value=10000.0
    )

    submitted = st.form_submit_button(
        "Добавить в календарь"
    )

    if submitted:
        if not description.strip():
            st.error("Введите описание операции.")
        else:
            st.session_state.payments.append({
                "Дата": payment_date,
                "Описание": description.strip(),
                "Тип": payment_type,
                "Сумма": float(amount)
            })
            st.success("Операция добавлена.")


payments_df = pd.DataFrame(st.session_state.payments)

st.subheader("Управление платежами")
st.caption(
    "Изменяйте даты, описания, типы и суммы. "
    "Для удаления отметьте нужную строку."
)

payments_df["Удалить"] = False

edited_df = st.data_editor(
    payments_df,
    use_container_width=True,
    hide_index=True,
    num_rows="fixed",
    column_config={
        "Дата": st.column_config.DateColumn(
            "Дата",
            format="DD.MM.YYYY",
            required=True
        ),
        "Описание": st.column_config.TextColumn(
            "Описание",
            required=True
        ),
        "Тип": st.column_config.SelectboxColumn(
            "Тип",
            options=["Расход", "Поступление"],
            required=True
        ),
        "Сумма": st.column_config.NumberColumn(
            "Сумма, ₽",
            min_value=0.01,
            required=True
        ),
        "Удалить": st.column_config.CheckboxColumn(
            "Удалить"
        )
    },
    key="payment_editor"
)

if st.button("💾 Сохранить изменения"):
    updated = edited_df[
        ~edited_df["Удалить"]
    ].drop(columns=["Удалить"])

    st.session_state.payments = updated.to_dict(
        orient="records"
    )

    st.success("Изменения сохранены.")
    st.rerun()


st.subheader("Прогноз остатка по дням")

calendar = pd.DataFrame({
    "Дата": [
        today + timedelta(days=i)
        for i in range(31)
    ]
})

calendar["Остаток"] = float(opening_balance)

for i in range(1, len(calendar)):
    current_date = calendar.loc[i, "Дата"]

    day_payments = payments_df[
        payments_df["Дата"] == current_date
    ]

    incoming = day_payments.loc[
        day_payments["Тип"] == "Поступление",
        "Сумма"
    ].sum()

    outgoing = day_payments.loc[
        day_payments["Тип"] == "Расход",
        "Сумма"
    ].sum()

    calendar.loc[i, "Остаток"] = (
        calendar.loc[i - 1, "Остаток"]
        + incoming
        - outgoing
    )

st.line_chart(
    calendar.set_index("Дата")["Остаток"]
)

negative_days = calendar[
    calendar["Остаток"] < 0
]

low_reserve_days = calendar[
    calendar["Остаток"] < reserve
]

if not negative_days.empty:
    first_day = negative_days.iloc[0]["Дата"]
    st.error(
        f"Кассовый разрыв: {first_day:%d.%m.%Y}"
    )
elif not low_reserve_days.empty:
    first_day = low_reserve_days.iloc[0]["Дата"]
    st.warning(
        f"Остаток ниже резерва: {first_day:%d.%m.%Y}"
    )
else:
    st.success(
        "По календарю кассовых разрывов не обнаружено."
    )

st.caption(
    "Календарь рассчитывается только по операциям "
    "из таблицы выше. Общие суммы из предыдущего "
    "прогноза автоматически не распределяются по дням."
)
