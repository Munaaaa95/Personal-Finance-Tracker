import streamlit as st
import pandas as pd
import plotly.express as px


# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="FinSight | Personal Finance Analyzer",
    page_icon="◈",
    layout="wide",
    initial_sidebar_state="collapsed"
)


# ============================================================
# CUSTOM CSS
# ============================================================

st.markdown(
    """
    <style>

    /* Main page */

    .main .block-container {
        max-width: 1350px;
        padding: 3rem 4rem 5rem 4rem;
    }

    /* Hero */

    .subtitle {
        color: var(--text-color);
        opacity: 0.65;
        font-size: 1.05rem;
        margin-bottom: 3rem;
    }

    /* Section descriptions */

    .section-description {
        color: var(--text-color);
        opacity: 0.65;
        margin-bottom: 1.5rem;
    }

    /* Metric cards */

    .metric-box {
        background-color: var(--secondary-background-color);
        border: 1px solid rgba(128, 128, 128, 0.2);
        border-radius: 16px;
        padding: 1.4rem;
        min-height: 125px;
    }

    .metric-label {
        color: var(--text-color);
        opacity: 0.6;
        font-size: 0.8rem;
        text-transform: uppercase;
        letter-spacing: 1px;
    }

    .metric-number {
        color: var(--text-color);
        font-size: 1.7rem;
        font-weight: 700;
        margin-top: 0.5rem;
    }

    .positive {
        color: #10b981;
    }

    .negative {
        color: #ef4444;
    }

    /* Insight cards */

    .insight-box {
        background-color: var(--secondary-background-color);
        border: 1px solid rgba(128, 128, 128, 0.2);
        border-radius: 14px;
        padding: 1.2rem 1.4rem;
        margin-bottom: 1rem;
    }

    .insight-title {
        color: var(--text-color);
        font-weight: 700;
        margin-bottom: 0.4rem;
    }

    .insight-description {
        color: var(--text-color);
        opacity: 0.65;
        line-height: 1.6;
    }

    /* Footer */

    .footer {
        text-align: center;
        color: var(--text-color);
        opacity: 0.45;
        margin-top: 5rem;
        padding-top: 2rem;
        border-top: 1px solid rgba(128, 128, 128, 0.2);
    }

    </style>
    """,
    unsafe_allow_html=True
)

# ============================================================
# TRANSACTION CATEGORIZATION
# ============================================================

def categorize_transaction(description):

    description = str(description).lower()

    categories = {
        "Transport": [
            "uber",
            "bolt",
            "taxi",
            "bus",
            "transport",
            "fuel",
            "petrol"
        ],

        "Food": [
            "chicken republic",
            "kfc",
            "restaurant",
            "food",
            "shoprite",
            "groceries",
            "market"
        ],

        "Entertainment": [
            "netflix",
            "spotify",
            "cinema",
            "movie",
            "game"
        ],

        "Utilities": [
            "mtn",
            "airtel",
            "glo",
            "9mobile",
            "data",
            "electricity",
            "ekedc",
            "water"
        ],

        "Shopping": [
            "amazon",
            "zara",
            "clothing",
            "jumia",
            "shop"
        ]
    }

    for category, keywords in categories.items():

        for keyword in keywords:

            if keyword in description:
                return category

    return "Other"


# ============================================================
# HEADER
# ============================================================

st.caption("PERSONAL FINANCE ANALYTICS")

st.title("FinSight")

st.markdown(
    '<p class="subtitle">'
    'Understand where your money goes, identify spending patterns, '
    'and turn transaction data into useful financial insights.'
    '</p>',
    unsafe_allow_html=True
)


# ============================================================
# DATA SECTION
# ============================================================

st.header("Data")

st.markdown(
    '<p class="section-description">'
    'Upload your transaction history or use the sample data to explore the dashboard.'
    '</p>',
    unsafe_allow_html=True
)

with st.expander("Upload & Filter Data"):

    uploaded_file = st.file_uploader(
        "Upload your transaction CSV",
        type=["csv"]
    )

    st.caption(
        "Required columns: date, description, amount, type"
    )


# ============================================================
# LOAD DATA
# ============================================================

if uploaded_file is not None:

    try:

        df = pd.read_csv(uploaded_file)

        st.success(
            f"Loaded {uploaded_file.name}"
        )

    except Exception as error:

        st.error("The uploaded CSV could not be read.")

        st.exception(error)

        st.stop()

else:

    try:

        df = pd.read_csv("sample_transactions.csv")

    except FileNotFoundError:

        st.error(
            "sample_transactions.csv was not found. "
            "Make sure it is in the same folder as app.py."
        )

        st.stop()


