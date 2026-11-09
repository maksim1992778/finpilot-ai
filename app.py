
import streamlit as st
import pandas as pd
import numpy as np

st.set_page_config(
    page_title="ДеньгиПодКонтролем AI",
    page_icon="💰",
    layout="wide"
)

# ===== FinPilot Design System v0.6 =====

if "theme" not in st.session_state:
    st.session_state.theme = "Светлая"

theme = st.sidebar.radio(
    "🎨 Тема оформления",
    ["Светлая", "Тёмная"],
    index=0 if st.session_state.theme == "Светлая" else 1
)

st.session_state.theme = theme

if theme == "Тёмная":
    bg = "#0B1020"
    surface = "#151D30"
    text = "#F4F7FC"
    muted = "#9AA8C0"
    border = "#29354C"
    sidebar = "#10182A"
else:
    bg = "#F5F7FC"
    surface = "#FFFFFF"
    text = "#18243A"
    muted = "#68788F"
    border = "#E4EAF3"
    sidebar = "#EAF0FA"

st.markdown(
    f"""
    <style>
    .stApp {{
        background: {bg};
        color: {text};
    }}

    [data-testid="stSidebar"] {{
        background: {sidebar};
    }}

    h1, h2, h3 {{
        color: {text} !important;
        letter-spacing: -0.035em;
        font-weight: 700;
    }}

    [data-testid="stMetric"] {{
        background: {surface};
        border: 1px solid {border};
        border-radius: 18px;
        padding: 20px;
        box-shadow: 0 6px 24px rgba(0,0,0,0.04);
    }}

    [data-testid="stMetricLabel"] {{
        color: {muted};
    }}

    [data-testid="stMetricValue"] {{
        color: {text};
    }}

    div.stButton > button[kind="primary"] {{
        background: linear-gradient(
            135deg, #476BFF, #8055F5
        );
        border: none;
        border-radius: 12px;
        color: white;
        font-weight: 600;
    }}

    [data-testid="stDataFrame"] {{
        border-radius: 14px;
        overflow: hidden;
    }}

    [data-testid="stVerticalBlock"] {{
        gap: 0.85rem;
    }}

    </style>
    """,
    unsafe_allow_html=True
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
if "Дата" not in payments_df.columns:
    payments_df = pd.DataFrame(
        columns=["Дата", "Описание", "Тип", "Сумма"]
    )

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


# ===== Экспорт платежного календаря =====
import io

# ===== Импорт платежного календаря v0.5 =====
st.subheader("📤 Восстановление календаря")

import_file = st.file_uploader(
    "Выберите сохранённый календарь Excel",
    type=["xlsx"],
    key="payments_import"
)

if import_file is not None:
    try:
        imported = pd.read_excel(import_file)

        required = ["Дата", "Описание", "Тип", "Сумма"]

        if list(imported.columns) != required:
            st.error(
                "Неверный формат. Нужны столбцы: "
                "Дата, Описание, Тип, Сумма."
            )
        else:
            imported["Дата"] = pd.to_datetime(
                imported["Дата"], errors="coerce"
            ).dt.date

            imported["Сумма"] = pd.to_numeric(
                imported["Сумма"], errors="coerce"
            )

            valid = (
                imported["Дата"].notna().all()
                and imported["Описание"].notna().all()
                and imported["Описание"].astype(str).str.strip().ne("").all()
                and imported["Тип"].isin(
                    ["Расход", "Поступление"]
                ).all()
                and imported["Сумма"].notna().all()
                and imported["Сумма"].gt(0).all()
            )

            if not valid:
                st.error(
                    "В файле есть некорректные даты, "
                    "типы операций или суммы."
                )
            else:
                st.info(
                    f"Найдено операций: {len(imported)}. "
                    "При восстановлении текущий календарь "
                    "будет заменён."
                )

                if st.button("✅ Восстановить календарь"):
                    st.session_state.payments = (
                        imported.to_dict(orient="records")
                    )
                    st.success("Календарь восстановлен.")
                    st.rerun()

    except Exception as e:
        st.error(f"Ошибка загрузки Excel: {e}")

st.subheader("📥 Сохранение календаря")

export_df = pd.DataFrame(
    st.session_state.payments,
    columns=["Дата", "Описание", "Тип", "Сумма"]
)

output = io.BytesIO()

with pd.ExcelWriter(
    output,
    engine="openpyxl"
) as writer:
    export_df.to_excel(
        writer,
        index=False,
        sheet_name="Платежи"
    )

st.download_button(
    label="📥 Скачать календарь Excel",
    data=output.getvalue(),
    file_name="finpilot_payments.xlsx",
    mime=(
        "application/vnd.openxmlformats-officedocument."
        "spreadsheetml.sheet"
    )
)

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