# ============================================================
# CLEAN COLUMN NAMES
# ============================================================

df.columns = (
    df.columns
    .astype(str)
    .str.strip()
    .str.lower()
    .str.replace(" ", "_")
)


# ============================================================
# VALIDATE COLUMNS
# ============================================================

required_columns = {
    "date",
    "description",
    "amount",
    "type"
}

missing_columns = required_columns - set(df.columns)

if missing_columns:

    st.error(
        "Missing required columns: "
        + ", ".join(sorted(missing_columns))
    )

    st.info(
        "Columns found: "
        + ", ".join(df.columns)
    )

    st.stop()


# ============================================================
# CLEAN DATA
# ============================================================

df["date"] = pd.to_datetime(
    df["date"],
    errors="coerce"
)

df["description"] = (
    df["description"]
    .astype(str)
    .str.strip()
)

df["amount"] = (
    df["amount"]
    .astype(str)
    .str.replace("₦", "", regex=False)
    .str.replace(",", "", regex=False)
    .str.strip()
)

df["amount"] = pd.to_numeric(
    df["amount"],
    errors="coerce"
)

df["type"] = (
    df["type"]
    .astype(str)
    .str.strip()
    .str.title()
)

df = df.dropna(
    subset=["date", "amount"]
).copy()


if df.empty:

    st.error(
        "No valid transactions were found. "
        "Check the date and amount columns in your CSV."
    )

    st.stop()


# ============================================================
# AUTOMATIC CATEGORIZATION
# ============================================================

df["category"] = df["description"].apply(
    categorize_transaction
)


# ============================================================
# FILTER
# ============================================================

with st.expander("Filters"):

    selected_categories = st.multiselect(
        "Transaction categories",
        options=sorted(df["category"].unique()),
        default=sorted(df["category"].unique())
    )


filtered_df = df[
    df["category"].isin(selected_categories)
].copy()


# ============================================================
# OVERVIEW
# ============================================================

st.header("Overview")

st.markdown(
    '<p class="section-description">'
    'A quick snapshot of your financial activity.'
    '</p>',
    unsafe_allow_html=True
)


income = filtered_df.loc[
    filtered_df["type"] == "Income",
    "amount"
].sum()


expenses = filtered_df.loc[
    filtered_df["type"] == "Expense",
    "amount"
].sum()


balance = income - expenses


savings_rate = (
    (balance / income) * 100
    if income > 0
    else 0
)


col1, col2, col3, col4 = st.columns(4)


with col1:

    st.markdown(
        '<div class="metric-box">'
        '<div class="metric-label">Total Income</div>'
        f'<div class="metric-number">₦{income:,.0f}</div>'
        '</div>',
        unsafe_allow_html=True
    )


with col2:

    st.markdown(
        '<div class="metric-box">'
        '<div class="metric-label">Total Expenses</div>'
        f'<div class="metric-number">₦{expenses:,.0f}</div>'
        '</div>',
        unsafe_allow_html=True
    )


with col3:

    balance_class = (
        "positive"
        if balance >= 0
        else "negative"
    )

    st.markdown(
        '<div class="metric-box">'
        '<div class="metric-label">Available Balance</div>'
        f'<div class="metric-number {balance_class}">'
        f'₦{balance:,.0f}'
        '</div>'
        '</div>',
        unsafe_allow_html=True
    )


with col4:

    savings_class = (
        "positive"
        if savings_rate >= 20
        else "negative"
    )

    st.markdown(
        '<div class="metric-box">'
        '<div class="metric-label">Savings Rate</div>'
        f'<div class="metric-number {savings_class}">'
        f'{savings_rate:.1f}%'
        '</div>'
        '</div>',
        unsafe_allow_html=True
    )


# ============================================================
# SPENDING ANALYSIS
# ============================================================

st.header("Spending Analysis")

st.markdown(
    '<p class="section-description">'
    'See which categories account for the largest share of your expenses.'
    '</p>',
    unsafe_allow_html=True
)


expense_df = filtered_df[
    filtered_df["type"] == "Expense"
].copy()


if not expense_df.empty:

    category_summary = (
        expense_df
        .groupby("category")["amount"]
        .sum()
        .sort_values(ascending=False)
        .reset_index()
    )

    col1, col2 = st.columns(2)


    with col1:

        st.subheader("Spending by Category")

        fig_pie = px.pie(
            category_summary,
            names="category",
            values="amount",
            hole=0.55
        )

        fig_pie.update_layout(
            template="plotly_white",
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            margin=dict(
                l=20,
                r=20,
                t=30,
                b=20
            ),
            legend_title=""
        )

        st.plotly_chart(
            fig_pie,
            use_container_width=True
        )


    with col2:

        st.subheader("Category Comparison")

        fig_bar = px.bar(
            category_summary,
            x="amount",
            y="category",
            orientation="h"
        )

        fig_bar.update_layout(
            template="plotly_white",
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            margin=dict(
                l=20,
                r=20,
                t=30,
                b=20
            ),
            xaxis_title="Amount",
            yaxis_title=""
        )

        st.plotly_chart(
            fig_bar,
            use_container_width=True
        )

else:

    st.info(
        "There are no expense transactions for the selected categories."
    )


# ============================================================
# FINANCIAL TRENDS
# ============================================================

st.header("Financial Trends")

st.markdown(
    '<p class="section-description">'
    'Compare income and expenses over time.'
    '</p>',
    unsafe_allow_html=True
)


trend_df = filtered_df.copy()

trend_df["month"] = (
    trend_df["date"]
    .dt.to_period("M")
    .astype(str)
)


monthly = (
    trend_df
    .groupby(["month", "type"])["amount"]
    .sum()
    .reset_index()
)


if not monthly.empty:

    fig_trend = px.line(
        monthly,
        x="month",
        y="amount",
        color="type",
        markers=True
    )

    fig_trend.update_layout(
        template="plotly_white",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        margin=dict(
            l=20,
            r=20,
            t=30,
            b=20
        ),
        xaxis_title="Month",
        yaxis_title="Amount",
        legend_title=""
    )

    st.plotly_chart(
        fig_trend,
        use_container_width=True
    )


# ============================================================
# INSIGHTS
# ============================================================

st.header("Financial Insights")

st.markdown(
    '<p class="section-description">'
    'Automatically generated observations based on your transaction data.'
    '</p>',
    unsafe_allow_html=True
)


insights = []


if savings_rate >= 20:

    insights.append(
        (
            "Healthy savings rate",
            f"You're currently saving about {savings_rate:.1f}% "
            "of your recorded income. That's a strong position to build on."
        )
    )

elif savings_rate > 0:

    insights.append(
        (
            "Room to improve savings",
            f"Your current savings rate is {savings_rate:.1f}%. "
            "Consider reviewing your largest recurring expenses."
        )
    )

else:

    insights.append(
        (
            "Spending exceeds income",
            "Your recorded expenses are currently equal to or greater "
            "than your income. Review your largest spending categories."
        )
    )


if not expense_df.empty:

    biggest_category = category_summary.iloc[0]["category"]

    biggest_amount = category_summary.iloc[0]["amount"]

    insights.append(
        (
            "Largest spending category",
            f"{biggest_category} accounts for "
            f"₦{biggest_amount:,.0f} of your recorded expenses."
        )
    )


if not expense_df.empty:

    largest_transaction = expense_df.loc[
        expense_df["amount"].idxmax()
    ]

    insights.append(
        (
            "Largest transaction",
            f"{largest_transaction['description']} was your "
            f"largest recorded expense at "
            f"₦{largest_transaction['amount']:,.0f}."
        )
    )


if income > 0:

    expense_ratio = (
        expenses / income
    ) * 100

    insights.append(
        (
            "Expense ratio",
            f"Your expenses represent approximately "
            f"{expense_ratio:.1f}% of your recorded income."
        )
    )


for title, description in insights:

    st.markdown(
        '<div class="insight-box">'
        f'<div class="insight-title">{title}</div>'
        f'<div class="insight-description">{description}</div>'
        '</div>',
        unsafe_allow_html=True
    )


# ============================================================
# TRANSACTIONS
# ============================================================

st.header("Transactions")

st.markdown(
    '<p class="section-description">'
    'Review your cleaned and automatically categorized transactions.'
    '</p>',
    unsafe_allow_html=True
)


display_df = filtered_df[
    [
        "date",
        "description",
        "amount",
        "type",
        "category"
    ]
].copy()


display_df["date"] = display_df[
    "date"
].dt.strftime("%Y-%m-%d")


display_df["amount"] = display_df[
    "amount"
].apply(
    lambda value: f"₦{value:,.0f}"
)


st.dataframe(
    display_df,
    use_container_width=True,
    hide_index=True
)


# ============================================================
# FOOTER
# ============================================================

st.markdown(
    '<div class="footer">'
    'FinSight · Personal Finance Analyzer'
    '<br>'
    'Built with Python · Pandas · Streamlit · Plotly'
    '</div>',
    unsafe_allow_html=True
)